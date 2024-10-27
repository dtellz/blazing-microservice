"""API routes for the events."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from app.dependencies import SessionDep
from app.models.event import Event
from app.schemas.event import EventList, EventSummary, SearchResponse

router = APIRouter()


@router.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    """Check if the API is healthy."""
    return {"status": "OK"}


@router.get(
    "/search",
    response_model=SearchResponse,
    openapi_extra={
        "description": "",
        "summary": "Lists the available events on a time range",
    },  # Avoid docstring in FastAPI docs
)
def get_events(
    session: SessionDep,
    starts_at: datetime = Query(
        ...,
        description="Return only events that starts after this date",
        example="2017-07-21T17:32:28Z",
    ),
    ends_at: datetime = Query(
        ...,
        description="Return only events that finishes before this date",
        example="2021-07-21T17:32:28Z",
    ),
) -> SearchResponse:
    """Search for events within a given date range.

    Args:
        session: Database session dependency
        starts_at: Start date/time to search from (inclusive)
        ends_at: End date/time to search until (inclusive)

    Returns:
        SearchResponse containing list of matching events

    Raises:
        HTTPException: If starts_at is not before ends_at
    """
    # Convert naive datetimes to UTC if they don't have tzinfo
    if starts_at.tzinfo is None:
        starts_at = starts_at.replace(tzinfo=timezone.utc)
    if ends_at.tzinfo is None:
        ends_at = ends_at.replace(tzinfo=timezone.utc)

    if starts_at >= ends_at:
        raise HTTPException(
            status_code=400,
            detail="starts_at must be before ends_at",
        )

    statement = select(Event).where(
        Event.start_date >= starts_at.date(),
        Event.end_date <= ends_at.date(),
    )
    events = session.exec(statement).all()

    # Convert Event models to EventSummary schemas
    event_summaries = [
        EventSummary.model_validate(event.model_dump()) for event in events
    ]

    return SearchResponse(data=EventList(events=event_summaries))
