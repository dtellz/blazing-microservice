"""Schemas for the events."""

from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, Field


class EventSummary(BaseModel):
    """Event summary schema."""

    id: UUID = Field(..., description="Identifier for the plan (UUID)")
    title: str = Field(..., description="Title of the plan")
    start_date: date = Field(
        ..., description="Date when the event starts in local time"
    )
    start_time: time | None = Field(
        None,
        description="Time when the event starts in local time",
        example="22:38:19",
    )
    end_date: date | None = Field(
        None,
        description="Date when the event ends in local time",
    )
    end_time: time | None = Field(
        None,
        description="Time when the event ends in local time",
        example="14:45:15",
    )
    min_price: float | None = Field(
        None,
        description="Min price from all the available tickets",
    )
    max_price: float | None = Field(
        None,
        description="Max price from all the available tickets",
    )


class EventList(BaseModel):
    """List of event summaries."""

    events: list[EventSummary]


class ErrorResponse(BaseModel):
    """Error response schema."""

    code: str
    message: str


class SearchSuccessResponse(BaseModel):
    """Search response schema."""

    data: EventList | None = None
    error: None = None


class SearchErrorResponse(BaseModel):
    """Search error response schema."""

    data: None = None
    error: ErrorResponse
