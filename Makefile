help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "		install			Install dependencies"
	@echo "		test			Run tests"
	@echo "		lint			Run linters"
	@echo "		format			Run formatters"
	@echo "		format-and-lint		Run formatters, then run linters"
	@echo "		clean			Clean/remove cached and elective files"

install:
	poetry install
	poetry run pre-commit install

test:
	poetry run pytest -v \
		--cov-report term-missing \
		--cov-branch \
		--cov-report=xml \
		--cov=src/textbelt_py \
		--cov-fail-under=100

lint:
	poetry run ruff check
	poetry run mypy .

format:
	poetry run ruff check --extend-select I --fix
	poetry run ruff format

format-and-lint: format lint

clean:
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -f .coverage


.PHONY: install test lint format format-and-lint clean help
