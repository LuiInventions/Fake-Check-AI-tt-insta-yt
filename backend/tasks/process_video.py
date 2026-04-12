import asyncio
import os
import logging
from celery_app import celery_app
from config import get_settings
from models.database import AsyncSessionLocal, Video
from services.downloader import download_video
from services.transcriber import transcribe_video
from services.frame_extractor import extract_frames
from services.analyzer import analyze_video
from services.ai_detector import check_ai_probability
from sqlalchemy.future import select

logger = logging.getLogger(__name__)
settings = get_settings()

async def process_video_async(video_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Video).where(Video.id == video_id))
        video = result.scalar_one_or_none()
        logger.info(f"Task started for video {video_id}")
        video.status = "processing"
        await db.commit()

        video_path = None
        ai_probability = 0.0
        try:
            logger.info(f"Downloading video from {video.url}")
            dl_info = await download_video(video.url, settings.UPLOAD_DIR)
            video_path = dl_info["filepath"]
            video.title, video.platform = dl_info["title"], dl_info["platform"]
            
            logger.info(f"Extracting audio, checking AI presence, and frames for video: {video.title}")
            transcript, frames, ai_prob = await asyncio.gather(
                transcribe_video(video_path), 
                extract_frames(video_path, settings.FRAMES_DIR, settings.FRAMES_PER_VIDEO),
                check_ai_probability(video_path)
            )
            video.transcript, video.frames_paths, ai_probability = transcript, frames, ai_prob
            
            analysis = await analyze_video(transcript, frames)
            video.analysis_result, video.status = analysis.model_dump(), "done"
            
        except Exception as e:
            video.status, video.error_message = "error", str(e)
            logger.error(f"Error processing video {video_id}: {e}")
        finally:
            await db.commit()
            if video_path and os.path.exists(video_path): os.remove(video_path)
            
            if video.telegram_chat_id and settings.TELEGRAM_BOT_TOKEN:
                await send_analysis_results(video, analysis.model_dump(), ai_probability)

async def send_analysis_results(video: Video, analysis_dict: dict, ai_probability: float = 0.0):
    import httpx
    try:
        if video.status == "done":
            verdict = analysis_dict.get("verdict", "")
            summary = analysis_dict.get("summary", "")
            
            verdict_emoji = "⚪" if verdict in ["music", "joke"] else "🔴" if verdict == "likely_fake" else "🟡" if verdict == "uncertain" else "🟢"
            verdict_text = "Irrelevant (Entertainment/Music)" if verdict in ["music", "joke"] else "Likely Fake" if verdict == "likely_fake" else "Uncertain" if verdict == "uncertain" else "Likely Real"
            
            message = f"{verdict_emoji} Analysis: {verdict_text} {verdict_emoji}\n\n"
            
            claims = analysis_dict.get("claims", [])
            true_claims = [c for c in claims if c.get("assessment") == "true"]
            false_claims = [c for c in claims if c.get("assessment") in ("false", "misleading")]
            
            if verdict not in ["joke", "music"]:
                if true_claims:
                    message += "✅ **True:**\n"
                    for c in true_claims:
                        message += f"• {c.get('claim', '')}\n"
                    message += "\n"
                    
                if false_claims:
                    message += "❌ **False/Misleading:**\n"
                    for c in false_claims:
                        message += f"• {c.get('claim', '')}\n"
                    message += "\n"
                    
                what_happened = analysis_dict.get("what_actually_happened")
                if what_happened and verdict != "likely_real":
                    message += f"📖 **Background:**\n{what_happened}\n\n"
                
            message += f"📌 **Verdict:**\n{summary}\n\n"
            
            sources = analysis_dict.get("sources", [])
            valid_sources = []
            for s in sources:
                if not s or "instagram.com" in s or "tiktok.com" in s or video.url in s:
                    continue
                if s not in valid_sources:
                    valid_sources.append(s)
                if len(valid_sources) >= 3:
                    break
                    
            if valid_sources:
                message += "🔗 **Sources for further reading:**\n"
                for src in valid_sources:
                    message += f"• {src}\n\n"
                    
            ai_percentage = int(ai_probability * 100)
            if ai_percentage >= 70:
                message += f"🚨 **Attention: This post is {ai_percentage}% AI generated!** 🚨\n\n"
                
            if verdict in ["joke", "music"]:
                message += "Any questions?\n\nDo you still want me to check this post properly?"
            else:
                message += "Any questions?"
            
            logger.info(f"Sending Telegram message:\n{message}")
            
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": video.telegram_chat_id, 
                        "text": message,
                        "link_preview_options": {"is_disabled": True}
                    }
                )
                if res.status_code != 200:
                    logger.warning(f"Telegram error: {res.text}.")
        else:
            message = f"❌ Analysis Error\n\nUnfortunately, there was a problem:\n{video.error_message}"
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": video.telegram_chat_id, 
                        "text": message,
                        "link_preview_options": {"is_disabled": True}
                    }
                )
    except Exception as ex:
        logger.error(f"Failed to send Telegram message: {ex}")

async def force_analyze_video_async(video_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Video).where(Video.id == video_id))
        video = result.scalar_one_or_none()
        if not video or not video.transcript:
            logger.error(f"Force analysis failed: Video {video_id} not found or has no transcript.")
            return

        logger.info(f"Forced exact fact check started for video {video_id}")
        video.status = "processing"
        await db.commit()

        try:
            # Force factual to skip circuit breaker
            analysis = await analyze_video(video.transcript, video.frames_paths or [], force_factual=True)
            video.analysis_result, video.status = analysis.model_dump(), "done"
        except Exception as e:
            video.status, video.error_message = "error", str(e)
            logger.error(f"Error forced processing video {video_id}: {e}")
        finally:
            await db.commit()
            if video.telegram_chat_id and settings.TELEGRAM_BOT_TOKEN:
                await send_analysis_results(video, video.analysis_result, 0.0) # We might not have AI prob saved, assume 0 for forces

@celery_app.task(name="tasks.process_video.process_video_task")
def process_video_task(video_id: str):
    asyncio.get_event_loop().run_until_complete(process_video_async(video_id))

@celery_app.task(name="tasks.process_video.force_analyze_video_task")
def force_analyze_video_task(video_id: str):
    asyncio.get_event_loop().run_until_complete(force_analyze_video_async(video_id))
