PY ?= python3
DB ?= $(SKILLGUARD_DB)
export PYTHONPATH := src

.PHONY: setup test baseline-fixtures pipeline index sample scan analyze validation-sheet benchmark check

setup:
	$(PY) -m pip install -e ".[dev,analysis]"

test:
	$(PY) -m pytest -q

# Runs the Sprint 1 baseline on hand-written fixtures (NOT research results).
baseline-fixtures:
	$(PY) -m skillguard.baseline tests/fixtures/repos --out results/fixtures

# Sprint 2 pipeline on the GitSkills release: make pipeline DB=/path/to/agent_skills_release.db
pipeline: index sample scan analyze validation-sheet

index:
	mkdir -p data/interim
	$(PY) -m skillguard index --db "$(DB)"

sample:
	$(PY) -m skillguard sample --db "$(DB)" --per-group 5000

scan:
	$(PY) -m skillguard scan

analyze:
	mkdir -p figures results
	$(PY) -m skillguard analyze

validation-sheet:
	mkdir -p data/annotations
	$(PY) -m skillguard annotation-sample

# SWE 330 GQM evidence: Q4 performance and Q5 completeness/schema
benchmark:
	$(PY) scripts/benchmark.py

check:
	$(PY) scripts/check_outputs.py
