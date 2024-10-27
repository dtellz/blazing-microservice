from datetime import date, time
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )
    provider_unique_id: str = Field(..., index=True)
    provider_base_event_id: str = Field(..., index=True)
    provider_event_id: str = Field(..., index=True)
    title: str = Field(..., nullable=False)
    start_date: date = Field(..., nullable=False)
    start_time: Optional[time] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    end_time: Optional[time] = Field(default=None)
    min_price: Optional[float] = Field(default=None)
    max_price: Optional[float] = Field(default=None)
