"""Fetch events from the external API."""

import logging
from datetime import datetime

import requests
from lxml import etree
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from app.core.config import settings
from app.dependencies import get_db
from app.models.event import Event
from app.worker import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=5)
def fetch_events_task(self) -> None:
    """Fetch events from the external API."""

    db = next(get_db())
    try:
        response = requests.get(settings.EXTERNAL_API_URL, timeout=10)
        response.raise_for_status()
        xml_content = response.content

        events = parse_xml(xml_content)
        upsert_events(events, db)

    except requests.exceptions.RequestException as exc:
        logger.error(f"Error fetching events: {exc}")
        # exponential backoff retry
        self.retry(exc=exc, countdown=2**self.request.retries)
    finally:
        db.close()


def parse_xml(xml_content: bytes) -> list[dict]:
    """Parse the XML content from the external API."""

    root = etree.fromstring(xml_content)
    events = []
    for base_event_elem in root.xpath("//base_event"):
        sell_mode = base_event_elem.get("sell_mode")
        if sell_mode != "online":
            continue

        base_event_id = base_event_elem.get("base_event_id")
        title = base_event_elem.get("title")

        for event_elem in base_event_elem.xpath("./event"):
            event_id = event_elem.get("event_id")
            provider_unique_id = f"{base_event_id}_{event_id}"

            event_start_datetime = datetime.fromisoformat(
                event_elem.get("event_start_date")
            )
            event_end_datetime = datetime.fromisoformat(
                event_elem.get("event_end_date")
            )

            # Aggregate prices from zones
            min_price = None
            max_price = None
            for zone_elem in event_elem.xpath("./zone"):
                price = float(zone_elem.get("price", "0") or "0")
                if min_price is None or price < min_price:
                    min_price = price
                if max_price is None or price > max_price:
                    max_price = price

            event_data = {
                "provider_unique_id": provider_unique_id,
                "provider_base_event_id": base_event_id,
                "provider_event_id": event_id,
                "title": title,
                "start_date": event_start_datetime.date(),
                "start_time": event_start_datetime.time(),
                "end_date": event_end_datetime.date(),
                "end_time": event_end_datetime.time(),
                "min_price": min_price,
                "max_price": max_price,
            }
            events.append(event_data)
    return events


def upsert_events(events: list[dict], db) -> None:
    """Upsert events to the database."""

    existing_events = db.exec(select(Event)).all()
    existing_events_by_provider_unique_id = {
        e.provider_unique_id: e for e in existing_events
    }

    for event_data in events:
        provider_unique_id = event_data["provider_unique_id"]
        event = existing_events_by_provider_unique_id.get(provider_unique_id)
        if event:
            # Update existing event
            for key, value in event_data.items():
                if key != "id":  # Don't overwrite our UUID
                    setattr(event, key, value)
        else:
            # Create new event
            event = Event(**event_data)
            db.add(event)
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error saving events to the database: {e}")
