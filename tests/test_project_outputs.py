from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_outputs_exist_and_are_nonempty() -> None:
    paths = [
        "data/processed/institutions.csv",
        "data/processed/institution_history.csv",
        "data/processed/state_summary.csv",
        "data/processed/field_summary.csv",
        "data/processed/equity_long.csv",
        "data/processed/model_predictions.csv",
        "models/metrics.json",
        "models/confusion_matrix.csv",
        "models/feature_importance.csv",
        "models/model_card.md",
        "outputs/eda/insights.json",
        "outputs/eda/data_quality_audit.json",
        "dashboard/app.py",
    ]
    for relative in paths:
        path = ROOT / relative
        assert path.exists(), relative
        assert path.stat().st_size > 0, relative


def test_five_static_eda_figures_exist() -> None:
    figures = list((ROOT / "outputs" / "figures").glob("eda_*.png"))
    assert len(figures) >= 5

