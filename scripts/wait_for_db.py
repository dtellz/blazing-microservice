"""Utility script to wait for the database to be ready on startup."""

import asyncio
import os

import asyncpg


async def wait_for_db():
    db_host = os.environ.get("POSTGRES_HOST", "db")
    db_name = os.environ.get("POSTGRES_DB")
    db_user = os.environ.get("POSTGRES_USER")
    db_password = os.environ.get("POSTGRES_PASSWORD")
    while True:
        try:
            conn = await asyncpg.connect(
                database=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
            )
            await conn.close()
            print("Database is ready!")
            break
        except (asyncpg.CannotConnectNowError, ConnectionRefusedError):
            print("Database is not ready. Waiting...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(wait_for_db())
