from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import spearmanr

from ttdltq.config import OUTPUT_DIR, PROCESSED_DIR, ensure_runtime_directories


FACTOR_LABELS = {
    "retention_rate": "Duy trì năm đầu",
    "pell_share": "Tỷ lệ nhận Pell Grant",
    "federal_loan_share": "Tỷ lệ vay liên bang",
    "student_faculty_ratio": "Sinh viên/giảng viên",
    "net_price": "Chi phí ròng",
    "tuition_in_state": "Học phí trong bang",
    "log_undergrad_enrollment": "Quy mô (log)",
    "instructional_spend_per_fte": "Chi giảng dạy/SV",
    "full_time_faculty_share": "Tỷ lệ GV toàn thời gian",
}


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    valid = values.notna() & weights.notna() & (weights > 0)
    if not valid.any():
        return float("nan")
    return float(np.average(values[valid], weights=weights[valid]))


def grouped_summary(frame: pd.DataFrame, group: str) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for label, part in frame.groupby(group, dropna=False):
        eligible = part["low_completion"].notna()
        weights = part["undergrad_enrollment"].clip(lower=0)
        records.append(
            {
                "dimension": group,
                "group": str(label),
                "institution_count": int(part["unitid"].nunique()),
                "undergrad_enrollment": float(weights.sum(min_count=1)),
                "weighted_completion_rate": weighted_mean(
                    part["completion_rate"], weights
                ),
                "median_completion_rate": float(part["completion_rate"].median()),
                "weighted_retention_rate": weighted_mean(part["retention_rate"], weights),
                "low_completion_institution_share": float(
                    part.loc[eligible, "low_completion"].mean()
                )
                if eligible.any()
                else float("nan"),
            }
        )
    return pd.DataFrame(records)


