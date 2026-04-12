from fastapi import APIRouter
import redis.asyncio as redis
from config import get_settings

router = APIRouter()
settings = get_settings()

@router.get("/")
async def health_check():
    redis_status = False
    try:
        r = redis.from_url(settings.redis_url_with_auth)
        await r.ping()
        await r.close()
        redis_status = True
    except Exception:
        redis_status = False
    return {"status": "ok", "redis": redis_status}
