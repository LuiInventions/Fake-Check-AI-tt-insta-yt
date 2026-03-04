from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.schemas import VideoAnalyzeRequest, VideoResponse
from models.database import get_db, Video
from tasks.process_video import process_video_task
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=VideoResponse)
async def analyze_video(request: VideoAnalyzeRequest, db: AsyncSession = Depends(get_db)):
    db_video = Video(url=request.url, status="pending")
    db.add(db_video)
    await db.commit()
    await db.refresh(db_video)
    process_video_task.delay(db_video.id)
    return db_video

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Video).where(Video.id == video_id))
    db_video = result.scalar_one_or_none()
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video

@router.get("/{video_id}/frames")
async def get_video_frames(video_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Video).where(Video.id == video_id))
    db_video = result.scalar_one_or_none()
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"frames": db_video.frames_paths or []}
