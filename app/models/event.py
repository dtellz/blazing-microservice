"""Models for the events."""

from datetime import date, time
from uuid import UUID, uuid4

from sqlalchemy import Date, Float, Index, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Event(Base):
    """Event model."""

    __tablename__ = "events"

    __table_args__ = (
        Index("idx_date_range", "start_date", "end_date"),
        Index(
            "idx_provider_ids",
            "provider_unique_id",
            "provider_base_event_id",
            "provider_event_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        nullable=False,
    )
    provider_unique_id: Mapped[str] = mapped_column(String, unique=True)
    provider_base_event_id: Mapped[str] = mapped_column(String)
    provider_event_id: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    min_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_price: Mapped[float | None] = mapped_column(Float, nullable=True)