def correlation_table(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for factor, label in FACTOR_LABELS.items():
        if factor not in frame:
            continue
        valid = frame[[factor, "completion_rate"]].dropna()
        if len(valid) < 30:
            continue
        rho, pvalue = spearmanr(valid[factor], valid["completion_rate"])
        rows.append(
            {
                "factor": factor,
                "factor_label": label,
                "n": len(valid),
                "spearman_rho": float(rho),
                "p_value": float(pvalue),
                "absolute_rho": abs(float(rho)),
            }
        )
    return pd.DataFrame(rows).sort_values("absolute_rho", ascending=False)


def equity_summary(equity: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for label, part in equity.groupby("student_group"):
        weights = part["cohort_count"].clip(lower=0)
        rows.append(
            {
                "student_group": label,
                "institution_count": int(part["unitid"].nunique()),
                "cohort_count": float(weights.sum(min_count=1)),
                "completion_3yr_rate": weighted_mean(
                    part["completion_3yr_rate"], weights
                ),
                "withdrawal_3yr_rate": weighted_mean(
                    part["withdrawal_3yr_rate"], weights
                ),
            }
        )
    return pd.DataFrame(rows)


def disadvantage_summary(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    factors = {
        "high_pell": ("pell_share", "high"),
        "high_net_price": ("net_price", "high"),
        "high_student_faculty": ("student_faculty_ratio", "high"),
        "low_retention": ("retention_rate", "low"),
    }
    eligible = frame.dropna(
        subset=["completion_rate", "pell_share", "net_price", "student_faculty_ratio", "retention_rate"]
    ).copy()
    thresholds: list[dict[str, Any]] = []
    for flag, (column, direction) in factors.items():
        quantile = 0.75 if direction == "high" else 0.25
        cutoff = float(eligible[column].quantile(quantile))
        eligible[flag] = (
            eligible[column] >= cutoff if direction == "high" else eligible[column] <= cutoff
        ).astype(int)
        thresholds.append(
            {
                "flag": flag,
                "variable": column,
                "direction": direction,
                "quantile": quantile,
                "cutoff": cutoff,
            }
        )
    eligible["disadvantage_count"] = eligible[list(factors)].sum(axis=1)
    summary = (
        eligible.groupby("disadvantage_count")
        .agg(
            institution_count=("unitid", "nunique"),
            median_completion_rate=("completion_rate", "median"),
            mean_completion_rate=("completion_rate", "mean"),
            low_completion_share=("low_completion", "mean"),
        )
        .reset_index()
    )
    return summary, pd.DataFrame(thresholds)


def configure_style() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "figure.facecolor": "white",
        }
    )


def create_static_charts(
    institutions: pd.DataFrame,
    state: pd.DataFrame,
    correlations: pd.DataFrame,
    disadvantage: pd.DataFrame,
) -> None:
    configure_style()
    figure_dir = OUTPUT_DIR / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    state_plot = state[
        (state["institution_count"] >= 5) & state["completion_rate"].notna()
    ].copy()
    state_plot = pd.concat(
        [state_plot.nsmallest(8, "completion_rate"), state_plot.nlargest(8, "completion_rate")]
    ).drop_duplicates("state")
    state_plot = state_plot.sort_values("completion_rate")
    fig, ax = plt.subplots(figsize=(9.5, 7.2))
    colors = ["#DC2626" if value < state_plot["completion_rate"].median() else "#0F766E" for value in state_plot["completion_rate"]]
    ax.barh(state_plot["state"], state_plot["completion_rate"] * 100, color=colors)
    ax.set(
        title="Chênh lệch tỷ lệ hoàn thành giữa các bang",
        xlabel="Tỷ lệ hoàn thành có trọng số (%)",
        ylabel="Bang",
    )
    ax.bar_label(ax.containers[0], fmt="%.1f%%", padding=3, fontsize=8)
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(figure_dir / "eda_state_completion.png", dpi=180)
    plt.close(fig)

    box_data = institutions.dropna(subset=["completion_rate", "control"])
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(
        data=box_data,
        x="control",
        y="completion_rate",
        hue="control",
        palette=["#2563EB", "#0F766E", "#EA580C"],
        legend=False,
        showfliers=False,
        ax=ax,
    )
    ax.set(
        title="Phân bố tỷ lệ hoàn thành theo loại hình cơ sở",
        xlabel="Loại hình",
        ylabel="Tỷ lệ hoàn thành",
    )
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    fig.tight_layout()
    fig.savefig(figure_dir / "eda_completion_by_control.png", dpi=180)
    plt.close(fig)

    scatter = institutions.dropna(subset=["retention_rate", "completion_rate", "control"])
    if len(scatter) > 3000:
        scatter = scatter.sample(3000, random_state=42)
    fig, ax = plt.subplots(figsize=(9, 6.4))
    sns.scatterplot(
        data=scatter,
        x="retention_rate",
        y="completion_rate",
        hue="control",
        alpha=0.55,
        s=35,
        ax=ax,
    )
    sns.regplot(
        data=scatter,
        x="retention_rate",
        y="completion_rate",
        scatter=False,
        color="#111827",
        line_kws={"linewidth": 2},
        ax=ax,
    )
    ax.set(
        title="Duy trì năm đầu liên quan đến khả năng hoàn thành",
        xlabel="Tỷ lệ duy trì sau năm đầu",
        ylabel="Tỷ lệ hoàn thành",
    )
    ax.xaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    ax.legend(title="Loại hình", fontsize=8)
    fig.tight_layout()
    fig.savefig(figure_dir / "eda_retention_completion_scatter.png", dpi=180)
    plt.close(fig)

    heat = correlations.set_index("factor_label")[["spearman_rho"]]
    fig, ax = plt.subplots(figsize=(7.2, max(4.5, 0.55 * len(heat))))
    sns.heatmap(
        heat,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        vmin=-1,
        vmax=1,
        linewidths=0.5,
        cbar_kws={"label": "Spearman rho"},
        ax=ax,
    )
    ax.set(title="Mức liên hệ đơn biến với tỷ lệ hoàn thành", xlabel="", ylabel="")
    fig.tight_layout()
    fig.savefig(figure_dir / "eda_factor_correlation_heatmap.png", dpi=180)
    plt.close(fig)

    fig, ax1 = plt.subplots(figsize=(9, 5.8))
    bars = ax1.bar(
        disadvantage["disadvantage_count"],
        disadvantage["median_completion_rate"] * 100,
        color="#2563EB",
        alpha=0.85,
    )
    ax1.set(
        title="Kết quả thay đổi khi nhiều bất lợi xuất hiện cùng lúc",
        xlabel="Số yếu tố bất lợi đồng thời",
        ylabel="Trung vị tỷ lệ hoàn thành (%)",
    )
    ax1.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=8)
    ax2 = ax1.twinx()
    ax2.plot(
        disadvantage["disadvantage_count"],
        disadvantage["low_completion_share"] * 100,
        color="#DC2626",
        marker="o",
        linewidth=2.2,
    )
    ax2.set_ylabel("Tỷ lệ cơ sở thuộc nhóm hoàn thành thấp (%)", color="#DC2626")
    fig.tight_layout()
    fig.savefig(figure_dir / "eda_compound_disadvantage.png", dpi=180)
    plt.close(fig)


