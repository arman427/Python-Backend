.PHONY: db-up db-down db-logs run

db-up:
	docker compose up -d

db-down:
	docker compose down

db-logs:
	docker compose logs -f db

run:
	uvicorn app.main:app --reload