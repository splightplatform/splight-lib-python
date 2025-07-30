.PHONY: clean clean-test clean-pyc help
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

update-version:
	poetry version $(scope)

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	find . -name '*.pytest_cache' -exec rm -rf {} +
	rm -f .coverage

test: ## run tests with pytest
	uv run pytest splight_lib/

flake8:  ## run flake8 linter
	flake8 .

coverage: ## run coverage
	coverage run --source=. -m pytest; coverage report -m

install: clean ## install the package to the active Python's site-packages
	pip install -e ".[dev]"
	pre-commit install

black: ## run black formatter
	black .

isort: ## run isort formatter
	isort .

format: 
	isort splight_lib/
	ruff format splight_lib/

check_isort:
	isort --check-only --diff splight_lib/

check_ruff:
	ruff format --check --diff splight_lib/

check_format: check_ruff check_isort 