def build_insights(
    institutions: pd.DataFrame,
    state: pd.DataFrame,
    category: pd.DataFrame,
    correlations: pd.DataFrame,
    equity: pd.DataFrame,
    disadvantage: pd.DataFrame,
) -> list[dict[str, Any]]:
    insights: list[dict[str, Any]] = []

    eligible_states = state[(state["institution_count"] >= 5) & state["completion_rate"].notna()]
    lowest = eligible_states.nsmallest(1, "completion_rate").iloc[0]
    highest = eligible_states.nlargest(1, "completion_rate").iloc[0]
    insights.append(
        {
            "id": "INS-01",
            "research_question": "RQ1",
            "title": "Kết quả khác nhau rõ theo địa lý",
            "statement": (
                f"Trong các bang có ít nhất 5 cơ sở, tỷ lệ hoàn thành có trọng số dao động "
                f"từ {lowest.completion_rate:.1%} ở {lowest.state} đến "
                f"{highest.completion_rate:.1%} ở {highest.state}."
            ),
            "caveat": "Khác biệt mô tả có thể phản ánh cơ cấu trường và sinh viên; không phải tác động riêng của bang.",
        }
    )

    control = category[category["dimension"] == "control"].sort_values(
        "weighted_completion_rate"
    )
    low_control = control.iloc[0]
    high_control = control.iloc[-1]
    insights.append(
        {
            "id": "INS-02",
            "research_question": "RQ1/RQ3",
            "title": "Loại hình cơ sở đi cùng khoảng cách hoàn thành",
            "statement": (
                f"Tỷ lệ hoàn thành có trọng số thấp nhất ở nhóm {low_control.group} "
                f"({low_control.weighted_completion_rate:.1%}) và cao nhất ở nhóm "
                f"{high_control.group} ({high_control.weighted_completion_rate:.1%})."
            ),
            "caveat": "Không kiểm soát đầy đủ khác biệt đầu vào và sứ mệnh đào tạo giữa các nhóm trường.",
        }
    )

    strongest = correlations.iloc[0]
    direction = "cùng chiều" if strongest.spearman_rho > 0 else "ngược chiều"
    insights.append(
        {
            "id": "INS-03",
            "research_question": "RQ2/RQ3",
            "title": "Chỉ báo liên hệ mạnh nhất trong EDA",
            "statement": (
                f"{strongest.factor_label} có liên hệ {direction} mạnh nhất với tỷ lệ hoàn thành "
                f"trong các biến đã xét (Spearman rho={strongest.spearman_rho:.2f}, N={int(strongest.n):,})."
            ),
            "caveat": "Hệ số tương quan không chứng minh quan hệ nhân quả và chưa kiểm soát đồng thời các biến khác.",
        }
    )

    equity_indexed = equity.set_index("student_group")
    if {"Nhận Pell Grant", "Không nhận Pell Grant"}.issubset(equity_indexed.index):
        pell = equity_indexed.loc["Nhận Pell Grant"]
        no_pell = equity_indexed.loc["Không nhận Pell Grant"]
        gap = no_pell["completion_3yr_rate"] - pell["completion_3yr_rate"]
        insights.append(
            {
                "id": "INS-04",
                "research_question": "RQ2/RQ4",
                "title": "Khoảng cách theo nhu cầu hỗ trợ tài chính",
                "statement": (
                    f"Nhóm không nhận Pell Grant có tỷ lệ hoàn thành ba năm cao hơn nhóm nhận Pell "
                    f"khoảng {gap:.1%} trong dữ liệu có thể công bố."
                ),
                "caveat": "Pell Grant là chỉ báo nhu cầu tài chính; dữ liệu Title IV và privacy suppression giới hạn tính đại diện.",
            }
        )

    first = disadvantage.iloc[0]
    last = disadvantage.iloc[-1]
    insights.append(
        {
            "id": "INS-05",
            "research_question": "RQ5",
            "title": "Bất lợi cộng dồn đi cùng kết quả thấp hơn",
            "statement": (
                f"Trung vị hoàn thành giảm từ {first.median_completion_rate:.1%} khi có "
                f"{int(first.disadvantage_count)} bất lợi xuống {last.median_completion_rate:.1%} "
                f"khi có {int(last.disadvantage_count)} bất lợi trong định nghĩa phân vị đã khóa."
            ),
            "caveat": "Chỉ số bất lợi là quy tắc mô tả dựa trên phân vị, không phải thang đo nhân quả.",
        }
    )
    return insights


