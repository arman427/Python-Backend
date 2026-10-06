.PHONY: up down logs test run migrate seed
up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api

run:
	uvicorn app.main:app --reload

migrate:
	alembic upgrade head

seed:
	python -m app.seed

test:
	pytest -q
