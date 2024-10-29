"""Unit tests for the fetch events task."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.tasks.fetch_events import _fetch_events, parse_xml, upsert_events


@pytest.mark.asyncio
async def test_parse_xml():
    """Test parse_xml function."""
    xml_content = b"""
    <root>
        <base_event base_event_id="1" title="Test Event" sell_mode="online">
            <event event_id="001" event_start_date="2024-10-28T12:00:00" event_end_date="2024-10-28T14:00:00">
                <zone price="20.0" />
                <zone price="50.0" />
            </event>
        </base_event>
    </root>
    """  # noqa: E501
    events = parse_xml(xml_content)
    assert len(events) == 1
    event = events[0]
    assert event["provider_unique_id"] == "1_001"
    assert event["min_price"] == 20.0
    assert event["max_price"] == 50.0
    assert event["title"] == "Test Event"


@pytest.mark.asyncio(scope="function")
async def test_upsert_events(async_session: AsyncSession):
    """Test upsert_events function."""
    sample_events = [
        {
            "provider_unique_id": "1_101",
            "provider_base_event_id": "1",
            "provider_event_id": "101",
            "title": "Test Event",
            "start_date": "2024-10-28",
            "start_time": "12:00:00",
            "end_date": "2024-10-28",
            "end_time": "14:00:00",
            "min_price": 20.0,
            "max_price": 50.0,
        }
    ]

    with patch.object(
        async_session, "execute", new_callable=AsyncMock
    ) as mock_execute:  # noqa: E501
        with patch.object(
            async_session, "commit", new_callable=AsyncMock
        ) as mock_commit:
            await upsert_events(sample_events, async_session)

            mock_execute.assert_called_once()
            mock_commit.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_events_success():
    """Test fetch_events_task function."""
    # Mock response data
    mock_xml = b"""
    <root>
        <base_event base_event_id="1" title="Test Event" sell_mode="online">
            <event event_id="001" event_start_date="2024-10-28T12:00:00" event_end_date="2024-10-28T14:00:00">
                <zone price="20.0" />
            </event>
        </base_event>
    </root>
    """  # noqa: E501

    mock_response = MagicMock()
    mock_response.content = mock_xml
    mock_response.raise_for_status = MagicMock()

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session_maker = MagicMock(spec=async_sessionmaker)
    mock_session_maker.return_value.__aenter__.return_value = mock_session

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.__aenter__.return_value.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        await _fetch_events(mock_session_maker)

    # Verify the session was used correctly
    mock_session_maker.assert_called_once()
    # Verify HTTP request was made
    mock_client.__aenter__.return_value.get.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_events_http_error():
    """Test fetch_events_task function with HTTP error."""
    mock_session_maker = MagicMock(spec=async_sessionmaker)
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session_maker.return_value.__aenter__.return_value = mock_session

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.__aenter__.return_value.get.side_effect = httpx.RequestError(
        "Test error"
    )

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(httpx.RequestError):
            await _fetch_events(mock_session_maker)

    # Verify the session was created
    mock_session_maker.assert_called_once()
