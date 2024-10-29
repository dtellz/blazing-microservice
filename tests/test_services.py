from datetime import date, datetime, time, timezone
from uuid import UUID

import pytest
from fastapi import HTTPException

from app.models.event import Event
from app.schemas.event import SearchResponse
from app.services.events_service import EventService


@pytest.mark.asyncio
async def test_ensure_utc_timezone():
    """Test _ensure_utc_timezone method."""
    service = EventService()

    # Test naive datetime gets UTC timezone
    naive_dt = datetime(2023, 1, 1, 12, 0)
    utc_dt = service._ensure_utc_timezone(naive_dt)
    assert utc_dt.tzinfo == timezone.utc

    # Test aware datetime remains unchanged
    aware_dt = datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc)
    result_dt = service._ensure_utc_timezone(aware_dt)
    assert result_dt == aware_dt


@pytest.mark.asyncio
async def test_validate_date_range():
    """Test _validate_date_range method."""
    service = EventService()

    # Valid date range should not raise exception
    valid_start = datetime(2023, 1, 1, tzinfo=timezone.utc)
    valid_end = datetime(2023, 1, 2, tzinfo=timezone.utc)
    service._validate_date_range(valid_start, valid_end)

    # Invalid date range should raise HTTPException
    invalid_start = datetime(2023, 1, 2, tzinfo=timezone.utc)
    invalid_end = datetime(2023, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(HTTPException) as exc:
        service._validate_date_range(invalid_start, invalid_end)
    assert exc.value.status_code == 400
    assert exc.value.detail == "starts_at must be before ends_at"


@pytest.mark.asyncio(scope="function")
async def test_search_events(async_session):
    """Test search_events method."""
    service = EventService()

    # Create test event
    test_event = Event(
        id=UUID("a7a9d2f8-e3d3-4b2a-b8c9-f1d4e6a7b8c9"),
        provider_unique_id="test_1234",
        provider_base_event_id="base_123",
        provider_event_id="event_123",
        title="Test Event",
        start_date=date(2023, 1, 15),
        start_time=time(12, 0),
        end_date=date(2023, 1, 15),
        end_time=time(14, 0),
        min_price=10.0,
        max_price=20.0,
    )

    async with async_session.begin():
        async_session.add(test_event)
        await async_session.commit()

    # Search within date range containing the event
    starts_at = datetime(2023, 1, 1, tzinfo=timezone.utc)
    ends_at = datetime(2023, 1, 31, tzinfo=timezone.utc)

    response = await service.search_events(async_session, starts_at, ends_at)

    assert isinstance(response, SearchResponse)
    assert response.data is not None
    assert len(response.data.events) == 1
    assert response.data.events[0].title == "Test Event"
    assert response.data.events[0].min_price == 10.0
    assert response.data.events[0].max_price == 20.0


@pytest.mark.asyncio(scope="function")
async def test_search_events_no_results(async_session):
    """Test search_events method with no matching results."""
    service = EventService()

    # Search with date range that shouldn't contain any events
    starts_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    ends_at = datetime(2024, 1, 31, tzinfo=timezone.utc)

    response = await service.search_events(async_session, starts_at, ends_at)

    assert isinstance(response, SearchResponse)
    assert response.data is not None
    assert len(response.data.events) == 0


@pytest.mark.asyncio(scope="function")
async def test_search_events_invalid_dates(async_session):
    """Test search_events method with invalid date range."""
    service = EventService()

    starts_at = datetime(2023, 12, 31, tzinfo=timezone.utc)
    ends_at = datetime(2023, 1, 1, tzinfo=timezone.utc)

    with pytest.raises(HTTPException) as exc:
        await service.search_events(async_session, starts_at, ends_at)

    assert exc.value.status_code == 400
    assert exc.value.detail == "starts_at must be before ends_at"