def write_insight_markdown(insights: list[dict[str, Any]]) -> None:
    lines = [
        "# Insight đã kiểm chứng từ dữ liệu",
        "",
        "Các nhận định dưới đây được tạo từ pipeline EDA. Từ **liên quan** được dùng có chủ ý; ",
        "dữ liệu quan sát không đủ để khẳng định quan hệ nhân quả.",
        "",
    ]
    for insight in insights:
        lines.extend(
            [
                f"## {insight['id']} — {insight['title']}",
                "",
                insight["statement"],
                "",
                f"**Giới hạn:** {insight['caveat']}",
                "",
            ]
        )
    (OUTPUT_DIR / "eda" / "insights.md").write_text("\n".join(lines), encoding="utf-8")


def run_eda() -> dict[str, Any]:
    ensure_runtime_directories()
    institutions = pd.read_csv(PROCESSED_DIR / "institutions.csv", low_memory=False)
    state = pd.read_csv(PROCESSED_DIR / "state_summary.csv")
    equity_long = pd.read_csv(PROCESSED_DIR / "equity_long.csv", low_memory=False)

    summaries = pd.concat(
        [
            grouped_summary(institutions, "control"),
            grouped_summary(institutions, "locale_group"),
            grouped_summary(institutions, "distance_only"),
            grouped_summary(institutions, "predominant_degree"),
        ],
        ignore_index=True,
    )
    correlations = correlation_table(institutions)
    equity = equity_summary(equity_long)
    disadvantage, thresholds = disadvantage_summary(institutions)

    out = OUTPUT_DIR / "eda"
    out.mkdir(parents=True, exist_ok=True)
    summaries.to_csv(out / "category_summary.csv", index=False, encoding="utf-8-sig")
    correlations.to_csv(out / "factor_correlations.csv", index=False, encoding="utf-8-sig")
    equity.to_csv(out / "equity_summary.csv", index=False, encoding="utf-8-sig")
    disadvantage.to_csv(out / "disadvantage_summary.csv", index=False, encoding="utf-8-sig")
    thresholds.to_csv(out / "disadvantage_thresholds.csv", index=False, encoding="utf-8-sig")

    create_static_charts(institutions, state, correlations, disadvantage)
    insights = build_insights(
        institutions, state, summaries, correlations, equity, disadvantage
    )
    with (out / "insights.json").open("w", encoding="utf-8") as handle:
        json.dump(insights, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    write_insight_markdown(insights)
    return {
        "category_rows": len(summaries),
        "correlation_rows": len(correlations),
        "equity_rows": len(equity),
        "disadvantage_rows": len(disadvantage),
        "insight_count": len(insights),
    }


def main() -> None:
    print(json.dumps(run_eda(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

