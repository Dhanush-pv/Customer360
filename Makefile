.PHONY: up down logs generate init-db load test lint reset
up:
	docker compose up -d postgres
down:
	docker compose down
logs:
	docker compose logs -f postgres
generate:
	python -m customer360 generate --output data/generated --seed 42
init-db:
	python -m customer360 init-db
load:
	python -m customer360 load --input data/generated
test:
	pytest
lint:
	ruff check customer360 tests
reset:
	docker compose down -v
