"""Database session."""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Forcing asyncpg driver by ensuring +asyncpg is in the URL
database_url = str(settings.DATABASE_URL)

engine = create_async_engine(database_url)

async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
