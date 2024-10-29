import asyncio
from unittest.mock import patch

import pytest
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
    echo=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
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


@pytest_asyncio.fixture
async def async_session(prepare_database):
    """Create a new database session for a test."""
    async with AsyncSession(
        engine_test, expire_on_commit=False, autoflush=False, autocommit=False
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
async def client(prepare_database, async_session, event_service):
    """Create a test client with a test database session."""

    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[EventService] = lambda: event_service

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
def mock_httpx_get():
    """Mock httpx.AsyncClient.get method."""
    with patch("httpx.AsyncClient.get") as mock_get:
        yield mock_get


@pytest_asyncio.fixture
def mock_celery_task():
    """Mock Celery task."""
    with patch("app.tasks.fetch_events.fetch_events_task.delay") as mock_task:
        yield mock_task


@pytest_asyncio.fixture
def event_service():
    """Provide an instance of EventService."""
    return EventService()
