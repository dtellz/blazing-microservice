from datetime import date, time
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class EventSummary(BaseModel):
    id: UUID = Field(..., description="Identifier for the plan (UUID)")
    title: str = Field(..., description="Title of the plan")
    start_date: date = Field(
        ..., description="Date when the event starts in local time"
    )
    start_time: Optional[time] = Field(
        None,
        description="Time when the event starts in local time",
        example="22:38:19",
    )
    end_date: Optional[date] = Field(
        None, description="Date when the event ends in local time"
    )
    end_time: Optional[time] = Field(
        None,
        description="Time when the event ends in local time",
        example="14:45:15",
    )
    min_price: Optional[float] = Field(
        None, description="Min price from all the available tickets"
    )
    max_price: Optional[float] = Field(
        None, description="Max price from all the available tickets"
    )


class EventList(BaseModel):
    events: List[EventSummary]
