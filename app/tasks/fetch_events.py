"""Fetch events from the external API."""

import asyncio
import logging
from datetime import datetime

import httpx
from lxml import etree
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.models.event import Event
from app.worker import celery_app

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # isort: skip  # fmt: skip # noqa: E501


logger = logging.getLogger(__name__)


async def _fetch_events(session_maker: async_sessionmaker) -> None:
    """Asynchronous helper function to fetch events."""
    try:
        logger.info("Starting to fetch events from external API.")
        async with session_maker() as session:
            # Fetch XML data
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    settings.EXTERNAL_API_URL,
                    timeout=10,
                )
                response.raise_for_status()
                xml_content = response.content
                logger.info("Successfully fetched events from external API.")

            # Parse events
            events = parse_xml(xml_content)
            logger.info(f"Parsed {len(events)} events from XML.")

            batch_size = 50
            for i in range(0, len(events), batch_size):
                batch = events[i : i + batch_size]  # noqa: E203
                await upsert_events(batch, session)
                logger.info(f"Upserted batch of {len(batch)} events.")

    except httpx.RequestError as exc:
        logger.error(f"HTTP request error while fetching events: {exc}")
        raise  # Reraise the exception to be caught by the outer try-except

    except Exception as exc:
        logger.error(f"Unexpected error in _fetch_events: {exc}")
        raise


def parse_xml(xml_content: bytes) -> list[dict]:
    """Parse the XML content from the external API."""
    try:
        root = etree.fromstring(xml_content)
    except etree.XMLSyntaxError as e:
        logger.error(f"XML parsing error: {e}")
        return []

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

            try:
                event_start_datetime = datetime.fromisoformat(
                    event_elem.get("event_start_date")
                )
                event_end_datetime = datetime.fromisoformat(
                    event_elem.get("event_end_date")
                )
            except ValueError as e:
                logger.error(f"Parsing error: {e}")
                continue  # Skip events with invalid dates

            # Aggregate prices from zones
            min_price = None
            max_price = None
            for zone_elem in event_elem.xpath("./zone"):
                try:
                    price = float(zone_elem.get("price", "0") or "0")
                except ValueError as e:
                    logger.error(f"Parsing error: {e}")
                    price = 0.0
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


async def upsert_events(events: list[dict], session: AsyncSession) -> None:
    """Upsert events to the database using ON CONFLICT."""
    if not events:
        logger.info("No events to upsert.")
        return

    try:
        stmt = insert(Event).values(events)
        update_dict = {
            c.name: getattr(stmt.excluded, c.name)
            for c in Event.__table__.columns
            if c.name != "id"
        }
        stmt = stmt.on_conflict_do_update(
            index_elements=["provider_unique_id"],
            set_=update_dict,
        )

        await session.execute(stmt)
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Error saving events to the database: {e}")
        raise


@celery_app.task(bind=True, max_retries=5)
def fetch_events_task(self) -> None:
    """Fetch events from the external API."""
    try:
        # Create a new event loop for this task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Create a new async engine and session maker bound to this loop
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        session_maker = async_sessionmaker(engine, expire_on_commit=False)

        loop.run_until_complete(_fetch_events(session_maker))
    except Exception as exc:
        logger.error(f"Error in fetch_events_task: {exc}")
        # Exponential backoff retry
        self.retry(exc=exc, countdown=2**self.request.retries)
    finally:
        loop.close()
