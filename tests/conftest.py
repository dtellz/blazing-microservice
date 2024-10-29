"""Fixtures for testing."""

import asyncio
from typing import Generator

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.db.session import Base
from app.dependencies import get_db
from app.main import app
from app.services.events_service import EventService

# Use the same database URL from settings but with test database
TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@localhost:5433/postgres_test"
)

# Create an asynchronous engine for testing
engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
)


@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def prepare_database():
    """Create the test database tables."""
    async with engine_test.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        await conn.commit()

    yield

    async with engine_test.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.commit()


@pytest_asyncio.fixture(scope="function")
async def async_session():
    """Create a new database session for a test."""
    async with AsyncSession(
        engine_test, expire_on_commit=True, autoflush=True
    ) as session:
        try:
            yield session
            if session.in_transaction():
                await session.rollback()
        except Exception:
            await session.rollback()
            raise
        finally:
            if session.in_transaction():
                await session.rollback()
            await session.close()


@pytest_asyncio.fixture
def anyio_backend():
    """Specify the backend for pytest-asyncio."""
    return "asyncio"


@pytest_asyncio.fixture
async def client(async_session, event_service):
    """Create a test client with a test database session."""

    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[EventService] = lambda: event_service

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
def event_service():
    """Provide an instance of EventService."""
    return EventService()
