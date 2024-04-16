# Makefile for managing Celery commands

.PHONY: help run-worker run-beat

help:
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@echo "  run-worker            Start Celery worker"
	@echo "  run--without-beat     Start Celery worker"
	@echo "  run-beat              Start Celery beat scheduler"

run-worker:
	@echo "Starting Celery worker, beat..."
	celery -A worker.app worker --beat --loglevel=info

run-worker-without-beat:
	@echo "Starting Celery worker..."
	celery -A worker.app worker --loglevel=info

run-beat:
	@echo "Starting Celery beat scheduler..."
	celery -A worker.app beat --loglevel=info

alembic-autogenerate:
	@echo "Generating migration..."
	alembic revision --autogenerate -m "$(MESSAGE)"

alembic-upgrade:
	@echo "Upgrading database..."
	alembic upgrade head

.PHONY: format
format:
	$(call log, reorganizing imports & formatting code)
	poetry run black .
	poetry run isort .
	poetry run ruff check . --fix --exit-zero