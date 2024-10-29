"""Dependency injectors for the application."""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.services.events_service import EventService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]
EventServiceDep = Annotated[EventService, Depends(EventService)]
