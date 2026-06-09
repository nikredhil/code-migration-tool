.PHONY: install install-spark data test run help

PY ?= python3

install:                 ## install deps
	$(PY) -m pip install -r requirements.txt

install-spark:           ## local dry-run extra (needs Java; not with databricks-connect)
	$(PY) -m pip install pyspark

data:                    ## generate the small mock data sample
	$(PY) -m code_migration.data.generate_mock_data

test:                    ## local tests (no workspace / no API key needed)
	$(PY) -m pytest tests -q

run:                     ## run the pipeline (defaults from .env)
	$(PY) -m code_migration.run --example all

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "};{printf "  %-14s %s\n",$$1,$$2}'
