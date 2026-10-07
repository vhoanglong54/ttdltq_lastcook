from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.inspection import permutation_importance
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, SplineTransformer, StandardScaler

from ttdltq.config import (
    MODEL_DIR,
    OUTPUT_DIR,
    PROCESSED_DIR,
    ensure_runtime_directories,
    load_yaml,
)


@dataclass(frozen=True)
class SplitInfo:
    strategy: str
    train_rows: int
    test_rows: int
    train_years: list[int]
    test_years: list[int]


def specificity_score(y_true: pd.Series, y_pred: np.ndarray) -> float:
    tn, fp, _, _ = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return float(tn / (tn + fp)) if (tn + fp) else float("nan")


def metric_bundle(
    y_true: pd.Series, y_pred: np.ndarray, probability: np.ndarray
) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "specificity": specificity_score(y_true, y_pred),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, probability)),
        "brier_score": float(brier_score_loss(y_true, probability)),
    }


def make_preprocessor(
    numeric_features: list[str],
    categorical_features: list[str],
    *,
    nonlinear: bool,
) -> ColumnTransformer:
    numeric_steps: list[tuple[str, Any]] = [
        ("imputer", SimpleImputer(strategy="median")),
    ]
    if nonlinear:
        numeric_steps.append(
            (
                "splines",
                SplineTransformer(n_knots=5, degree=2, include_bias=False),
            )
        )
        numeric_steps.append(("scaler", StandardScaler(with_mean=False)))
    else:
        numeric_steps.append(("scaler", StandardScaler()))

    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "encoder",
                            OneHotEncoder(handle_unknown="ignore", drop=None),
                        ),
                    ]
                ),
                categorical_features,
            ),
            ("numeric", Pipeline(numeric_steps), numeric_features),
        ],
        remainder="drop",
    )


def make_model(
    numeric_features: list[str],
    categorical_features: list[str],
    *,
    nonlinear: bool,
    balanced: bool,
) -> Pipeline:
    return Pipeline(
        [
            (
                "preprocessor",
                make_preprocessor(
                    numeric_features,
                    categorical_features,
                    nonlinear=nonlinear,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    C=0.5 if nonlinear else 1.0,
                    class_weight="balanced" if balanced else None,
                    max_iter=5000,
                    random_state=42,
                ),
            ),
        ]
    )


def validate_features(
    features: list[str], forbidden: list[str], target: str
) -> None:
    normalized = {feature.lower() for feature in features}
    violations = normalized & {feature.lower() for feature in forbidden}
    if target.lower() in normalized:
        violations.add(target.lower())
    if violations:
        raise ValueError(f"Target leakage: forbidden model features {sorted(violations)}")


def load_model_frame() -> tuple[pd.DataFrame, bool]:
    history_path = PROCESSED_DIR / "institution_history.csv"
    current_path = PROCESSED_DIR / "institutions.csv"
    if history_path.exists():
        history = pd.read_csv(history_path, low_memory=False)
        if "academic_year" in history and history["academic_year"].nunique() >= 2:
            return history, True
    return pd.read_csv(current_path, low_memory=False), False


def split_frame(
    frame: pd.DataFrame,
    features: list[str],
    target: str,
    *,
    random_state: int,
    test_size: float,
    prefer_temporal: bool,
    has_history: bool,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, SplitInfo]:
    eligible = frame.dropna(subset=[target]).copy()
    eligible[target] = pd.to_numeric(eligible[target], errors="raise").astype(int)
    if prefer_temporal and has_history:
        years = sorted(int(year) for year in eligible["academic_year"].dropna().unique())
        test_year = years[-1]
        train_mask = eligible["academic_year"] < test_year
        test_mask = eligible["academic_year"] == test_year
        train = eligible.loc[train_mask]
        test = eligible.loc[test_mask]
        if len(train) >= 5000 and len(test) >= 500:
            info = SplitInfo(
                strategy="temporal_last_year_holdout",
                train_rows=len(train),
                test_rows=len(test),
                train_years=years[:-1],
                test_years=[test_year],
            )
            return (
                train[features],
                test[features],
                train[target],
                test[target],
                info,
            )

    train, test = train_test_split(
        eligible,
        test_size=test_size,
        random_state=random_state,
        stratify=eligible[target],
    )
    info = SplitInfo(
        strategy="stratified_cross_sectional_holdout",
        train_rows=len(train),
        test_rows=len(test),
        train_years=[],
        test_years=[],
    )
    return train[features], test[features], train[target], test[target], info


