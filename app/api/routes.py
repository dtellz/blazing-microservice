from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from app.dependencies import SessionDep
from app.models.event import Event
from app.schemas.event import EventList, EventListResponse, EventSummary

router = APIRouter()


@router.get("/healthcheck")
async def healthcheck():
    return {"status": "OK"}


@router.get("/events", response_model=EventListResponse)
def get_events(
    session: SessionDep,
    starts_at: datetime = Query(
        ...,
        description="Start date and time in ISO format",
    ),
    ends_at: datetime = Query(
        ...,
        description="End date and time in ISO format",
    ),
):
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

    return EventListResponse(data=EventList(events=event_summaries))
