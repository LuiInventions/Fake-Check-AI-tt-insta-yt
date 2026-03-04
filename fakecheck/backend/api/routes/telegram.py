from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.database import get_db, Video, AsyncSessionLocal
from tasks.process_video import process_video_task
from services.chat_service import chat_about_video
from config import get_settings
import httpx
import re
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

@router.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    logger.info(f"Telegram Webhook received: {data}")
    
    if "message" not in data or "text" not in data["message"]:
        return {"status": "ignored"}
        
    chat_id = str(data["message"]["chat"]["id"])
    text = data["message"]["text"]
    
    # Extract URL from text
    url_match = re.search(r'(https?://[^\s]+)', text)
    if not url_match:
        # It's a follow-up chat message
        latest_video_query = await db.execute(
            select(Video).where(Video.telegram_chat_id == chat_id).order_by(Video.created_at.desc())
        )
        latest_video = latest_video_query.scalars().first()
        
        if not latest_video or latest_video.status != "done":
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": "Bitte sende mir zuerst den Link zu einem TikTok, Insta oder YouTube Video, das ich prüfen soll."
                    }
                )
            return {"status": "no context"}
            
        background_tasks.add_task(handle_chat_task, latest_video.id, text, chat_id)
        return {"status": "ok"}
        
    url = url_match.group(1)
    
    # Create video entry
    db_video = Video(url=url, status="pending", telegram_chat_id=chat_id)
    db.add(db_video)
    await db.commit()
    await db.refresh(db_video)
    
    # Trigger cellery
    process_video_task.delay(db_video.id)
    
    # Send processing message
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": "Video wird geprüft... ⏳"
            }
        )
        
    return {"status": "ok"}

async def handle_chat_task(video_id: str, text: str, chat_id: str):
    async with AsyncSessionLocal() as session:
        try:
            # Check if this is a response to forced analysis prompt
            video_res = await session.execute(select(Video).where(Video.id == video_id))
            video = video_res.scalar_one_or_none()
            
            if video and video.analysis_result:
                verdict = video.analysis_result.get("verdict", "")
                if verdict in ["joke", "music"]:
                    # Check for affirmative intent
                    clean_text = text.lower().strip()
                    affirmative_words = ["ja", "bitte", "doch", "trotzdem", "prüfen", "checken", "mach das", "gerne", "yes"]
                    
                    if any(word in clean_text for word in affirmative_words):
                        # Force analysis!
                        async with httpx.AsyncClient() as client:
                            await client.post(
                                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                                json={
                                    "chat_id": chat_id,
                                    "text": "Video wird geprüft... ⏳"
                                }
                            )
                        
                        from tasks.process_video import force_analyze_video_task
                        force_analyze_video_task.delay(video_id)
                        return

            # Normal chat handling
            reply_text = await chat_about_video(video_id, text, session)
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": reply_text
                    }
                )
        except Exception as e:
            logger.error(f"Error in chat task: {e}")
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": "Entschuldigung, es gab ein Problem bei der Verarbeitung deiner Frage."
                    }
                )
