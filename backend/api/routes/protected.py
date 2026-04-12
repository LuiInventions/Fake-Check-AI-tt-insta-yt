from fastapi import APIRouter, HTTPException, Depends, Request, Response, Header
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from config import get_settings, Settings
from datetime import datetime, timedelta, timezone
import os
import urllib.request
import urllib.parse
import json
import secrets
import jwt
import time
import bcrypt
import logging
from typing import Optional
from api.limiter import limiter

router = APIRouter()
logger = logging.getLogger(__name__)

def get_user_by_email(email: str, settings: Settings):
    """Get user credentials from settings (supports single admin for now)"""
    if email == settings.ADMIN_EMAIL:
        return {
            "email": settings.ADMIN_EMAIL,
            "password_hash": settings.ADMIN_PASSWORD, # Can be hash or plain for simplicity in local mode, but we'll stick to hash if provided
            "role": "admin"
        }
    return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_redis_client(settings: Settings):
    """Get Redis client for token revocation and 2FA storage"""
    import redis
    try:
        redis_url = settings.redis_url_with_auth
        return redis.from_url(redis_url, decode_responses=True)
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/verify-password")
@limiter.limit("5/15minute")
async def verify_password_endpoint(
    request: Request,
    req: LoginRequest,
    settings: Settings = Depends(get_settings)
):
    """
    Step 1: Verify email and password
    Rate limited to 5 attempts per 15 minutes per IP
    """
    # Audit log
    logger.info(f"Login attempt for {req.email} from {request.client.host}")

    # Get user from settings
    user = get_user_by_email(req.email, settings)

    if not user:
        # Standardized error to prevent user enumeration
        logger.warning(f"Login failed: User {req.email} not found from {request.client.host}")
        return JSONResponse(status_code=401, content={"detail": "Ungültige Anmeldedaten"})

    # Verify password (checks both bcrypt hash and plain text for ease of setup)
    is_valid = False
    try:
        if user['password_hash'].startswith('$2b$'):
            is_valid = verify_password(req.password, user['password_hash'])
        else:
            is_valid = (req.password == user['password_hash'])
    except Exception:
        is_valid = (req.password == user['password_hash'])

    if not is_valid:
        logger.warning(f"Login failed: Invalid password for {req.email} from {request.client.host}")
        return JSONResponse(status_code=401, content={"detail": "Ungültige Anmeldedaten"})

    # Generate cryptographically secure 8-digit 2FA code (stronger than 6-digit)
    code = "".join(str(secrets.randbelow(10)) for _ in range(8))

    # Store 2FA code in Redis with 5-minute expiration
    redis_client = get_redis_client(settings)
    if redis_client:
        try:
            redis_key = f"2fa:{req.email}"
            redis_client.setex(
                redis_key,
                300,  # 5 minutes TTL
                json.dumps({
                    "code": code,
                    "expires_at": time.time() + 300,
                    "used": False,
                    "ip": request.client.host
                })
            )
        except Exception as e:
            logger.error(f"Redis 2FA storage failed: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    else:
        logger.error("Redis not available for 2FA storage")
        raise HTTPException(status_code=500, detail="Service temporarily unavailable")

    # Send 2FA code via Mailtrap
    url = "https://send.api.mailtrap.io/api/send"
    headers = {
        "Authorization": f"Bearer {settings.MAILTRAP_API_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "FakeCheck-Auth/1.0"
    }
    data = {
        "from": {"email": "security@fakecheck.local", "name": "FakeCheck Security"},
        "to": [{"email": req.email}],
        "subject": "Your 2FA Security Code",
        "text": f"Your 2FA security code is: {code}\n\nThis code will expire in 5 minutes.\n\nIf you did not request this code, please ignore this email.",
        "html": f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #3b82f6;">Two-Factor Authentication</h2>
            <p>Your security code is:</p>
            <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                <h1 style="margin: 0; color: #1f2937; letter-spacing: 8px; font-size: 32px;">{code}</h1>
            </div>
            <p style="color: #6b7280; font-size: 14px;">This code will expire in 5 minutes.</p>
            <p style="color: #6b7280; font-size: 14px;">If you did not request this code, please ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #9ca3af; font-size: 12px;">Lui Inventions - Secure Access</p>
        </body>
        </html>
        """
    }

    req_obj = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    try:
        with urllib.request.urlopen(req_obj) as response:
            logger.info(f"2FA code sent successfully to {req.email}")
    except Exception as e:
        logger.error(f"Mailtrap error for {req.email}: {e}")
        return JSONResponse(status_code=500, content={"detail": "Failed to send 2FA email"})

    return JSONResponse(content={"status": "pending_2fa"}, status_code=200)

class TwoFARequest(BaseModel):
    email: EmailStr
    code: str

@router.post("/verify-2fa")
@limiter.limit("5/15minute")
async def verify_2fa(
    request: Request,
    req: TwoFARequest,
    response: Response,
    settings: Settings = Depends(get_settings)
):
    """
    Step 2: Verify 2FA code and issue JWT token
    Rate limited to 5 attempts per 15 minutes per IP
    """
    if not settings.SECRET_KEY:
        logger.critical("SECRET_KEY not set in environment")
        raise RuntimeError("SECRET_KEY ist nicht gesetzt. Bitte in .env definieren.")

    jwt_secret = settings.SECRET_KEY

    # Get 2FA data from Redis
    redis_client = get_redis_client(settings)
    if not redis_client:
        logger.error("Redis not available for 2FA verification")
        raise HTTPException(status_code=500, detail="Service temporarily unavailable")

    try:
        redis_key = f"2fa:{req.email}"
        entry_json = redis_client.get(redis_key)

        if not entry_json:
            logger.warning(f"2FA failed: No pending code for {req.email} from {request.client.host}")
            return JSONResponse(status_code=401, content={"detail": "Ungültige Anmeldedaten"})

        entry = json.loads(entry_json)

        if entry["used"]:
            logger.warning(f"2FA failed: Code already used for {req.email} from {request.client.host}")
            return JSONResponse(status_code=401, content={"detail": "OTP bereits verwendet"})

        if time.time() > entry["expires_at"]:
            redis_client.delete(redis_key)
            logger.warning(f"2FA failed: Code expired for {req.email} from {request.client.host}")
            return JSONResponse(status_code=401, content={"detail": "OTP abgelaufen"})

        if entry["code"] != req.code:
            logger.warning(f"2FA failed: Invalid code for {req.email} from {request.client.host}. Expected: {entry['code']}, Got: {req.code}")
            return JSONResponse(status_code=401, content={"detail": "Ungültiger 2FA-Code"})

        # Mark code as used
        entry["used"] = True
        redis_client.setex(redis_key, 300, json.dumps(entry))

        # Generate JWT token
        user = get_user_by_email(req.email, settings)
        payload = {
            "sub": req.email,
            "role": user.get("role", "user"),
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)  # 24 hour expiration
        }
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")

        logger.info(f"2FA successful: Token issued for {req.email} from {request.client.host}")

        # Set secure cookie
        response.set_cookie(
            key="fakecheck_session",
            value=token,
            path="/",
            httponly=True,  # Prevent XSS
            secure=False,    # Allow HTTP for local use
            samesite="lax", # CSRF protection
            max_age=86400   # 24 hours
        )

        return {"status": "success", "token": token}

    except json.JSONDecodeError as e:
        logger.error(f"2FA error: Invalid Redis data for {req.email}: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

class TokenRequest(BaseModel):
    token: str

@router.post("/verify-token")
async def verify_token(
    request: Request,
    req: TokenRequest,
    settings: Settings = Depends(get_settings)
):
    """
    Verify JWT token validity
    Checks against Redis-based revocation list
    """
    if not settings.SECRET_KEY:
        raise RuntimeError("SECRET_KEY ist nicht gesetzt. Bitte in .env definieren.")

    jwt_secret = settings.SECRET_KEY

    # Check Redis-based revocation list
    redis_client = get_redis_client(settings)
    if redis_client:
        try:
            if redis_client.sismember("revoked_tokens", req.token):
                logger.warning(f"Token verification failed: Token revoked from {request.client.host}")
                return JSONResponse(status_code=401, content={"detail": "Sitzung wurde beendet"})
        except Exception as e:
            logger.error(f"Redis revocation check failed: {e}")

    try:
        payload = jwt.decode(req.token, jwt_secret, algorithms=["HS256"])
        return JSONResponse(content={"status": "success", "email": payload.get("sub")}, status_code=200)
    except jwt.ExpiredSignatureError:
        logger.warning(f"Token verification failed: Token expired from {request.client.host}")
        return JSONResponse(status_code=401, content={"detail": "Token abgelaufen"})
    except Exception as e:
        logger.warning(f"Token verification failed: Invalid token from {request.client.host}")
        return JSONResponse(status_code=401, content={"detail": "Ungültige Anmeldedaten"})

@router.get("/auth-check")
async def auth_check(request: Request, settings: Settings = Depends(get_settings)):
    """
    Caddy forward_auth endpoint
    Validates session cookie or Authorization header
    """
    if not settings.SECRET_KEY:
        raise RuntimeError("SECRET_KEY ist nicht gesetzt. Bitte in .env definieren.")

    jwt_secret = settings.SECRET_KEY

    # Try cookie first
    token = request.cookies.get("fakecheck_session")

    # Fall back to Authorization header
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if token:
        # Check Redis-based revocation list
        redis_client = get_redis_client(settings)
        if redis_client:
            try:
                if redis_client.sismember("revoked_tokens", token):
                    logger.warning(f"Auth check failed: Token revoked from {request.client.host}")
                    return Response(status_code=401)
            except Exception as e:
                logger.error(f"Redis revocation check failed: {e}")

        try:
            jwt.decode(token, jwt_secret, algorithms=["HS256"])
            return Response(status_code=200)
        except Exception as e:
            logger.warning(f"Auth check failed: {e} from {request.client.host}")

    # Return 401 to trigger Caddy's error handling (redirect to login)
    return Response(status_code=401)

@router.post("/logout")
async def logout(request: Request, response: Response, settings: Settings = Depends(get_settings)):
    """
    Logout endpoint
    Adds token to Redis-based revocation list
    """
    # Get token from cookie or header
    token = request.cookies.get("fakecheck_session")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if token:
        # Add to Redis-based revocation list with TTL matching token expiration
        redis_client = get_redis_client(settings)
        if redis_client:
            try:
                # Decode token to get expiration time
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
                exp_timestamp = payload.get("exp")

                if exp_timestamp:
                    ttl = int(exp_timestamp - time.time())
                    if ttl > 0:
                        redis_client.sadd("revoked_tokens", token)
                        redis_client.expire(token, ttl)
                        logger.info(f"Token revoked successfully from {request.client.host}")
            except Exception as e:
                logger.error(f"Token revocation failed: {e}")

    # Delete cookie
    response.delete_cookie(
        key="fakecheck_session",
        path="/"
    )

    logger.info(f"Logout successful from {request.client.host}")
    return {"status": "success"}

@router.get("/protected-download/{filename}")
async def protected_download(
    filename: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    settings: Settings = Depends(get_settings)
):
    """
    Protected file download endpoint
    Requires valid JWT token in Authorization header (NOT URL parameter!)
    """
    if not settings.SECRET_KEY:
        raise RuntimeError("SECRET_KEY ist nicht gesetzt. Bitte in .env definieren.")

    jwt_secret = settings.SECRET_KEY

    # Get token from Authorization header (preferred) or fallback to cookie
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    else:
        token = request.cookies.get("fakecheck_session")

    if not token:
        logger.warning(f"Download failed: No token provided for {filename} from {request.client.host}")
        raise HTTPException(status_code=401, detail="Authentication required")

    # Verify token
    try:
        jwt.decode(token, jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        logger.warning(f"Download failed: Token expired for {filename} from {request.client.host}")
        raise HTTPException(status_code=401, detail="Token abgelaufen")
    except Exception:
        logger.warning(f"Download failed: Invalid token for {filename} from {request.client.host}")
        raise HTTPException(status_code=401, detail="Invalid session token")

    # Validate filename (prevent path traversal)
    if ".." in filename or "/" in filename or "\\" in filename:
        logger.warning(f"Download failed: Invalid filename {filename} from {request.client.host}")
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Whitelist allowed files
    allowed_files = [
        "fakecheck-ios-source.tar.gz",
        "fakecheck-frontend-ready.zip",
        "antigravity_template.zip"
    ]

    if filename not in allowed_files:
        logger.warning(f"Download failed: File {filename} not in whitelist from {request.client.host}")
        raise HTTPException(status_code=404, detail="File not found")

    protected_dir = "/app/data/protected_downloads"
    file_path = os.path.join(protected_dir, filename)

    if not os.path.exists(file_path):
        logger.error(f"Download failed: File {filename} does not exist")
        raise HTTPException(status_code=404, detail="File not found")

    logger.info(f"Download successful: {filename} by user from {request.client.host}")

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=filename
    )
