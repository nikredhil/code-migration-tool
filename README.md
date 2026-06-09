# Code-Migration Tool

Agentic tool that migrates legacy pipeline code to **Databricks PySpark** and
proves the conversion is correct before a human sees it:

> **detect** language (SQL / dbt / Spark) → **convert** to Databricks PySpark →
> run the converted code on **Databricks** *and* the original on an **independent
> engine (DuckDB)** against the same data sample → **compare**. Pass ✅ → raise a
> PR for review. Fail ❌ → retry, appending a lesson to `SKILLS.md`.

Every converted module is gated by a **static AST safety check** before it runs,
and every run is logged to **MLflow**.

It runs on infra provisioned by the separate **lakebase-accelerator** (loose
coupling: this repo just hands the accelerator a tfvars/bundle under `deploy/`).

## Layout
```
code_migration/
  pipeline/   detect · convert · safety · runners (duckdb / serverless-sql / cluster) · compare · pr · orchestrator · llm
  examples/   sql · dbt · spark sources (one shared schema)
  data/       deterministic mock data + sampler
  config.py   settings + example registry  ·  run.py  entrypoint
SKILLS.md     self-updating conversion heuristics
demo_notebook.py   Databricks demo (widgets + MLflow link)
deploy/       code_migration.tfvars + bundle/  (handed to the accelerator)
tests/
```

## Quick start
```bash
cp .env.example .env        # Databricks host/token, backend, provider, GITHUB_REPO
make install
make test                   # offline: data gen, dbt render, DuckDB reference, compare, safety guard

# run the pipeline
make run                                   # uses .env defaults
python -m code_migration.run --example sql --backend databricks_sql --provider rule --pr-live
```

## Providers (conversion) × backends (candidate execution)
| Provider | Needs | Notes |
|---|---|---|
| `rule` | nothing | deterministic SQL→`spark.sql`, dbt render, Spark pass-through |
| `anthropic` | `ANTHROPIC_API_KEY` | Claude API |
| `databricks` | workspace serving endpoint | hosted Claude (`databricks-claude-opus-4-8`), no external key |

| Backend | Runs on | Pair with |
|---|---|---|
| `local` | local pyspark (needs Java) | any provider (dry-run) |
| `databricks_sql` | serverless SQL warehouse (fast) | `rule` (emits `spark.sql`) |
| `databricks` | cluster via Command Execution | `databricks`/`anthropic` (DataFrame API) |

## Infra (via the accelerator)
This tool doesn't manage infra. To get a cluster, hand its tfvars to the
lakebase-accelerator:
```bash
lakebase deploy  code_migration --vars deploy/code_migration_lowcost.tfvars --bundle deploy/bundle
lakebase destroy code_migration --vars deploy/code_migration_lowcost.tfvars
```
For fast demos use serverless (`databricks_sql`) and skip the cluster entirely.
