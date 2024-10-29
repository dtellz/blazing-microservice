"""API routes for the events."""

from datetime import datetime

from fastapi import APIRouter, Query

from app.dependencies import EventServiceDep, SessionDep
from app.schemas.event import SearchErrorResponse, SearchSuccessResponse

router = APIRouter()


@router.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    """Check if the API is healthy."""
    # For debugging purposes during development
    return {"status": "OK"}


@router.get(
    "/search",
    responses={
        200: {
            "description": "List of plans",
            "model": SearchSuccessResponse,
        },
        400: {
            "description": "The request was not correctly formed (missing required parameters, wrong types...)",  # noqa: E501
            "model": SearchErrorResponse,
        },
        500: {
            "description": "Generic error",
            "model": SearchErrorResponse,
        },
    },
    openapi_extra={
        "description": "",
        "summary": "Lists the available events on a time range",
    },  # Avoid docstring in FastAPI docs
)
async def get_events(
    session: SessionDep,
    event_service: EventServiceDep,
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
) -> SearchSuccessResponse | SearchErrorResponse:
    """Search for events within a given date range.

    Args:
        event_service: Event service dependency for handling event operations
        starts_at: Start date/time to search from (inclusive)
        ends_at: End date/time to search until (inclusive)

    Returns:
        SearchSuccessResponse containing list of matching events
        SearchErrorResponse containing error details
    """

    return await event_service.search_events(session, starts_at, ends_at)
