PY ?= python3

.PHONY: setup test baseline-fixtures

setup:
	$(PY) -m pip install -e ".[dev]"

test:
	$(PY) -m pytest -q

# Runs the Sprint 1 baseline on hand-written fixtures (NOT research results).
baseline-fixtures:
	PYTHONPATH=src $(PY) -m skillguard.baseline tests/fixtures/repos --out results/fixtures
