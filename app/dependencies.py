"""Dependency injectors for the application."""

from typing import Annotated, Generator

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import engine
from app.services.events_service import EventService


def get_db() -> Generator[AsyncSession, None, None]:
    with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]
EventServiceDep = Annotated[EventService, Depends(EventService)]
