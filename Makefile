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
	uv version --bump=$(scope)

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

install:
	uv sync --all-extras

install-dev:
	uv sync --all-extras --dev

isort: ## run isort formatter
	uv run isort .


format: install-dev
	uv run pre-commit run --all-files

check-format: install-dev
	uv run pre-commit run --all-files
	# --show-diff-on-failure

# format: 
# 	uv run isort splight_lib/
# 	uv run ruff format splight_lib/
#
# check_isort:
# 	uv run isort --check-only --diff splight_lib/
#
# check_ruff:
# 	uv run ruff format --check --diff splight_lib/
#
# check_format: check_ruff check_isort 
#
