.PHONY: test lint run

test:
	pytest

lint:
	ruff check .

run:
	python -m astguiclient.lead_sync
