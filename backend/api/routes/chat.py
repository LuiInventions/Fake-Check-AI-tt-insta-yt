from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.schemas import ChatRequest, ChatResponse
from models.database import get_db, Video, Message
from services.chat_service import chat_about_video
import logging
import re

router = APIRouter()
logger = logging.getLogger(__name__)

def validate_uuid(video_id: str) -> bool:
    """Validate UUID format to prevent SQL injection"""
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, video_id, re.IGNORECASE))

@router.post("/", response_model=ChatResponse)
async def post_chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Chat about an analyzed video"""
    logger.info(f"Chat request for video {request.video_id}: {request.message[:100]}")

    result = await db.execute(select(Video).where(Video.id == request.video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.status != "done":
        raise HTTPException(status_code=400, detail="Video analysis not complete yet")

    reply = await chat_about_video(request.video_id, request.message, db)
    return ChatResponse(reply=reply)

@router.get("/{video_id}/history")
async def get_chat_history(video_id: str, db: AsyncSession = Depends(get_db)):
    """Get chat history for a video"""
    # Validate UUID to prevent SQL injection
    if not validate_uuid(video_id):
        logger.warning(f"Invalid video ID format attempted in chat history: {video_id}")
        raise HTTPException(status_code=400, detail="Invalid video ID format")

    result = await db.execute(select(Message).where(Message.video_id == video_id).order_by(Message.created_at.asc()))
    messages = result.scalars().all()
    return {"history": [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in messages]}
