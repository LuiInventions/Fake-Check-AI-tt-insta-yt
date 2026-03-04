import yt_dlp
import uuid
import asyncio
import logging

logger = logging.getLogger(__name__)

async def download_video(url: str, output_dir: str) -> dict:
    video_id = str(uuid.uuid4())
    output_path = f"{output_dir}/{video_id}.%(ext)s"
    
    ydl_opts = {
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]/bestvideo+bestaudio/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
        'retries': 3,
        'extract_flat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }
    
    import os
    # We explicitly do NOT load personal cookies anymore as per user request to avoid bans.
    cookie_str = None
    
    loop = asyncio.get_event_loop()
    def _download():
        try:
            target_url = url
            if "instagram.com" in target_url:
                try:
                    import requests
                    logger.info("Instagram URL detected, attempting Instagram Looter (RapidAPI) extraction")
                    
                    from config import get_settings
                    rapidapi_key = get_settings().RAPIDAPI_KEY
                    headers = {
                        "x-rapidapi-host": "instagram-looter2.p.rapidapi.com",
                        "x-rapidapi-key": rapidapi_key
                    }
                    rapidapi_url = "https://instagram-looter2.p.rapidapi.com/post-dl"
                    
                    res = requests.get(rapidapi_url, headers=headers, params={"url": target_url}, timeout=15)
                    
                    if res.status_code == 429:
                        raise Exception("RapidAPI Fehler 429: Too Many Requests für 'Instagram Looter'.")
                    elif res.status_code == 403:
                        raise Exception("RapidAPI Fehler 403: Abo für 'Instagram Looter' fehlt.")
                        
                    res.raise_for_status()
                    data = res.json()
                    
                    if data.get("status") and "data" in data and "medias" in data["data"]:
                        medias = data["data"]["medias"]
                        media_types = ("video", "image", "carousel")
                        video_urls = [m.get("link") or m.get("url") for m in medias if m.get("type") in media_types]
                        video_urls = [u for u in video_urls if u]
                        if video_urls:
                            target_url = video_urls[0]
                        else:
                            raise Exception("Instagram Looter API: Keine Media-URL im JSON gefunden.")
                    else:
                        raise Exception(f"RapidAPI JSON Unbekannt: {str(data)[:300]}")
                        
                    logger.info("Successfully extracted Instagram raw video URL via Instagram Looter")
                except Exception as ie:
                    if "RapidAPI Fehler" in str(ie) or "RapidAPI JSON" in str(ie):
                        raise ie  # Pass the explicit error up
                    logger.warning(f"RapidAPI failed, falling back to yt-dlp: {ie}")
                    
            if target_url.lower().split('?')[0].endswith(('.jpg', '.jpeg', '.png', '.webp')):
                import requests
                logger.info(f"Direct image URL detected, downloading with requests: {target_url}")
                res = requests.get(target_url, stream=True, timeout=15)
                res.raise_for_status()
                ext = target_url.lower().split('?')[0].split('.')[-1]
                if not ext: ext = "jpg"
                final_path = f"{output_dir}/{video_id}.{ext}"
                with open(final_path, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=8192):
                        f.write(chunk)
                return {
                    "filepath": final_path,
                    "title": "Instagram Image",
                    "duration": 0,
                    "platform": "instagram"
                }
                    
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(target_url, download=True)
                return {
                    "filepath": ydl.prepare_filename(info),
                    "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0),
                    "platform": info.get("extractor", "unknown"),
                }
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise e
    
    return await loop.run_in_executor(None, _download)
