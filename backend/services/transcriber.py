import asyncio
import os
import logging
from openai import AsyncOpenAI
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def transcribe_video(filepath: str) -> str:
    if filepath.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
        return ""
        
    if settings.MOCK_MODE:
        logger.info(f"[MOCK_MODE] Skipping transcription for {filepath}")
        return "MOCK TRANSCRIPT: This video claims that the earth is flat and we never went to the moon."
        
    audio_path = f"{filepath}.wav"
    try:
        cmd = [
            "ffmpeg", "-i", filepath,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            audio_path, "-y"
        ]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            logger.warning(f"FFmpeg audio extraction failed (likely no audio track): {stderr.decode()}")
            return ""
            
        with open(audio_path, "rb") as audio_file:
            response = await client.audio.transcriptions.create(
                model=settings.WHISPER_MODEL,
                file=audio_file
            )
        return response.text
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
