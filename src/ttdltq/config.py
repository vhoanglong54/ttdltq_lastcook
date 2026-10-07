from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
MODEL_DIR = PROJECT_ROOT / "models"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
DOCS_DIR = PROJECT_ROOT / "docs"
REPORT_DIR = PROJECT_ROOT / "report"


def load_yaml(name: str) -> dict[str, Any]:
    """Load a UTF-8 YAML configuration from the project config directory."""

    path = CONFIG_DIR / name
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML mapping: {path}")
    return data


def ensure_runtime_directories() -> None:
    """Create only directories used for generated artifacts."""

    for path in (
        RAW_DIR,
        INTERIM_DIR,
        PROCESSED_DIR,
        MODEL_DIR,
        OUTPUT_DIR / "figures",
        OUTPUT_DIR / "eda",
        REPORT_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)

