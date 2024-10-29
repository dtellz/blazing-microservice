from datetime import datetime, timezone
from uuid import UUID

import pytest

from app.schemas.event import EventList, EventSummary, SearchResponse


@pytest.mark.asyncio
async def test_search_events_success(client, event_service):
    """Test successful event search."""
    # Mock data
    event_summary = EventSummary(
        id=UUID("a7a9d2f8-e3d3-4b2a-b8c9-f1d4e6a7b8c9"),
        title="Test Event",
        start_date=datetime.now(timezone.utc).date(),
        start_time=datetime.now(timezone.utc).time(),
        end_date=datetime.now(timezone.utc).date(),
        end_time=datetime.now(timezone.utc).time(),
        min_price=10.0,
        max_price=20.0,
    )
    mock_response = SearchResponse(data=EventList(events=[event_summary]))

    async def mock_search(*args):
        return mock_response

    event_service.search_events = mock_search

    starts_at = "2023-01-01T00:00:00Z"
    ends_at = "2023-12-31T23:59:59Z"

    response = await client.get(
        f"/search?starts_at={starts_at}&ends_at={ends_at}"
    )  # noqa: E501

    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert "events" in data["data"]
    assert len(data["data"]["events"]) == 1
    assert data["data"]["events"][0]["title"] == "Test Event"


@pytest.mark.asyncio
async def test_search_events_invalid_dates(client):
    """Test search with invalid date range."""
    # Test with ends_at before starts_at
    starts_at = "2023-12-31T00:00:00Z"
    ends_at = "2023-01-01T00:00:00Z"

    response = await client.get(
        f"/search?starts_at={starts_at}&ends_at={ends_at}"
    )  # noqa: E501

    assert response.status_code == 500

    data = response.json()

    assert "data" in data
    assert "error" in data


@pytest.mark.asyncio
async def test_search_events_missing_parameters(client):
    """Test search with missing required parameters."""
    response = await client.get("/search")

    assert response.status_code == 400

    data = response.json()

    assert "data" in data
    assert "error" in data


@pytest.mark.asyncio
async def test_search_events_invalid_date_format(client):
    """Test search with invalid date format."""
    starts_at = "invalid-date"
    ends_at = "2023-12-31T23:59:59Z"

    response = await client.get(
        f"/search?starts_at={starts_at}&ends_at={ends_at}"
    )  # noqa: E501

    assert response.status_code == 400

    data = response.json()

    assert "data" in data
    assert "error" in data