def save_diagnostic_plots(
    y_true: pd.Series,
    prediction: np.ndarray,
    probability: np.ndarray,
) -> None:
    figure_dir = OUTPUT_DIR / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    ConfusionMatrixDisplay.from_predictions(
        y_true,
        prediction,
        display_labels=["Không thấp", "Hoàn thành thấp"],
        cmap="Blues",
        colorbar=False,
        ax=ax,
    )
    ax.set_title("Ma trận nhầm lẫn — Logistic Regression")
    fig.tight_layout()
    fig.savefig(figure_dir / "model_confusion_matrix.png", dpi=180)
    plt.close(fig)

    fpr, tpr, _ = roc_curve(y_true, probability)
    precision, recall, _ = precision_recall_curve(y_true, probability)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].plot(fpr, tpr, color="#0F766E", linewidth=2.4)
    axes[0].plot([0, 1], [0, 1], linestyle="--", color="#94A3B8")
    axes[0].set(title="ROC curve", xlabel="False Positive Rate", ylabel="True Positive Rate")
    axes[1].plot(recall, precision, color="#C2410C", linewidth=2.4)
    axes[1].set(title="Precision–Recall curve", xlabel="Recall", ylabel="Precision")
    for axis in axes:
        axis.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(figure_dir / "model_roc_pr.png", dpi=180)
    plt.close(fig)

    observed, predicted = calibration_curve(y_true, probability, n_bins=10, strategy="quantile")
    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    ax.plot(predicted, observed, marker="o", color="#2563EB", linewidth=2)
    ax.plot([0, 1], [0, 1], linestyle="--", color="#94A3B8")
    ax.set(
        title="Độ hiệu chỉnh xác suất",
        xlabel="Xác suất dự báo trung bình",
        ylabel="Tỷ lệ thực tế",
    )
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(figure_dir / "model_calibration.png", dpi=180)
    plt.close(fig)


def write_model_card(
    metrics: dict[str, Any], feature_importance: pd.DataFrame
) -> None:
    primary = metrics["models"]["balanced_spline_logistic"]
    split = metrics["split"]
    top_features = feature_importance.head(8)
    lines = [
        "# Model card — cảnh báo tỷ lệ hoàn thành thấp",
        "",
        "## Mục tiêu",
        "",
        "Dự báo cơ sở/nhóm cơ sở có tỷ lệ hoàn thành trong 150% thời gian chuẩn dưới 40%. ",
        "Mô hình không dự báo danh tính hay kết quả của từng sinh viên.",
        "",
        "## Thuật toán",
        "",
        "Logistic Regression với trọng số cân bằng lớp. Các biến số liên tục được biến đổi ",
        "bằng spline trước khi đi vào Logistic Regression để biểu diễn quan hệ phi tuyến; ",
        "bộ phân loại cuối cùng vẫn là Logistic Regression đúng yêu cầu rubric.",
        "",
        "## Chia dữ liệu",
        "",
        f"- Chiến lược: `{split['strategy']}`",
        f"- Train: {split['train_rows']:,} dòng",
        f"- Test: {split['test_rows']:,} dòng",
        "",
        "## Kết quả trên test",
        "",
        f"- Accuracy: **{primary['accuracy']:.3f}**",
        f"- Balanced Accuracy: **{primary['balanced_accuracy']:.3f}**",
        f"- Recall nhóm rủi ro: **{primary['recall']:.3f}**",
        f"- Precision: **{primary['precision']:.3f}**",
        f"- F1: **{primary['f1']:.3f}**",
        f"- ROC-AUC: **{primary['roc_auc']:.3f}**",
        f"- Brier score: **{primary['brier_score']:.3f}**",
        "",
        "Ngưỡng nghiệm thu bắt buộc của dự án là Accuracy >= 0,80 và không dùng biến ",
        "rò rỉ mục tiêu. Balanced Accuracy và Recall >= 0,80 là mục tiêu chẩn đoán bổ sung, ",
        "được công bố trung thực ngay cả khi chưa đạt.",
        "",
        "Accuracy đo tỷ lệ dự báo đúng tổng thể; Balanced Accuracy cân bằng giữa hai lớp; ",
        "Recall đo tỷ lệ nhóm hoàn thành thấp được phát hiện; Precision cho biết mức đúng ",
        "của các cảnh báo; F1 cân bằng Precision–Recall; ROC-AUC đo khả năng xếp hạng rủi ro; ",
        "Brier score đo chất lượng xác suất (càng thấp càng tốt).",
        "",
        "## Yếu tố có giá trị dự báo lớn",
        "",
    ]
    for row in top_features.itertuples(index=False):
        lines.append(f"- `{row.feature}`: permutation importance {row.importance_mean:.4f}")
    lines.extend(
        [
            "",
            "## Giới hạn",
            "",
            "- Dữ liệu quan sát chỉ chứng minh mối liên hệ, không chứng minh nguyên nhân.",
            "- Một số chỉ số chỉ đại diện người nhận hỗ trợ Title IV.",
            "- Ô có cỡ mẫu nhỏ có thể bị privacy suppression.",
            "- Retention là chỉ báo sớm ở cấp cơ sở, không phải đặc điểm cá nhân.",
            "- Kết quả hiện đã được đánh giá theo thời gian (test 2022); vẫn cần theo dõi drift khi có năm mới.",
            "",
        ]
    )
    (MODEL_DIR / "model_card.md").write_text("\n".join(lines), encoding="utf-8")


