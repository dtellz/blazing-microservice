from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.tasks.fetch_events import parse_xml, upsert_events


@pytest.mark.asyncio
async def test_parse_xml():
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
