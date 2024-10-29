.PHONY: run build start stop down clean

run: build start

build:
	docker compose build

start:
	docker compose up -d

restart: down run

stop:
	docker compose stop

down:
	docker compose down

clean:
	docker compose down -v

run-task:
	docker compose exec celery_worker celery -A app.worker call app.tasks.fetch_events.fetch_events_task

test: 
	poetry run pytest --cov=app
