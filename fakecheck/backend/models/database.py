from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.types import JSON
from typing import Optional, List
import uuid
import datetime
from config import get_settings

settings = get_settings()
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    url: Mapped[str]
    platform: Mapped[Optional[str]]
    title: Mapped[Optional[str]]
    transcript: Mapped[Optional[str]]
    analysis_result: Mapped[Optional[dict]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(default="pending")
    error_message: Mapped[Optional[str]]
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
    frames_paths: Mapped[Optional[list]] = mapped_column(JSON)
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(default=None)

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    video_id: Mapped[str]
    role: Mapped[str]
    content: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
