import asyncio
import os
import uuid
import logging
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

async def extract_frames(filepath: str, output_dir: str, num_frames: int = 8) -> list[str]:
    if filepath.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
        return [filepath]
        
    try:
        probe_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", filepath
        ]
        probe_proc = await asyncio.create_subprocess_exec(*probe_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await probe_proc.communicate()
        
        duration = float(stdout.decode().strip())
        if duration <= 0: return []
            
        fps = num_frames / duration
        session_id = str(uuid.uuid4())
        output_pattern = os.path.join(output_dir, f"{session_id}_frame_%04d.jpg")
        
        extract_cmd = [
            "ffmpeg", "-i", filepath,
            "-vf", f"fps={fps}",
            "-q:v", str(int(100 - settings.FRAME_QUALITY) // 5 + 2),
            output_pattern, "-y"
        ]
        
        ex_proc = await asyncio.create_subprocess_exec(*extract_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await ex_proc.communicate()
        
        frames = []
        for file in sorted(os.listdir(output_dir)):
            if file.startswith(session_id) and file.endswith(".jpg"):
                frames.append(os.path.join(output_dir, file))
                if len(frames) == num_frames: break
        return frames
    except Exception as e:
        logger.error(f"Frame extraction failed: {e}")
        raise
