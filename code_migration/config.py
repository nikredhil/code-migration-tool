"""Self-contained config for the code-migration tool.

Holds runtime settings (LLM provider, execution backend, MLflow, GitHub) and the
example registry. The tool is standalone — it does not import the accelerator;
it only hands the accelerator a tfvars/bundle path when it wants infra.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

HERE = Path(__file__).resolve().parent           # code_migration/
REPO_ROOT = HERE.parent                           # tool repo root (git root)
SKILLS_FILE = REPO_ROOT / "SKILLS.md"
EXAMPLES_DIR = HERE / "examples"
CONVERTED_DIR = REPO_ROOT / "converted"           # converted PySpark (PR content)
DEPLOY_DIR = REPO_ROOT / "deploy"                 # tfvars + bundle handed to the accelerator

# Input tables available to every converted transform (registered as temp views).
TABLE_SCHEMA = """\
Available input tables (read via spark.table("<name>")):

  regions(region_id INT, region_name STRING)
  customers(customer_id INT, region_id INT, signup_date DATE)
  orders(order_id INT, customer_id INT, order_date DATE, amount DOUBLE, status STRING)
"""


@dataclass(frozen=True)
class Example:
    key: str
    path: Path
    expected_language: str


EXAMPLES: dict[str, Example] = {
    "sql": Example("sql", EXAMPLES_DIR / "sql" / "revenue_by_region.sql", "sql"),
    "dbt": Example("dbt", EXAMPLES_DIR / "dbt" / "customer_ltv.sql", "dbt"),
    "spark": Example("spark", EXAMPLES_DIR / "spark" / "active_users.py", "spark"),
}


@dataclass(frozen=True)
class Settings:
    databricks_host: str = field(default_factory=lambda: os.getenv("DATABRICKS_HOST", ""))
    databricks_token: str = field(default_factory=lambda: os.getenv("DATABRICKS_TOKEN", ""))
    # candidate execution backend: local | databricks | databricks_sql
    candidate_backend: str = field(default_factory=lambda: os.getenv("CANDIDATE_BACKEND", "local"))
    # conversion provider: rule | anthropic | databricks (workspace-hosted Claude)
    converter_provider: str = field(default_factory=lambda: os.getenv("CONVERTER_PROVIDER", "rule"))
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    # observability
    mlflow_enabled: bool = field(default_factory=lambda: os.getenv("MLFLOW_ENABLED", "true").lower() == "true")
    mlflow_tracking_uri: str = field(default_factory=lambda: os.getenv("MLFLOW_TRACKING_URI", "databricks"))
    mlflow_experiment: str = field(default_factory=lambda: os.getenv("MLFLOW_EXPERIMENT", ""))
    # PR creation
    github_repo: str = field(default_factory=lambda: os.getenv("GITHUB_REPO", ""))
    pr_base_branch: str = field(default_factory=lambda: os.getenv("PR_BASE_BRANCH", "main"))


SETTINGS = Settings()
