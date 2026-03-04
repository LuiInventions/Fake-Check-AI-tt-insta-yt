import logging
import asyncio
import os
import requests
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

async def check_ai_probability(video_path: str) -> float:
    """
    Submits the video to Sightengine genai model synchronously.
    Returns the maximum ai_generated probability (0.0 to 1.0) found in frames,
    or 0.0 on failure.
    """
    if not os.path.exists(video_path):
        return 0.0
    
    api_user = settings.SIGHTENGINE_API_USER
    api_secret = settings.SIGHTENGINE_API_SECRET
    
    if not api_user or not api_secret:
        logger.warning("Sightengine API credentials not set.")
        return 0.0
        
    url = "https://api.sightengine.com/1.0/video/check-sync.json"
    
    loop = asyncio.get_event_loop()
    
    def _upload():
        try:
            with open(video_path, 'rb') as f:
                files = {'media': f}
                data = {
                    'models': 'genai',
                    'api_user': api_user,
                    'api_secret': api_secret
                }
                res = requests.post(url, files=files, data=data, timeout=120)
                res.raise_for_status()
                return res.json()
        except Exception as e:
            logger.error(f"Sightengine HTTP Request failed: {e}")
            return None
            
    data = await loop.run_in_executor(None, _upload)
    
    if data:
        if data.get("status") == "success" and "data" in data and "frames" in data["data"]:
            frames = data["data"]["frames"]
            max_ai = 0.0
            for frame in frames:
                ai_score = frame.get("type", {}).get("ai_generated", 0.0)
                if ai_score > max_ai:
                    max_ai = ai_score
            logger.info(f"Sightengine AI Detection completed. Highest Score: {max_ai}")
            return max_ai
        else:
            logger.warning(f"Sightengine unexpected response: {data}")
            return 0.0
    
    return 0.0
