import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from api.limiter import limiter
from config import get_settings
from models.database import engine, Base
from api.routes import video, chat, health, telegram, protected

settings = get_settings()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# NOTE: Token revocation is now handled via Redis in protected.py
# This global set is deprecated but kept for backwards compatibility
revoked_tokens: set = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FakeCheck FastAPI...")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.FRAMES_DIR, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("Shutting down FakeCheck FastAPI...")

app = FastAPI(
    title=settings.APP_NAME, 
    lifespan=lifespan,
    docs_url=None,     # Disable Swagger UI
    redoc_url=None,    # Disable ReDoc
    openapi_url=None   # Disable openapi.json
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global custom exception handler to mask stack traces in production
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/health", tags=["Health"])
app.include_router(video.router, prefix="/api/video", tags=["Video"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(telegram.router, prefix="/api/telegram", tags=["Telegram"])
app.include_router(protected.router, prefix="/api", tags=["Protected Downloads"])
