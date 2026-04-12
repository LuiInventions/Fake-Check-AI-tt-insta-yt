from slowapi import Limiter
from fastapi import Request
import json

def get_client_ip(request: Request) -> str:
    """Get client IP from X-Forwarded-For or request.client.host"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host

def get_email_from_request(request: Request) -> str:
    """
    Get email from request body for account-based rate limiting
    Falls back to IP-based limiting if email not available
    """
    try:
        # Check if request has body
        if hasattr(request, "_body"):
            body = request._body
            if body:
                data = json.loads(body)
                email = data.get("email")
                if email:
                    return f"email:{email}"
    except:
        pass

    # Fallback to IP-based limiting
    return f"ip:{get_client_ip(request)}"

# Default limiter uses IP
limiter = Limiter(key_func=get_client_ip)

# Account-based limiter uses email from request body
account_limiter = Limiter(key_func=get_email_from_request)
