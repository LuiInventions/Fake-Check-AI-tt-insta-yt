from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from openai import AsyncOpenAI
import json
from models.database import Video, Message
from config import get_settings

settings = get_settings()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def chat_about_video(video_id: str, user_message: str, db: AsyncSession) -> str:
    db_msg_user = Message(video_id=video_id, role="user", content=user_message)
    db.add(db_msg_user)
    await db.commit()

    video_res = await db.execute(select(Video).where(Video.id == video_id))
    video = video_res.scalar_one()
    context = f"TRANSKRIPT:\n{video.transcript}\n\nANALYSE-ERGEBNIS:\n{json.dumps(video.analysis_result)}"

    msg_res = await db.execute(select(Message).where(Message.video_id == video_id).order_by(Message.created_at.asc()))
    history = msg_res.scalars().all()

    messages = [{"role": "system", "content": f"Du bist ein Faktencheck-Assistent. Hier ist der Kontext zum Video:\n\n{context}"}]
    messages.extend([{"role": msg.role, "content": msg.content} for msg in history])
        
    if settings.MOCK_MODE:
        reply_text = "MOCK REPLY: Based on the analysis, this video exhibits multiple red flags associated with misinformation."
    else:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            max_tokens=1000
        )
        reply_text = response.choices[0].message.content
    
    db_msg_assistant = Message(video_id=video_id, role="assistant", content=reply_text)
    db.add(db_msg_assistant)
    await db.commit()
    
    return reply_text
