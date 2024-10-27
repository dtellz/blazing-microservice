FROM python:3.12.7-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

COPY . .

RUN chmod +x scripts/wait_for_db.py

EXPOSE 8000

CMD ["sh", "-c", "python scripts/wait_for_db.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
