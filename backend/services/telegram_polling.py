import asyncio
import httpx
import logging
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("telegram_polling")

settings = get_settings()

async def poll_telegram():
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set. Polling aborted.")
        return

    logger.info("Starting Telegram Polling...")
    offset = 0
    timeout = 30
    
    # Internal endpoint to forward updates to
    # When running in Docker, 'backend' is the service name
    backend_url = os.getenv("BACKEND_INTERNAL_URL", "http://backend:8000/api/telegram/webhook")

    async with httpx.AsyncClient() as bot_client:
        async with httpx.AsyncClient() as backend_client:
            while True:
                try:
                    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"
                    params = {"offset": offset, "timeout": timeout}
                    
                    response = await bot_client.get(url, params=params, timeout=timeout + 5)
                    if response.status_code != 200:
                        logger.error(f"Telegram API error: {response.text}")
                        await asyncio.sleep(5)
                        continue
                        
                    data = response.json()
                    if not data.get("ok"):
                        logger.error(f"Telegram API not ok: {data}")
                        await asyncio.sleep(5)
                        continue
                        
                    updates = data.get("result", [])
                    for update in updates:
                        logger.info(f"Received update {update.get('update_id')}")
                        offset = update.get("update_id") + 1
                        
                        # Forward to backend webhook
                        try:
                            # We send the update as the body, just like Telegram webhooks do
                            webhook_res = await backend_client.post(backend_url, json=update)
                            if webhook_res.status_code != 200:
                                logger.error(f"Backend webhook error: {webhook_res.text}")
                        except Exception as e:
                            logger.error(f"Failed to forward update to backend: {e}")
                            
                except httpx.ReadTimeout:
                    continue
                except Exception as e:
                    logger.error(f"Polling error: {e}")
                    await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(poll_telegram())
    except KeyboardInterrupt:
        logger.info("Polling stopped by user.")
