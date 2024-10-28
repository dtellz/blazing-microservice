from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.event import Event
from app.schemas.event import EventList, EventSummary, SearchResponse


class EventService:
    """Service layer for event-related operations."""

    def __init__(self):
        pass

    @staticmethod
    def _ensure_utc_timezone(dt: datetime) -> datetime:
        """Ensure datetime has UTC timezone."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @staticmethod
    def _validate_date_range(starts_at: datetime, ends_at: datetime) -> None:
        """Validate that starts_at is before ends_at."""
        if starts_at >= ends_at:
            raise HTTPException(
                status_code=400, detail="starts_at must be before ends_at"
            )

    def search_events(
        self, session: Session, starts_at: datetime, ends_at: datetime
    ) -> SearchResponse:
        """Search for events within a given date range.

        Args:
            starts_at: Start date/time to search from (inclusive)
            ends_at: End date/time to search until (inclusive)

        Returns:
            SearchResponse containing list of matching events
        """
        starts_at = self._ensure_utc_timezone(starts_at)
        ends_at = self._ensure_utc_timezone(ends_at)

        self._validate_date_range(starts_at, ends_at)

        statement = select(Event).where(
            Event.start_date >= starts_at.date(),
            Event.end_date <= ends_at.date(),
        )
        events = session.exec(statement).all()

        event_summaries = [
            EventSummary.model_validate(event.model_dump()) for event in events
        ]

        return SearchResponse(data=EventList(events=event_summaries))
