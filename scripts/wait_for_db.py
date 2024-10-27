import os
import time

import psycopg2
from psycopg2 import OperationalError


def wait_for_db():
    db_host = os.environ.get("POSTGRES_HOST", "db")
    db_name = os.environ.get("POSTGRES_DB")
    db_user = os.environ.get("POSTGRES_USER")
    db_password = os.environ.get("POSTGRES_PASSWORD")
    while True:
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
            )
            conn.close()
            print("Database is ready!")
            break
        except OperationalError:
            print("Database is not ready. Waiting...")
            time.sleep(5)


if __name__ == "__main__":
    wait_for_db()