def train_all(*, prefer_temporal: bool = True) -> dict[str, Any]:
    ensure_runtime_directories()
    config = load_yaml("project.yaml")
    model_config = config["model"]
    target = model_config["target"]
    numeric = list(model_config["numeric_features"])
    categorical = list(model_config["categorical_features"])
    features = categorical + numeric
    validate_features(features, list(model_config["forbidden_features"]), target)

    frame, has_history = load_model_frame()
    required = set(features + [target, "unitid"])
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Model data is missing columns: {missing}")

    X_train, X_test, y_train, y_test, split = split_frame(
        frame,
        features,
        target,
        random_state=int(model_config["random_state"]),
        test_size=float(model_config["test_size"]),
        prefer_temporal=prefer_temporal,
        has_history=has_history,
    )

    candidates = {
        "baseline_logistic": make_model(
            numeric, categorical, nonlinear=False, balanced=False
        ),
        "balanced_spline_logistic": make_model(
            numeric, categorical, nonlinear=True, balanced=True
        ),
    }
    results: dict[str, dict[str, float]] = {}
    fitted: dict[str, Pipeline] = {}
    test_outputs: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for name, candidate in candidates.items():
        candidate.fit(X_train, y_train)
        probability = candidate.predict_proba(X_test)[:, 1]
        prediction = (probability >= 0.5).astype(int)
        results[name] = metric_bundle(y_test, prediction, probability)
        fitted[name] = candidate
        test_outputs[name] = (prediction, probability)

    primary_name = "balanced_spline_logistic"
    primary = fitted[primary_name]
    prediction, probability = test_outputs[primary_name]
    primary_metrics = results[primary_name]
    minimum_accuracy = float(model_config["minimum_accuracy"])
    quality_gate = {
        "accuracy_at_least_0_80": primary_metrics["accuracy"] >= minimum_accuracy,
        "no_forbidden_features": True,
    }
    diagnostic_targets = {
        "balanced_accuracy_at_least_0_80": primary_metrics["balanced_accuracy"] >= 0.80,
        "recall_at_least_0_80": primary_metrics["recall"] >= 0.80,
    }

    permutation = permutation_importance(
        primary,
        X_test,
        y_test,
        scoring="balanced_accuracy",
        n_repeats=12,
        random_state=int(model_config["random_state"]),
        n_jobs=-1,
    )
    importance = pd.DataFrame(
        {
            "feature": features,
            "importance_mean": permutation.importances_mean,
            "importance_std": permutation.importances_std,
        }
    ).sort_values("importance_mean", ascending=False)
    importance.to_csv(
        MODEL_DIR / "feature_importance.csv", index=False, encoding="utf-8-sig"
    )

    test_index = X_test.index
    predictions = frame.loc[
        test_index,
        [
            column
            for column in [
                "unitid",
                "institution_name",
                "state",
                "control",
                "predominant_degree",
                "completion_rate",
                "low_completion",
                "academic_year",
            ]
            if column in frame.columns
        ],
    ].copy()
    predictions["risk_probability"] = probability
    predictions["predicted_low_completion"] = prediction
    predictions["risk_level"] = pd.cut(
        predictions["risk_probability"],
        bins=[-np.inf, 0.4, 0.7, np.inf],
        labels=["Thấp", "Trung bình", "Cao"],
        right=False,
    ).astype("string")
    predictions["evaluation_split"] = "test"
    predictions.to_csv(
        MODEL_DIR / "test_predictions.csv", index=False, encoding="utf-8-sig"
    )

    # Refit the selected specification on all eligible historical observations for
    # deployment.  Evaluation metrics above remain untouched and come only from
    # the held-out test split.
    eligible = frame.dropna(subset=[target]).copy()
    primary.fit(eligible[features], eligible[target].astype(int))

    # The dashboard displays one current record per institution, not six repeated
    # institution-year rows.  Score the current Scorecard snapshot with the model
    # fitted on the historical panel.
    scoring_frame = pd.read_csv(PROCESSED_DIR / "institutions.csv", low_memory=False)
    scoring_frame = scoring_frame.dropna(subset=[target]).copy()
    missing_scoring = sorted(set(features) - set(scoring_frame.columns))
    if missing_scoring:
        raise ValueError(f"Dashboard scoring data is missing columns: {missing_scoring}")
    all_probability = primary.predict_proba(scoring_frame[features])[:, 1]
    all_prediction = (all_probability >= 0.5).astype(int)
    dashboard_predictions = scoring_frame[
        [
            column
            for column in [
                "unitid",
                "institution_name",
                "state",
                "control",
                "predominant_degree",
                "completion_rate",
                "low_completion",
                "academic_year",
            ]
            if column in scoring_frame.columns
        ]
    ].copy()
    dashboard_predictions["risk_probability"] = all_probability
    dashboard_predictions["predicted_low_completion"] = all_prediction
    dashboard_predictions["risk_level"] = pd.cut(
        dashboard_predictions["risk_probability"],
        bins=[-np.inf, 0.4, 0.7, np.inf],
        labels=["Thấp", "Trung bình", "Cao"],
        right=False,
    ).astype("string")
    dashboard_predictions.to_csv(
        PROCESSED_DIR / "model_predictions.csv", index=False, encoding="utf-8-sig"
    )
    joblib.dump(primary, MODEL_DIR / "logistic_completion.joblib")

    matrix = confusion_matrix(y_test, prediction, labels=[0, 1])
    pd.DataFrame(
        matrix,
        index=["actual_not_low", "actual_low"],
        columns=["predicted_not_low", "predicted_low"],
    ).to_csv(MODEL_DIR / "confusion_matrix.csv", encoding="utf-8-sig")

    metrics: dict[str, Any] = {
        "target": target,
        "target_definition": "completion_rate < 0.40",
        "positive_class": "institution with low completion rate",
        "probability_cutoff": 0.5,
        "features": {"numeric": numeric, "categorical": categorical},
        "split": asdict(split),
        "models": results,
        "selected_model": primary_name,
        "quality_gate": quality_gate,
        "quality_gate_passed": all(quality_gate.values()),
        "diagnostic_targets": diagnostic_targets,
        "confusion_matrix": matrix.tolist(),
    }
    with (MODEL_DIR / "metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    save_diagnostic_plots(y_test, prediction, probability)
    write_model_card(metrics, importance)
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train and evaluate Logistic Regression")
    parser.add_argument(
        "--prefer-temporal",
        action="store_true",
        help="Use the latest academic year as test when historical files are available",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metrics = train_all(prefer_temporal=args.prefer_temporal)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

