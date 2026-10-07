from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def test_protected_rubric_is_unchanged() -> None:
    manifest = json.loads((ROOT / "data" / "source_manifest.json").read_text(encoding="utf-8"))
    protected = manifest["protected_files"]
    assert len(protected) == 1
    filename, metadata = next(iter(protected.items()))
    assert metadata["policy"] == "read_only_do_not_modify"
    assert sha256(ROOT / filename) == metadata["sha256"]


def test_institution_dataset_meets_minimum_quality() -> None:
    frame = pd.read_csv(ROOT / "data" / "processed" / "institutions.csv", low_memory=False)
    assert len(frame) >= 5_000
    assert frame["unitid"].is_unique
    assert frame["completion_rate"].notna().sum() >= 5_000
    assert frame[["latitude", "longitude"]].notna().all(axis=1).sum() >= 5_000


def test_rates_and_binary_target_are_valid() -> None:
    frame = pd.read_csv(ROOT / "data" / "processed" / "institutions.csv", low_memory=False)
    for column in [
        "completion_rate",
        "retention_rate",
        "pell_share",
        "federal_loan_share",
        "withdrawal_3yr_rate",
    ]:
        values = frame[column].dropna()
        assert values.between(0, 1).all(), column
    assert set(frame["low_completion"].dropna().astype(int).unique()) <= {0, 1}


def test_history_supports_temporal_holdout() -> None:
    history = pd.read_csv(
        ROOT / "data" / "processed" / "institution_history.csv", low_memory=False
    )
    assert history["academic_year"].nunique() >= 2
    assert history["academic_year"].max() == 2022
    assert history["academic_year"].min() == 2017

