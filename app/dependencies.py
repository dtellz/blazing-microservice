"""Dependency injectors for the application."""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import engine
from app.services.events_service import EventService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]
EventServiceDep = Annotated[EventService, Depends(EventService)]
