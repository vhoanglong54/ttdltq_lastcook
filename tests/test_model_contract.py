from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def load_metrics() -> dict:
    return json.loads((ROOT / "models" / "metrics.json").read_text(encoding="utf-8"))


def test_model_meets_locked_accuracy_gate() -> None:
    metrics = load_metrics()
    selected = metrics["models"][metrics["selected_model"]]
    assert selected["accuracy"] >= 0.80
    assert metrics["models"]["structural_logistic"]["accuracy"] >= 0.80
    assert metrics["models"]["early_warning_logistic"]["accuracy"] >= 0.80
    assert metrics["quality_gate_passed"] is True
    assert metrics["split"]["strategy"] == "temporal_last_year_holdout"
    assert metrics["split"]["test_years"] == [2022]


def test_model_features_do_not_leak_target() -> None:
    metrics = load_metrics()
    features = set(metrics["features"]["numeric"] + metrics["features"]["categorical"])
    forbidden = {"completion_rate", "low_completion", "c150_4", "c150_l4"}
    assert not features.intersection(forbidden)


def test_predictions_have_probability_and_one_row_per_current_institution() -> None:
    predictions = pd.read_csv(
        ROOT / "data" / "processed" / "model_predictions.csv", low_memory=False
    )
    assert predictions["unitid"].is_unique
    assert predictions["risk_probability"].between(0, 1).all()
    assert set(predictions["risk_level"].dropna().unique()) <= {"Thấp", "Trung bình", "Cao"}


def test_dashboard_does_not_rank_named_institutions() -> None:
    source = (ROOT / "dashboard" / "app.py").read_text(encoding="utf-8")
    assert "institution_name" not in source
    assert "Danh sách cơ sở" not in source

