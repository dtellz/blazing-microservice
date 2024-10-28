"""Database session."""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.config import settings

engine = create_async_engine(str(settings.DATABASE_URL))

async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


# Utility function to create tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
