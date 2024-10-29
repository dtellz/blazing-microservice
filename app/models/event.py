"""Models for the events."""

from datetime import date, time
from uuid import UUID, uuid4

from sqlalchemy import Date, Float, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Event(Base):
    """Event model."""

    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        nullable=False,
    )
    provider_unique_id: Mapped[str] = mapped_column(
        String,
        index=True,
        unique=True,
    )
    provider_base_event_id: Mapped[str] = mapped_column(String, index=True)
    provider_event_id: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    min_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_price: Mapped[float | None] = mapped_column(Float, nullable=True)
