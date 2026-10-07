from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
MODEL = ROOT / "models"
EDA = ROOT / "outputs" / "eda"

COLORS = {
    "primary": "#0F766E",
    "blue": "#2563EB",
    "risk": "#DC2626",
    "warning": "#F59E0B",
    "safe": "#16A34A",
}

FACTOR_META = {
    "retention_rate": (
        "Tiếp tục học sau năm nhất",
        "Tỷ lệ sinh viên quay lại học tiếp sau năm đầu tiên.",
        "percent",
    ),
    "student_faculty_ratio": (
        "Số sinh viên trên một giảng viên",
        "Con số càng cao nghĩa là một giảng viên phải phục vụ nhiều sinh viên hơn.",
        "ratio",
    ),
    "pell_share": (
        "Tỷ lệ sinh viên nhận Pell Grant",
        "Đo bằng tỷ lệ nhận Pell Grant — hỗ trợ dành chủ yếu cho người có hoàn cảnh khó khăn.",
        "percent",
    ),
    "federal_loan_share": (
        "Tỷ lệ sử dụng khoản vay liên bang",
        "Tỷ lệ sinh viên sử dụng khoản vay giáo dục liên bang Hoa Kỳ.",
        "percent",
    ),
    "net_price": (
        "Chi phí thực trả sau hỗ trợ",
        "Chi phí trung bình còn lại sau khi trừ học bổng và hỗ trợ.",
        "usd",
    ),
    "tuition_in_state": (
        "Học phí công bố",
        "Học phí dành cho người học trong bang, chưa trừ hỗ trợ.",
        "usd",
    ),
    "undergrad_enrollment": (
        "Quy mô sinh viên",
        "Tổng số sinh viên đại học trong kỳ báo cáo.",
        "count",
    ),
    "full_time_faculty_share": (
        "Giảng viên toàn thời gian",
        "Tỷ lệ đội ngũ giảng dạy làm việc toàn thời gian.",
        "percent",
    ),
}

MODEL_LABELS = {
    "retention_rate": "Tiếp tục học sau năm nhất",
    "student_faculty_ratio": "Sinh viên / giảng viên",
    "pell_share": "Tỷ lệ nhận Pell Grant",
    "federal_loan_share": "Tỷ lệ sử dụng khoản vay liên bang",
    "net_price": "Chi phí thực trả",
    "tuition_in_state": "Học phí",
    "log_undergrad_enrollment": "Quy mô sinh viên",
    "predominant_degree": "Bậc đào tạo",
    "control": "Loại hình quản lý",
    "locale_group": "Khu vực địa lý",
    "distance_only": "Học hoàn toàn trực tuyến",
    "admission_rate": "Mức độ tuyển chọn",
    "instructional_spend_per_fte": "Chi cho giảng dạy / sinh viên",
    "average_faculty_salary": "Mức lương giảng viên",
    "full_time_faculty_share": "Giảng viên toàn thời gian",
    "age_25_plus_share": "Người học từ 25 tuổi",
}

RISK_PROFILE_FACTORS = {
    "retention_rate": (
        "Tiếp tục học sau năm nhất thấp",
        "low",
        "Tăng cố vấn, hỗ trợ học tập và theo dõi việc quay lại sau năm nhất",
        "percent",
    ),
    "student_faculty_ratio": (
        "Nhiều sinh viên trên một giảng viên",
        "high",
        "Rà soát khả năng tiếp cận giảng viên và lớp hỗ trợ",
        "ratio",
    ),
    "instructional_spend_per_fte": (
        "Chi cho giảng dạy trên sinh viên thấp",
        "low",
        "Rà soát phân bổ nguồn lực trực tiếp cho giảng dạy",
        "usd",
    ),
    "full_time_faculty_share": (
        "Tỷ lệ giảng viên toàn thời gian thấp",
        "low",
        "Rà soát mức độ sẵn có và tính liên tục của đội ngũ giảng dạy",
        "percent",
    ),
    "pell_share": (
        "Tỷ lệ sinh viên nhận Pell Grant cao",
        "high",
        "Tăng tư vấn học bổng, hỗ trợ khẩn cấp và kết nối dịch vụ sinh viên",
        "percent",
    ),
    "federal_loan_share": (
        "Tỷ lệ sử dụng khoản vay liên bang cao",
        "high",
        "Tăng tư vấn tài chính và theo dõi áp lực chi phí học tập",
        "percent",
    ),
    "net_price": (
        "Chi phí thực trả cao",
        "high",
        "Rà soát học bổng và mức hỗ trợ theo nhu cầu tài chính",
        "usd",
    ),
}

DEGREE_LABELS = {
    "Associate": "Cao đẳng 2 năm (Associate)",
    "Bachelor": "Cử nhân (Bachelor)",
    "Graduate": "Sau đại học (Graduate)",
}

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
    "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
    "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "PR": "Puerto Rico",
    "GU": "Guam", "VI": "U.S. Virgin Islands", "AS": "American Samoa",
    "MP": "Northern Mariana Islands", "FM": "Micronesia", "MH": "Marshall Islands",
    "PW": "Palau",
}


st.set_page_config(
    page_title="Các yếu tố liên quan đến kết quả học tập",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.1rem; padding-bottom: 2rem;}
      [data-testid="stMetric"] {background:white;border:1px solid #e2e8f0;
        border-radius:14px;padding:14px 16px;box-shadow:0 4px 16px rgba(15,23,42,.05)}
      .note {background:#eff6ff;border-left:5px solid #2563eb;border-radius:9px;
        padding:.8rem 1rem;margin:.5rem 0 1rem}
      .finding {background:#f0fdfa;border-left:5px solid #0f766e;border-radius:9px;
        padding:1rem 1.1rem;min-height:128px;overflow-wrap:anywhere;line-height:1.55}
      .definition {background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
        padding:.75rem 1rem;color:#334155}
      h1,h2,h3 {color:#0f172a}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, Any]:
    files = {
        "institutions": DATA / "institutions.csv",
        "predictions": DATA / "model_predictions.csv",
        "equity": EDA / "equity_summary.csv",
        "disadvantage": EDA / "disadvantage_summary.csv",
        "importance": MODEL / "feature_importance.csv",
        "metrics": MODEL / "metrics.json",
        "insights": EDA / "insights.json",
    }
    missing = [str(path) for path in files.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Thiếu đầu ra pipeline:\n" + "\n".join(missing))
    result: dict[str, Any] = {}
    for name, path in files.items():
        result[name] = (
            pd.read_csv(path, low_memory=False)
            if path.suffix == ".csv"
            else json.loads(path.read_text(encoding="utf-8"))
        )
    return result


@st.cache_resource(show_spinner=False)
def load_prediction_model() -> Any:
    model_path = MODEL / "logistic_completion.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Thiếu mô hình dự báo: {model_path}")
    return joblib.load(model_path)


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    valid = values.notna() & weights.notna() & (weights > 0)
    return float(np.average(values[valid], weights=weights[valid])) if valid.any() else np.nan


def pct(value: float) -> str:
    return "—" if pd.isna(value) else f"{value:.1%}"


def readable_value(value: float, unit: str) -> str:
    if unit == "percent":
        return f"{value:.0%}"
    if unit == "usd":
        return f"${value:,.0f}"
    if unit == "count":
        return f"{value:,.0f} SV"
    return f"{value:.1f}"


def global_filters(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    choices = [
        ("state", "Bang/khu vực"),
        ("control", "Loại hình quản lý"),
        ("predominant_degree", "Bậc đào tạo chính"),
        ("locale_group", "Đô thị–nông thôn"),
        ("distance_only", "Học trực tuyến"),
    ]
    st.sidebar.caption("Các bộ lọc tác động đồng thời đến toàn bộ trang.")
    for column, label in choices:
        options = sorted(frame[column].dropna().astype(str).unique())
        selected = st.sidebar.multiselect(label, options)
        if selected:
            result = result[result[column].astype(str).isin(selected)]
    return result


def state_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    valid = frame[frame["state"].astype("string").str.fullmatch(r"[A-Z]{2}").fillna(False)]
    for state, part in valid.groupby("state"):
        weights = part["undergrad_enrollment"].clip(lower=0)
        rows.append(
            {
                "state": state,
                "state_name": STATE_NAMES.get(state, state),
                "group_count": part["unitid"].nunique(),
                "students": weights.sum(min_count=1),
                "completion": weighted_mean(part["completion_rate"], weights),
                "retention": weighted_mean(part["retention_rate"], weights),
            }
        )
    return pd.DataFrame(rows)


def state_context(frame: pd.DataFrame, state: str) -> dict[str, float]:
    part = frame[frame["state"] == state].copy()
    weights = part["undergrad_enrollment"].clip(lower=0)
    return {
        "retention": weighted_mean(part["retention_rate"], weights),
        "full_time_faculty": part["full_time_faculty_share"].median(),
        "pell": weighted_mean(part["pell_share"], weights),
        "bachelor_share": (part["predominant_degree"] == "Bachelor").mean(),
        "certificate_share": (part["predominant_degree"] == "Chứng chỉ").mean(),
        "rural_town_share": part["locale_group"].isin(["Nông thôn", "Thị trấn"]).mean(),
    }


def factor_levels(frame: pd.DataFrame, factor: str) -> pd.DataFrame:
    valid = frame[[factor, "completion_rate", "low_completion"]].dropna(
        subset=[factor, "completion_rate"]
    ).copy()
    if len(valid) < 40 or valid[factor].nunique() < 4:
        return pd.DataFrame()
    labels = ["Mức 1 · thấp nhất", "Mức 2", "Mức 3", "Mức 4 · cao nhất"]
    valid["level"] = pd.qcut(valid[factor], 4, labels=labels, duplicates="drop")
    summary = (
        valid.groupby("level", observed=True)
        .agg(
            factor_value=(factor, "median"),
            completion=("completion_rate", "median"),
            low_share=("low_completion", "mean"),
            group_count=("completion_rate", "size"),
        )
        .reset_index()
    )
    unit = FACTOR_META[factor][2]
    summary["display"] = summary["level"].astype(str) + "<br>" + summary["factor_value"].map(
        lambda value: readable_value(value, unit)
    )
    return summary


def correlations(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for factor, (label, _, _) in FACTOR_META.items():
        valid = frame[[factor, "completion_rate"]].dropna()
        if len(valid) < 30:
            continue
        rho = valid[factor].corr(valid["completion_rate"], method="spearman")
        rows.append(
            {
                "factor": label,
                "rho": rho,
                "sample": len(valid),
                "meaning": "Đi cùng kết quả cao hơn" if rho >= 0 else "Đi cùng kết quả thấp hơn",
            }
        )
    return pd.DataFrame(rows).sort_values("rho")


def high_risk_profiles(
    predictions: pd.DataFrame,
    reference: pd.DataFrame,
    model: Any,
) -> pd.DataFrame:
    """Summarize high-risk segments with counterfactual model diagnostics."""
    group_columns = ["predominant_degree", "control", "locale_group"]
    factor_columns = list(RISK_PROFILE_FACTORS)
    model_features = list(model.feature_names_in_)
    required = group_columns + factor_columns + [
        "unitid",
        "risk_probability",
        "risk_level",
        "completion_rate",
    ]
    available = predictions.dropna(subset=group_columns + ["risk_probability"])
    if available.empty or any(column not in available for column in required + model_features):
        return pd.DataFrame()

    minimum_size = 20 if len(available) >= 500 else max(5, round(len(available) * 0.03))
    aggregations: dict[str, tuple[str, Any]] = {
        "group_count": ("unitid", "nunique"),
        "average_risk": ("risk_probability", "mean"),
        "high_risk_share": ("risk_level", lambda values: (values == "Cao").mean()),
        "median_completion": ("completion_rate", "median"),
    }
    aggregations.update({factor: (factor, "median") for factor in factor_columns})
    summary = (
        available.groupby(group_columns, dropna=False)
        .agg(**aggregations)
        .reset_index()
        .query("group_count >= @minimum_size and average_risk >= 0.5")
        .sort_values(["average_risk", "group_count"], ascending=[False, False])
        .head(8)
    )
    if summary.empty:
        return summary

    benchmarks: dict[str, float] = {}
    for factor in factor_columns:
        values = reference[factor].dropna()
        benchmarks[factor] = float(values.median())

    def format_comparison(factor: str, group_value: float, baseline: float) -> str:
        unit = RISK_PROFILE_FACTORS[factor][3]
        if unit == "percent":
            return f"{group_value:.0%} so với mức chung {baseline:.0%}"
        if unit == "usd":
            return f"${group_value:,.0f} so với mức chung ${baseline:,.0f}"
        return f"{group_value:.1f} so với mức chung {baseline:.1f}"

    rows = []
    for row in summary.itertuples(index=False):
        segment = available[
            (available["predominant_degree"] == row.predominant_degree)
            & (available["control"] == row.control)
            & (available["locale_group"] == row.locale_group)
        ]
        conditions = []
        for factor, (label, direction, action, _) in RISK_PROFILE_FACTORS.items():
            group_value = getattr(row, factor)
            baseline = benchmarks[factor]
            if pd.isna(group_value) or pd.isna(baseline):
                continue
            has_expected_direction = (
                group_value < baseline if direction == "low" else group_value > baseline
            )
            if not has_expected_direction:
                continue
            counterfactual = segment[model_features].copy()
            counterfactual[factor] = baseline
            counterfactual_risk = float(model.predict_proba(counterfactual)[:, 1].mean())
            prediction_contribution = float(row.average_risk - counterfactual_risk)
            if prediction_contribution > 0.002:
                conditions.append(
                    (
                        prediction_contribution,
                        f"{label} ({format_comparison(factor, group_value, baseline)}; "
                        f"chênh dự báo +{prediction_contribution:.1%})",
                        action,
                    )
                )
        conditions.sort(reverse=True, key=lambda item: item[0])
        selected_conditions = conditions[:3]
        actions = list(dict.fromkeys(item[2] for item in selected_conditions))
        rows.append(
            {
                "Nhóm": (
                    f"{DEGREE_LABELS.get(row.predominant_degree, row.predominant_degree)} · "
                    f"{row.control} · {row.locale_group}"
                ),
                "Số quan sát": int(row.group_count),
                "Rủi ro trung bình": row.average_risk,
                "Tỷ trọng rủi ro cao": row.high_risk_share,
                "Hoàn thành điển hình": row.median_completion,
                "Yếu tố cần kiểm tra": " | ".join(item[1] for item in selected_conditions)
                or "Chưa có yếu tố can thiệp đơn lẻ vừa đúng chiều vừa đóng góp rõ vào dự báo",
                "Hướng cải thiện nên xem xét": " | ".join(actions)
                or "Phân tích sâu thêm trước khi đề xuất can thiệp",
            }
        )
    return pd.DataFrame(rows)


def finding(title: str, result: str, meaning: str) -> None:
    st.markdown(
        f'<div class="finding"><b>{title}</b><br><span style="font-size:1.05rem">'
        f"{result}</span><br><small>{meaning}</small></div>",
        unsafe_allow_html=True,
    )


def glossary() -> None:
    with st.expander("Giải thích nhanh các thuật ngữ"):
        st.markdown(
            """
            - **Hoàn thành chương trình:** tốt nghiệp trong tối đa 150% thời gian chuẩn;
              chương trình 4 năm được theo dõi trong tối đa 6 năm.
            - **Tiếp tục học sau năm nhất:** quay lại học năm tiếp theo thay vì dừng học.
            - **Tỷ lệ nhận Pell Grant:** tỷ lệ sinh viên nhận khoản hỗ trợ chủ yếu dành cho
              người có nhu cầu tài chính; đây là chỉ báo hoàn cảnh, không phải số tiền hỗ trợ.
            - **Tỷ lệ sử dụng khoản vay liên bang:** tỷ lệ sinh viên sử dụng khoản vay giáo
              dục liên bang; không phải số tiền vay hoặc dư nợ trung bình.
            - **Chi phí thực trả:** phần chi phí còn lại sau học bổng và hỗ trợ.
            - **Nhóm kết quả thấp:** tỷ lệ hoàn thành dưới 40%, dùng làm nhãn cho mô hình.
            """
        )


def overview_page(data: dict[str, Any], frame: pd.DataFrame) -> None:
    st.header("1 · Kết quả duy trì và hoàn thành khác nhau ở đâu?")
    st.markdown(
        '<div class="note"><b>RQ1:</b> Tỷ lệ hoàn thành chương trình, duy trì sau năm nhất '
        'và rút khỏi chương trình khác nhau như thế nào giữa các bang, loại hình quản lý, '
        'bậc đào tạo chính, địa bàn và hình thức đào tạo từ xa? Bản đồ và các phép so sánh '
        'trên trang này mô tả khoảng cách; trang 2 mới phân tích các yếu tố liên quan.</div>',
        unsafe_allow_html=True,
    )
    weights = frame["undergrad_enrollment"].clip(lower=0)
    eligible = frame["low_completion"].notna()
    columns = st.columns(4)
    columns[0].metric("Hoàn thành chương trình", pct(weighted_mean(frame["completion_rate"], weights)))
    columns[1].metric("Tiếp tục học sau năm nhất", pct(weighted_mean(frame["retention_rate"], weights)))
    columns[2].metric("Rút khỏi chương trình", pct(weighted_mean(frame["withdrawal_3yr_rate"], weights)))
    columns[3].metric("Nhóm kết quả dưới 40%", pct(frame.loc[eligible, "low_completion"].mean()))

    states = state_summary(frame)
    comparison_pool = states[(states["group_count"] >= 5) & states["completion"].notna()]
    if comparison_pool.empty:
        comparison_pool = states[states["completion"].notna()]
    lowest = comparison_pool.nsmallest(1, "completion").iloc[0]
    highest = comparison_pool.nlargest(1, "completion").iloc[0]
    geographic_gap = highest.completion - lowest.completion
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Bản đồ tỷ lệ hoàn thành theo bang")
        chart = px.choropleth(
            states,
            locations="state",
            locationmode="USA-states",
            scope="usa",
            color="completion",
            hover_name="state_name",
            hover_data={"completion": ":.1%", "retention": ":.1%", "students": ":,.0f", "state": False, "state_name": False},
            color_continuous_scale="RdYlGn",
            range_color=(0.3, 0.8),
            labels={"completion": "Hoàn thành"},
        )
        chart.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(chart, width="stretch")
        st.caption(
            "Màu xanh biểu thị tỷ lệ hoàn thành cao hơn, màu đỏ biểu thị tỷ lệ thấp hơn. "
            "Bộ lọc bên trái cho phép đối chiếu lại bản đồ theo loại hình và bậc đào tạo."
        )
    with right:
        st.subheader("Chênh lệch kết quả giữa các bang")
        ranked = pd.concat([
            comparison_pool.nsmallest(6, "completion"),
            comparison_pool.nlargest(6, "completion"),
        ])
        ranked = ranked.drop_duplicates("state").sort_values("completion")
        chart = px.bar(
            ranked,
            x="completion",
            y="state_name",
            orientation="h",
            color="completion",
            color_continuous_scale="RdYlGn",
            text_auto=".1%",
            labels={"completion": "Tỷ lệ hoàn thành", "state_name": "Bang"},
        )
        chart.update_layout(height=455, coloraxis_showscale=False, margin=dict(l=5, r=10, t=10, b=45))
        chart.update_yaxes(automargin=True)
        st.plotly_chart(chart, width="stretch")
        st.caption(
            f"Trong các bang có ít nhất 5 nhóm cơ sở, {lowest.state_name} đạt "
            f"{lowest.completion:.1%} và {highest.state_name} đạt {highest.completion:.1%}; "
            f"chênh {geographic_gap:.1%}."
        )

    st.subheader(f"Điều kiện nào đi cùng chênh lệch giữa {lowest.state_name} và {highest.state_name}?")
    low_context = state_context(frame, lowest.state)
    high_context = state_context(frame, highest.state)
    context_rows = [
        ("Tiếp tục học sau năm nhất", low_context["retention"], high_context["retention"]),
        ("Giảng viên toàn thời gian", low_context["full_time_faculty"], high_context["full_time_faculty"]),
        ("Sinh viên cần hỗ trợ tài chính", low_context["pell"], high_context["pell"]),
        ("Cơ sở đào tạo cử nhân", low_context["bachelor_share"], high_context["bachelor_share"]),
        ("Cơ sở đào tạo chứng chỉ", low_context["certificate_share"], high_context["certificate_share"]),
        ("Cơ sở ở nông thôn/thị trấn", low_context["rural_town_share"], high_context["rural_town_share"]),
    ]
    context_table = pd.DataFrame(
        {
            "Điều kiện": [row[0] for row in context_rows],
            lowest.state_name: [f"{row[1]:.1%}" for row in context_rows],
            highest.state_name: [f"{row[2]:.1%}" for row in context_rows],
            "Chênh lệch": [f"{row[2] - row[1]:+.1%}" for row in context_rows],
        }
    )
    st.dataframe(context_table, hide_index=True, width="stretch", height=248)
    retention_difference = high_context["retention"] - low_context["retention"]
    faculty_difference = high_context["full_time_faculty"] - low_context["full_time_faculty"]
    bachelor_difference = high_context["bachelor_share"] - low_context["bachelor_share"]
    remote_difference = high_context["rural_town_share"] - low_context["rural_town_share"]
    st.markdown(
        f'<div class="note"><b>Giải thích chênh lệch:</b> {highest.state_name} có tỷ lệ '
        f'tiếp tục học cao hơn <b>{retention_difference:+.1%}</b>, tỷ lệ giảng viên toàn thời '
        f'gian cao hơn <b>{faculty_difference:+.1%}</b> và tỷ trọng cơ sở đào tạo cử nhân cao '
        f'hơn <b>{bachelor_difference:+.1%}</b>. Đồng thời, tỷ trọng cơ sở ở nông thôn/thị '
        f'trấn của bang này chênh <b>{remote_difference:+.1%}</b> so với {lowest.state_name}. '
        f'Kết quả vì vậy phù hợp hơn với khác biệt về khả năng duy trì học tập, đội ngũ giảng '
        f'dạy và cơ cấu chương trình hơn là một cách giải thích đơn giản bằng mức độ hẻo lánh.</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Kết quả theo khu vực sống")
        locale = (
            frame.groupby("locale_group")
            .agg(completion=("completion_rate", "median"), group_count=("unitid", "nunique"))
            .reset_index()
            .query("group_count >= 10")
            .sort_values("completion")
        )
        chart = px.bar(
            locale,
            x="locale_group",
            y="completion",
            color="completion",
            text_auto=".1%",
            color_continuous_scale="RdYlGn",
            labels={"locale_group": "Khu vực", "completion": "Tỷ lệ hoàn thành điển hình"},
        )
        chart.update_yaxes(tickformat=".0%")
        chart.update_layout(height=410, coloraxis_showscale=False)
        st.plotly_chart(chart, width="stretch")
    with right:
        st.subheader("Cơ cấu kết quả theo bậc đào tạo")
        structure = (
            frame.dropna(subset=["low_completion"])
            .groupby(["predominant_degree", "risk_label"])["unitid"]
            .nunique()
            .rename("count")
            .reset_index()
        )
        structure["share"] = structure["count"] / structure.groupby("predominant_degree")["count"].transform("sum")
        chart = px.bar(
            structure,
            x="predominant_degree",
            y="share",
            color="risk_label",
            barmode="stack",
            text_auto=".1%",
            color_discrete_map={"Tỷ lệ hoàn thành thấp": COLORS["risk"], "Không thuộc nhóm thấp": COLORS["safe"]},
            labels={"predominant_degree": "Bậc đào tạo", "share": "Tỷ trọng", "risk_label": ""},
        )
        chart.update_yaxes(tickformat=".0%")
        chart.update_layout(
            height=430,
            legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="center", x=0.5),
            margin=dict(l=10, r=10, t=70, b=65),
        )
        chart.update_xaxes(automargin=True)
        st.plotly_chart(chart, width="stretch")

    finding(
        "Kết luận về khác biệt địa lý",
        f"{highest.state_name} cao hơn {lowest.state_name} {geographic_gap:.1%} về tỷ lệ hoàn thành.",
        "Chênh lệch địa lý đi cùng khác biệt về duy trì học tập, đội ngũ giảng dạy và cơ cấu chương trình.",
    )


def factor_page(data: dict[str, Any], frame: pd.DataFrame) -> None:
    st.header("2 · Tài chính và nguồn lực liên quan thế nào với kết quả?")

    retention = factor_levels(frame, "retention_rate")
    ratio = factor_levels(frame, "student_faculty_ratio")
    retention_gap = retention.iloc[-1].completion - retention.iloc[0].completion
    ratio_gap = ratio.iloc[-1].completion - ratio.iloc[0].completion
    equity_index = data["equity"].set_index("student_group")
    pell_gap = equity_index.loc["Không nhận Pell Grant", "completion_3yr_rate"] - equity_index.loc["Nhận Pell Grant", "completion_3yr_rate"]
    first_generation_gap = equity_index.loc["Không phải thế hệ đầu", "completion_3yr_rate"] - equity_index.loc["Thế hệ đầu học đại học", "completion_3yr_rate"]
    disadvantage = data["disadvantage"]
    peak_disadvantage = disadvantage.nlargest(1, "low_completion_share").iloc[0]

    st.markdown(
        f'<div class="note"><b>RQ2–RQ5 · Kết luận điều hành:</b> Trong phạm vi bộ lọc hiện tại, '
        f'khả năng tiếp tục học sau năm nhất là tín hiệu phân tách kết quả rõ nhất: nhóm '
        f'cao nhất có trung vị hoàn thành chênh <b>{abs(retention_gap) * 100:.1f} điểm phần '
        f'trăm</b> so với nhóm thấp nhất. Khoảng cách cũng đi cùng khả năng tiếp cận giảng '
        f'viên và hoàn cảnh tài chính, vì vậy bộ phận quản lý học vụ nên ưu tiên theo dõi '
        f'chuyển tiếp sau năm nhất, rồi phân tầng theo nguồn lực và nhu cầu hỗ trợ thay vì '
        f'dựa vào một chỉ số riêng lẻ. Đây là bằng chứng liên hệ, không phải kết luận nhân quả.</div>',
        unsafe_allow_html=True,
    )

    first_row = st.columns(2)
    with first_row[0]:
        finding(
            "1. Tiếp tục học sau năm nhất",
            f"Chênh {retention_gap * 100:+.1f} điểm phần trăm",
            "Tín hiệu sàng lọc nổi bật; ưu tiên kiểm tra nhóm chuyển tiếp thấp sau năm đầu.",
        )
    with first_row[1]:
        finding(
            "2. Sinh viên trên giảng viên",
            f"Chênh {ratio_gap * 100:+.1f} điểm phần trăm",
            "Áp lực tiếp cận giảng viên là dấu hiệu cần đối chiếu trong cùng loại hình đào tạo.",
        )
    st.write("")
    second_row = st.columns(2)
    with second_row[0]:
        finding(
            "3. Khó khăn tài chính",
            f"Chênh {pell_gap * 100:.1f} điểm phần trăm",
            "Khoảng cách Pell gợi ý nhu cầu phối hợp hỗ trợ tài chính với cố vấn học tập.",
        )
    with second_row[1]:
        finding(
            "4. Bất lợi cùng xuất hiện",
            f"Đỉnh rủi ro ở {int(peak_disadvantage.disadvantage_count)} điều kiện",
            f"Tỷ trọng dưới 40% đạt {peak_disadvantage.low_completion_share:.1%}; quan hệ không tăng tuyến tính.",
        )

    st.subheader("Đi sâu vào một yếu tố")
    selected = st.selectbox("Chọn yếu tố", list(FACTOR_META), format_func=lambda key: FACTOR_META[key][0])
    label, definition, _ = FACTOR_META[selected]
    st.caption(definition)
    levels = factor_levels(frame, selected)
    if levels.empty:
        st.warning("Bộ lọc hiện tại không còn đủ dữ liệu để chia thành bốn mức.")
    else:
        chart = px.line(
            levels,
            x="display",
            y="completion",
            markers=True,
            text="completion",
            hover_data={"group_count": ":,", "low_share": ":.1%"},
            labels={"display": label, "completion": "Tỷ lệ hoàn thành điển hình", "group_count": "Số nhóm dữ liệu", "low_share": "Tỷ trọng dưới 40%"},
        )
        chart.update_traces(line=dict(color=COLORS["primary"], width=4), marker=dict(size=12), texttemplate="%{text:.1%}", textposition="top center")
        chart.update_yaxes(tickformat=".0%")
        chart.update_layout(height=450)
        st.plotly_chart(chart, width="stretch")
        gap = levels.iloc[-1].completion - levels.iloc[0].completion
        low_level = levels.iloc[0]
        high_level = levels.iloc[-1]
        if selected == "retention_rate":
            dynamic_insight = (
                f"Trung vị hoàn thành tăng liên tục từ {low_level.completion:.1%} ở mức "
                f"retention thấp nhất lên {high_level.completion:.1%} ở mức cao nhất, chênh "
                f"{abs(gap) * 100:.1f} điểm phần trăm. Mẫu hình này cho thấy chuyển tiếp sau "
                f"năm nhất là một mốc theo dõi thực hành quan trọng: nên kiểm tra sớm khó khăn "
                f"học thuật, tài chính và khả năng hòa nhập ở nhóm retention thấp. Dữ liệu "
                f"không chứng minh riêng retention tạo ra mức cải thiện đó."
            )
        elif selected == "student_faculty_ratio":
            dynamic_insight = (
                f"Khi tỷ lệ sinh viên/giảng viên chuyển từ mức thấp nhất sang cao nhất, trung "
                f"vị hoàn thành {'tăng' if gap >= 0 else 'giảm'} {abs(gap) * 100:.1f} điểm "
                f"phần trăm. Đây là dấu hiệu cần rà soát khả năng tiếp cận giảng viên và lớp "
                f"hỗ trợ trong cùng loại hình, không phải bằng chứng sĩ số trực tiếp gây ra kết quả."
            )
        else:
            dynamic_insight = (
                f"Qua bốn mức của {label.lower()}, trung vị hoàn thành đi từ "
                f"{low_level.completion:.1%} đến {high_level.completion:.1%}, "
                f"{'tăng' if gap >= 0 else 'giảm'} {abs(gap) * 100:.1f} điểm phần trăm. "
                f"Khoảng cách này giúp xác định nhóm cần drill-down theo loại hình và bậc đào "
                f"tạo; chưa đủ để kết luận thay đổi riêng yếu tố này sẽ làm kết quả thay đổi tương ứng."
            )
        st.success(
            dynamic_insight
        )

    left, right = st.columns([1.05, 0.95])
    with left:
        st.subheader("Yếu tố nào liên quan mạnh hơn?")
        corr = correlations(frame)
        chart = px.scatter(
            corr,
            x="rho",
            y="factor",
            size="sample",
            color="meaning",
            text="rho",
            color_discrete_map={"Đi cùng kết quả cao hơn": COLORS["primary"], "Đi cùng kết quả thấp hơn": COLORS["risk"]},
            labels={"rho": "Mức liên quan (-1 đến +1)", "factor": "Yếu tố", "meaning": ""},
        )
        chart.update_traces(texttemplate="%{text:.2f}", textposition="middle right", marker=dict(sizemin=9))
        chart.update_xaxes(range=[-0.7, 0.7], zeroline=True, zerolinewidth=2)
        chart.update_layout(
            height=520,
            legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="center", x=0.5),
            margin=dict(l=10, r=15, t=75, b=45),
        )
        chart.update_yaxes(automargin=True)
        st.plotly_chart(chart, width="stretch")
        strongest_positive = corr.nlargest(1, "rho").iloc[0]
        negative_factors = corr[corr["rho"] < 0]
        strongest_negative = (
            negative_factors.nsmallest(1, "rho").iloc[0]
            if not negative_factors.empty
            else corr.nsmallest(1, "rho").iloc[0]
        )
        st.caption(
            f"Trong dữ liệu đang lọc, {strongest_positive['factor']} có liên hệ dương mạnh "
            f"nhất (rho={strongest_positive['rho']:.2f}); {strongest_negative['factor']} có "
            f"liên hệ thấp nhất (rho={strongest_negative['rho']:.2f}). Các biến học phí/chi "
            f"phí có thể đồng thời phản ánh loại trường, bậc đào tạo và mức tuyển chọn, nên "
            f"không được diễn giải rằng tăng chi phí sẽ cải thiện kết quả. Hành động phù hợp "
            f"là đối chiếu các yếu tố trong cùng nhóm cơ sở trước khi đề xuất hỗ trợ."
        )
    with right:
        st.subheader("Khu vực và loại hình kết hợp")
        matrix = frame.groupby(["locale_group", "control"])["completion_rate"].median().unstack()
        chart = go.Figure(
            go.Heatmap(
                z=matrix.to_numpy(),
                x=matrix.columns,
                y=matrix.index,
                colorscale="RdYlGn",
                zmin=0.25,
                zmax=0.8,
                text=np.vectorize(lambda value: "—" if pd.isna(value) else f"{value:.0%}")(matrix.to_numpy()),
                texttemplate="%{text}",
                hovertemplate="%{y}<br>%{x}<br>Hoàn thành: %{z:.1%}<extra></extra>",
            )
        )
        chart.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(chart, width="stretch")
        matrix_evidence = (
            frame[frame["locale_group"].ne("Không xác định")]
            .groupby(["locale_group", "control"], dropna=False)
            .agg(
                completion=("completion_rate", "median"),
                group_count=("unitid", "nunique"),
            )
            .reset_index()
            .dropna(subset=["completion"])
            .query("group_count >= 10")
        )
        if not matrix_evidence.empty:
            matrix_high = matrix_evidence.nlargest(1, "completion").iloc[0]
            matrix_low = matrix_evidence.nsmallest(1, "completion").iloc[0]
            st.caption(
                f"Trong các ô đã xác định địa bàn và có ít nhất 10 cơ sở, nhóm "
                f"{matrix_high['control']} · {str(matrix_high['locale_group']).lower()} có "
                f"trung vị hoàn thành cao nhất ({matrix_high['completion']:.1%}, "
                f"N={int(matrix_high['group_count'])}); nhóm {matrix_low['control']} · "
                f"{str(matrix_low['locale_group']).lower()} thấp nhất "
                f"({matrix_low['completion']:.1%}, N={int(matrix_low['group_count'])}). "
                f"Đây là điểm khởi đầu để drill-down cơ cấu chương trình và nguồn lực, không "
                f"phải bằng chứng loại hình hay địa bàn tự gây ra chênh lệch."
            )

    left, right = st.columns(2)
    with left:
        st.subheader("Hoàn cảnh tài chính và kết quả sau 3 năm")
        equity = data["equity"].melt(
            id_vars="student_group",
            value_vars=["completion_3yr_rate", "withdrawal_3yr_rate"],
            var_name="outcome",
            value_name="rate",
        )
        equity["outcome"] = equity["outcome"].map({"completion_3yr_rate": "Hoàn thành", "withdrawal_3yr_rate": "Rút khỏi chương trình"})
        equity["student_group"] = equity["student_group"].replace({"Nhận Pell Grant": "Cần hỗ trợ tài chính", "Không nhận Pell Grant": "Không nhận Pell", "Thế hệ đầu học đại học": "Đầu tiên trong gia đình học ĐH", "Không phải thế hệ đầu": "Gia đình đã có người học ĐH"})
        chart = px.bar(
            equity,
            x="rate",
            y="student_group",
            color="outcome",
            barmode="group",
            text_auto=".1%",
            color_discrete_map={"Hoàn thành": COLORS["primary"], "Rút khỏi chương trình": COLORS["risk"]},
            labels={"student_group": "Nhóm sinh viên", "rate": "Tỷ lệ", "outcome": ""},
        )
        chart.update_xaxes(tickformat=".0%", range=[0, max(0.6, equity["rate"].max() * 1.18)])
        chart.update_yaxes(automargin=True)
        chart.update_layout(
            height=540,
            legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="center", x=0.5),
            margin=dict(l=15, r=15, t=75, b=45),
        )
        st.plotly_chart(chart, width="stretch")
        st.caption(
            f"Hai phép so sánh độc lập đều cho thấy khoảng cách: nhóm nhận Pell có tỷ lệ "
            f"hoàn thành thấp hơn nhóm không nhận Pell {pell_gap * 100:.1f} điểm phần trăm; "
            f"nhóm thế hệ đầu thấp hơn nhóm còn lại {first_generation_gap * 100:.1f} điểm "
            f"phần trăm. Kết quả gợi ý cần phối hợp hỗ trợ tài chính với cố vấn học tập, nhưng "
            f"dữ liệu tổng hợp hiện tại không cho biết Pell và thế hệ đầu cùng xuất hiện trên "
            f"một cá nhân nên không thể kết luận về một ‘rào cản kép’."
        )
    with right:
        st.subheader("Khi nhiều điều kiện bất lợi cùng xuất hiện")
        chart = make_subplots(specs=[[{"secondary_y": True}]])
        chart.add_trace(go.Bar(x=disadvantage["disadvantage_count"], y=disadvantage["median_completion_rate"], name="Hoàn thành điển hình", marker_color=COLORS["blue"], text=[f"{value:.1%}" for value in disadvantage["median_completion_rate"]], textposition="outside"), secondary_y=False)
        chart.add_trace(go.Scatter(x=disadvantage["disadvantage_count"], y=disadvantage["low_completion_share"], name="Tỷ trọng dưới 40%", mode="lines+markers", line=dict(color=COLORS["risk"], width=3)), secondary_y=True)
        chart.update_yaxes(tickformat=".0%", secondary_y=False)
        chart.update_yaxes(tickformat=".0%", secondary_y=True)
        chart.update_xaxes(title="Số điều kiện bất lợi cùng xuất hiện", dtick=1, title_standoff=20)
        chart.update_layout(
            height=540,
            legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="center", x=0.5),
            margin=dict(l=15, r=15, t=75, b=80),
        )
        st.plotly_chart(chart, width="stretch")
        zero_disadvantage = disadvantage.loc[
            disadvantage["disadvantage_count"].eq(0)
        ].iloc[0]
        st.caption(
            f"Trên toàn bộ dữ liệu, tỷ trọng nhóm có completion dưới 40% tăng từ "
            f"{zero_disadvantage.low_completion_share:.1%} khi không có điều kiện bất lợi "
            f"lên cao nhất {peak_disadvantage.low_completion_share:.1%} ở mức "
            f"{int(peak_disadvantage.disadvantage_count)} điều kiện "
            f"(N={int(peak_disadvantage.institution_count)}). Các mức sau không tăng đều, "
            f"nên chỉ số này chỉ dùng để sàng lọc nhóm cần phân tích sâu; trước khi đề xuất "
            f"can thiệp phải kiểm tra quy mô và thành phần từng nhóm."
        )


def model_page(data: dict[str, Any], frame: pd.DataFrame) -> None:
    st.header("3 · Mô hình nhận diện nhóm completion dưới 40% tốt đến đâu?")
    st.markdown(
        '<div class="note"><b>RQ6:</b> Logistic Regression có nhận diện được các nhóm cơ sở–năm '
        'có tỷ lệ hoàn thành dưới 40% trên năm kiểm tra ngoài thời gian hay không, và việc '
        'bổ sung tỷ lệ duy trì sau năm nhất cải thiện Accuracy, Recall, Balanced Accuracy và '
        'ROC-AUC đến mức nào? Kết quả chỉ dùng để sắp xếp nhóm cần ưu tiên kiểm tra.</div>',
        unsafe_allow_html=True,
    )
    metrics = data["metrics"]
    selected = metrics["models"][metrics["selected_model"]]
    structural = metrics["models"]["structural_logistic"]
    prediction_model = load_prediction_model()
    model_features = list(prediction_model.feature_names_in_)
    columns = st.columns(4)
    columns[0].metric("Dự báo đúng tổng thể", f"{selected['accuracy']:.1%}")
    columns[1].metric("Đúng cân bằng hai nhóm", f"{selected['balanced_accuracy']:.1%}")
    columns[2].metric("Phát hiện nhóm kết quả thấp", f"{selected['recall']:.1%}")
    columns[3].metric("Khả năng xếp hạng rủi ro", f"{selected['roc_auc']:.3f}")

    merge_columns = [
        "unitid",
        *[feature for feature in model_features if feature not in data["predictions"].columns],
    ]
    predictions = data["predictions"].merge(
        frame[merge_columns].drop_duplicates("unitid"),
        on="unitid",
        how="inner",
    )
    if predictions.empty:
        st.warning("Bộ lọc hiện tại không còn quan sát đủ điều kiện để chạy phần dự báo.")
        return

    st.subheader("Dự báo hiện tại nói gì?")
    predicted_low_count = int(predictions["predicted_low_completion"].sum())
    high_risk_count = int((predictions["risk_level"] == "Cao").sum())
    prediction_columns = st.columns(3)
    prediction_columns[0].metric(
        "Dự báo tỷ lệ hoàn thành dưới 40%",
        f"{predicted_low_count:,} nhóm",
        f"{predicted_low_count / len(predictions):.1%} dữ liệu đang lọc",
    )
    prediction_columns[1].metric(
        "Rủi ro cao từ 70%",
        f"{high_risk_count:,} nhóm",
        f"{high_risk_count / len(predictions):.1%} dữ liệu đang lọc",
    )
    prediction_columns[2].metric(
        "Xác suất rủi ro trung bình",
        f"{predictions['risk_probability'].mean():.1%}",
        "Trung bình các nhóm đang lọc",
    )
    st.caption(
        "Mỗi nhóm ở đây là một quan sát cấp cơ sở trong dữ liệu hiện tại. Mô hình dự báo "
        "khả năng tỷ lệ hoàn thành của nhóm thấp hơn 40% và tổng hợp kết quả theo đặc điểm "
        "đào tạo, khu vực và nguồn lực."
    )

    st.subheader("Nhóm nào cần ưu tiên, vì sao và nên cải thiện gì?")
    priority_profiles = high_risk_profiles(
        predictions,
        data["institutions"],
        prediction_model,
    )
    if priority_profiles.empty:
        st.info(
            "Bộ lọc hiện tại không có nhóm kết hợp nào vừa đủ số quan sát vừa có rủi ro "
            "trung bình từ 50% để lập hồ sơ ưu tiên."
        )
    else:
        top_profile = priority_profiles.iloc[0]
        top_reason = str(top_profile["Yếu tố cần kiểm tra"]).split("|")[0].strip()
        top_action = str(top_profile["Hướng cải thiện nên xem xét"]).split("|")[0].strip()
        st.markdown(
            f'<div class="note"><b>Nhóm cần ưu tiên nhất:</b> {top_profile["Nhóm"]}. '
            f'Rủi ro dự báo trung bình <b>{top_profile["Rủi ro trung bình"]:.1%}</b>, '
            f'tỷ lệ hoàn thành điển hình <b>{top_profile["Hoàn thành điển hình"]:.1%}</b>. '
            f'Điểm cần kiểm tra trước: <b>{top_reason.lower()}</b>. '
            f'Hướng cải thiện nên xem xét: <b>{top_action.lower()}</b>.</div>',
            unsafe_allow_html=True,
        )
        display_profiles = priority_profiles.copy()
        display_profiles["Yếu tố nổi bật"] = display_profiles["Yếu tố cần kiểm tra"].str.split(
            "|", regex=False
        ).str[0].str.strip()
        display_profiles["Cải thiện ưu tiên"] = display_profiles[
            "Hướng cải thiện nên xem xét"
        ].str.split("|", regex=False).str[0].str.strip()
        for column in [
            "Rủi ro trung bình",
            "Hoàn thành điển hình",
        ]:
            display_profiles[column] = display_profiles[column].map(lambda value: f"{value:.1%}")
        display_profiles = display_profiles[
            [
                "Nhóm",
                "Số quan sát",
                "Rủi ro trung bình",
                "Hoàn thành điển hình",
                "Yếu tố nổi bật",
                "Cải thiện ưu tiên",
            ]
        ].head(5)
        st.dataframe(
            display_profiles,
            hide_index=True,
            width="stretch",
            height=min(385, 72 + 58 * len(display_profiles)),
        )
        st.caption(
            "Nhóm là tổ hợp bậc đào tạo · loại hình quản lý · khu vực sống, chỉ hiện khi "
            "có đủ số quan sát. ‘Chênh dự báo’ cho biết xác suất thay đổi bao nhiêu khi riêng "
            "yếu tố đó được đưa về mức điển hình và các yếu tố khác được giữ nguyên."
        )
        with st.expander("Xem đầy đủ yếu tố và hướng cải thiện của từng nhóm"):
            selected_profile_name = st.selectbox(
                "Chọn nhóm cần giải thích",
                priority_profiles["Nhóm"].tolist(),
                key="priority_profile",
            )
            selected_profile = priority_profiles.loc[
                priority_profiles["Nhóm"] == selected_profile_name
            ].iloc[0]
            st.markdown("**Các yếu tố đang làm xác suất dự báo cao hơn:**")
            for reason in str(selected_profile["Yếu tố cần kiểm tra"]).split("|"):
                st.markdown(f"- {reason.strip()}")
            st.markdown("**Hướng cải thiện nên kiểm tra tính khả thi:**")
            for action in str(selected_profile["Hướng cải thiện nên xem xét"]).split("|"):
                st.markdown(f"- {action.strip()}")
            st.caption(
                "Bậc đào tạo, loại hình và khu vực xác định nhóm so sánh. Các chênh dự báo "
                "được kiểm tra từng yếu tố riêng và được đọc tách biệt."
            )

    st.subheader("Thông tin sau năm nhất giúp dự báo tốt hơn bao nhiêu?")
    comparison = pd.DataFrame(
        {
            "Kịch bản": ["Chỉ dùng điều kiện nền tảng", "Bổ sung tiếp tục học sau năm nhất"],
            "Dự báo đúng tổng thể": [structural["accuracy"], selected["accuracy"]],
            "Phát hiện nhóm kết quả thấp": [structural["recall"], selected["recall"]],
            "Khả năng xếp hạng": [structural["roc_auc"], selected["roc_auc"]],
        }
    ).melt(id_vars="Kịch bản", var_name="Chỉ số", value_name="Giá trị")
    comparison_chart = px.bar(
        comparison,
        x="Chỉ số",
        y="Giá trị",
        color="Kịch bản",
        barmode="group",
        text_auto=".1%",
        color_discrete_sequence=[COLORS["blue"], COLORS["primary"]],
    )
    comparison_chart.update_yaxes(tickformat=".0%", range=[0, 1])
    comparison_chart.update_layout(
        height=430,
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="center", x=0.5),
        margin=dict(l=15, r=15, t=75, b=55),
    )
    st.plotly_chart(comparison_chart, width="stretch")
    accuracy_gain = selected["accuracy"] - structural["accuracy"]
    auc_gain = selected["roc_auc"] - structural["roc_auc"]
    st.success(
        f"Điều rút ra: sau khi biết tỷ lệ tiếp tục học sau năm nhất, Accuracy tăng "
        f"{accuracy_gain:.2%} và ROC-AUC tăng {auc_gain:.3f}. Điều này cho thấy khả năng "
        f"duy trì việc học cung cấp thêm thông tin dự báo rõ rệt."
    )

    left, right = st.columns([0.9, 1.1])
    with left:
        average = predictions["risk_probability"].mean()
        gauge = go.Figure(go.Indicator(mode="gauge+number", value=average * 100, number={"suffix": "%", "valueformat": ".1f"}, title={"text": "Rủi ro trung bình của nhóm đang lọc"}, gauge={"axis": {"range": [0, 100]}, "bar": {"color": COLORS["risk"]}, "steps": [{"range": [0, 40], "color": "#DCFCE7"}, {"range": [40, 70], "color": "#FEF3C7"}, {"range": [70, 100], "color": "#FEE2E2"}]}))
        gauge.update_layout(height=340, margin=dict(l=30, r=30, t=70, b=20))
        st.plotly_chart(gauge, width="stretch")
        distribution = predictions["risk_level"].value_counts().rename_axis("level").reset_index(name="count")
        donut = px.pie(distribution, names="level", values="count", hole=.58, color="level", color_discrete_map={"Cao": COLORS["risk"], "Trung bình": COLORS["warning"], "Thấp": COLORS["safe"]})
        donut.update_layout(height=320, legend_title_text="Mức dự báo")
        st.plotly_chart(donut, width="stretch")
    with right:
        st.subheader("Mô hình dự báo đúng và sai như thế nào?")
        matrix = np.array(metrics["confusion_matrix"])
        confusion = go.Figure(go.Heatmap(z=matrix, x=["Dự báo không thấp", "Dự báo thấp"], y=["Thực tế không thấp", "Thực tế thấp"], colorscale="Blues", text=matrix, texttemplate="%{text:,}", hovertemplate="%{y}<br>%{x}<br>Số trường hợp=%{z:,}<extra></extra>"))
        confusion.update_layout(height=370, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(confusion, width="stretch")
        st.markdown(f"Mô hình tìm đúng **{matrix[1, 1]:,}/{matrix[1].sum():,}** trường hợp kết quả thấp và bỏ sót **{matrix[1, 0]:,}** trường hợp.")

        st.subheader("Yếu tố giúp mô hình phân biệt kết quả")
        importance = data["importance"].nlargest(10, "importance_mean").copy()
        importance["label"] = importance["feature"].map(MODEL_LABELS).fillna(importance["feature"])
        importance = importance.sort_values("importance_mean")
        chart = px.bar(importance, x="importance_mean", y="label", orientation="h", error_x="importance_std", color="importance_mean", color_continuous_scale="Teal", labels={"importance_mean": "Mức đóng góp vào dự báo", "label": "Yếu tố"})
        chart.update_layout(height=410, coloraxis_showscale=False)
        st.plotly_chart(chart, width="stretch")
        st.caption("Mức đóng góp được đo bằng permutation importance trên tập kiểm tra năm 2022.")

    st.subheader("Nhóm nào có rủi ro dự báo cao nhất?")
    profile_columns = [
        "retention_rate",
        "student_faculty_ratio",
        "instructional_spend_per_fte",
        "full_time_faculty_share",
        "risk_probability",
        "completion_rate",
        "unitid",
    ]
    profiles = predictions[profile_columns].dropna().copy()
    if profiles.empty or profiles["retention_rate"].nunique() < 2:
        st.info("Bộ lọc hiện tại không đủ dữ liệu để tạo ma trận hồ sơ rủi ro.")
    else:
        retention_codes = pd.qcut(
            profiles["retention_rate"], 4, labels=False, duplicates="drop"
        )
        level_count = int(retention_codes.max()) + 1
        label_options = {
            2: ["Thấp", "Cao"],
            3: ["Thấp", "Trung bình", "Cao"],
            4: ["Thấp", "Trung bình thấp", "Trung bình cao", "Cao"],
        }
        retention_labels = label_options.get(
            level_count, [f"Mức {index + 1}" for index in range(level_count)]
        )
        profiles["Mức tiếp tục học"] = retention_codes.map(dict(enumerate(retention_labels)))
        resource_flags = pd.DataFrame(index=profiles.index)
        resource_flags["Nhiều sinh viên/giảng viên"] = profiles["student_faculty_ratio"].ge(
            profiles["student_faculty_ratio"].quantile(0.75)
        )
        resource_flags["Chi giảng dạy thấp"] = profiles["instructional_spend_per_fte"].le(
            profiles["instructional_spend_per_fte"].quantile(0.25)
        )
        resource_flags["Ít giảng viên toàn thời gian"] = profiles["full_time_faculty_share"].le(
            profiles["full_time_faculty_share"].quantile(0.25)
        )
        profiles["pressure_count"] = resource_flags.sum(axis=1)
        profiles["Áp lực nguồn lực"] = pd.cut(
            profiles["pressure_count"],
            bins=[-1, 0, 1, 3],
            labels=["Thấp · 0 điều kiện", "Vừa · 1 điều kiện", "Cao · 2–3 điều kiện"],
        )
        profile_summary = (
            profiles.groupby(["Mức tiếp tục học", "Áp lực nguồn lực"], observed=True)
            .agg(
                group_count=("unitid", "size"),
                average_risk=("risk_probability", "mean"),
                median_completion=("completion_rate", "median"),
            )
            .reset_index()
        )
        profile_matrix = profile_summary.pivot(
            index="Mức tiếp tục học", columns="Áp lực nguồn lực", values="average_risk"
        ).reindex(index=retention_labels)
        risk_heatmap = go.Figure(
            go.Heatmap(
                z=profile_matrix.to_numpy(),
                x=profile_matrix.columns,
                y=profile_matrix.index,
                colorscale="YlOrRd",
                zmin=0,
                zmax=0.8,
                text=np.vectorize(lambda value: "—" if pd.isna(value) else f"{value:.1%}")(
                    profile_matrix.to_numpy()
                ),
                texttemplate="%{text}",
                hovertemplate=(
                    "Tiếp tục học: %{y}<br>Áp lực nguồn lực: %{x}<br>"
                    "Rủi ro dự báo trung bình: %{z:.1%}<extra></extra>"
                ),
                colorbar=dict(title="Rủi ro"),
            )
        )
        risk_heatmap.update_layout(
            height=460,
            xaxis_title="Áp lực nguồn lực giảng dạy",
            yaxis_title="Khả năng tiếp tục học sau năm nhất",
            margin=dict(l=20, r=20, t=20, b=75),
        )
        st.plotly_chart(risk_heatmap, width="stretch")
        highest_profile = profile_summary.nlargest(1, "average_risk").iloc[0]
        lowest_profile = profile_summary.nsmallest(1, "average_risk").iloc[0]
        st.markdown(
            f'<div class="note"><b>Điều rút ra từ ma trận:</b> nhóm có mức tiếp tục học '
            f'<b>{str(highest_profile["Mức tiếp tục học"]).lower()}</b> và áp lực nguồn lực '
            f'<b>{str(highest_profile["Áp lực nguồn lực"]).lower()}</b> có rủi ro dự báo trung bình '
            f'<b>{highest_profile.average_risk:.1%}</b>. Nhóm thấp nhất là tiếp tục học '
            f'<b>{str(lowest_profile["Mức tiếp tục học"]).lower()}</b>, áp lực nguồn lực '
            f'<b>{str(lowest_profile["Áp lực nguồn lực"]).lower()}</b>, với rủi ro '
            f'<b>{lowest_profile.average_risk:.1%}</b>.</div>',
            unsafe_allow_html=True,
        )

    st.subheader("Kiểm tra thêm theo từng cách phân nhóm")
    options = {"Loại hình quản lý": "control", "Đô thị–nông thôn": "locale_group", "Bậc đào tạo": "predominant_degree", "Học trực tuyến": "distance_only"}
    group_name = st.selectbox("Chọn cách gom nhóm", list(options))
    group_column = options[group_name]
    grouped = (
        predictions.groupby(group_column, dropna=False)
        .agg(group_count=("unitid", "nunique"), average_risk=("risk_probability", "mean"), completion=("completion_rate", "median"), high_risk_share=("risk_level", lambda values: (values == "Cao").mean()))
        .reset_index()
        .query("group_count >= 5")
        .sort_values("average_risk")
    )
    if grouped.empty:
        st.info("Bộ lọc hiện tại không có nhóm nào đủ ít nhất 5 quan sát để so sánh.")
    else:
        chart = px.bar(grouped, x="average_risk", y=group_column, orientation="h", color="average_risk", color_continuous_scale="YlOrRd", text_auto=".1%", hover_data={"group_count": ":,", "completion": ":.1%", "high_risk_share": ":.1%"}, labels={"average_risk": "Rủi ro dự báo trung bình", group_column: group_name, "group_count": "Số nhóm dữ liệu", "completion": "Hoàn thành điển hình", "high_risk_share": "Tỷ trọng rủi ro cao"})
        chart.update_xaxes(tickformat=".0%")
        chart.update_layout(height=max(350, 48 * len(grouped)), coloraxis_showscale=False)
        st.plotly_chart(chart, width="stretch")
        highest_group = grouped.nlargest(1, "average_risk").iloc[0]
        lowest_group = grouped.nsmallest(1, "average_risk").iloc[0]
        st.info(
            f"Theo cách gom “{group_name}”, nhóm có rủi ro dự báo cao nhất là "
            f"“{highest_group[group_column]}” ({highest_group.average_risk:.1%}); thấp nhất là "
            f"“{lowest_group[group_column]}” ({lowest_group.average_risk:.1%}). Chênh lệch này "
            f"xác định thứ tự ưu tiên phân tích và hỗ trợ ở cấp nhóm."
        )

    st.subheader("Dự báo gợi ý ưu tiên gì?")
    st.markdown(
        """
        1. **Theo dõi việc tiếp tục học sau năm nhất trước tiên:** đây là thông tin làm khả
           năng dự báo tăng rõ nhất.
        2. **Ưu tiên nhóm vừa có khả năng tiếp tục học thấp vừa chịu áp lực nguồn lực:**
           cần kiểm tra thêm cố vấn học tập, hỗ trợ môn học và khả năng tiếp cận giảng viên.
        3. **Kết hợp với phân tích tài chính ở trang 2:** khoảng cách Pell, khoản vay và chi
           phí giúp xác định nhóm cần khảo sát hỗ trợ tài chính sâu hơn.

        Các đề xuất được triển khai ở cấp nhóm và cần được đánh giá lại sau can thiệp.
        """
    )

    with st.expander("Giải thích các chỉ số mô hình"):
        st.markdown(
            """
            - **Dự báo đúng tổng thể:** trong 100 trường hợp, mô hình dự báo đúng bao nhiêu.
            - **Đúng cân bằng:** đo cân bằng khả năng nhận ra cả nhóm thấp và nhóm không thấp.
            - **Phát hiện nhóm kết quả thấp:** trong các trường hợp thực sự thấp, mô hình tìm ra bao nhiêu.
            - **Khả năng xếp hạng:** 0,5 gần ngẫu nhiên; càng gần 1 càng tốt.
            """
        )


def main() -> None:
    try:
        data = load_data()
    except FileNotFoundError as error:
        st.error(str(error))
        st.code("python scripts/build_dataset.py\npython scripts/run_eda.py\npython scripts/train_model.py --prefer-temporal")
        st.stop()

    st.title("🎓 Các yếu tố liên quan đến duy trì và hoàn thành đại học")
    st.markdown(
        '<div class="definition"><b>Câu hỏi trung tâm:</b> Tỷ lệ hoàn thành, duy trì sau năm '
        'nhất và rút khỏi chương trình khác nhau ở đâu; các chỉ báo tài chính, nguồn lực và '
        'điều kiện đào tạo liên hệ với những khoảng cách đó như thế nào; và mô hình có nhận '
        'diện được nhóm cơ sở–năm có completion dưới 40% hay không? Các kết quả phản ánh '
        'mối liên hệ trong dữ liệu quan sát, không chứng minh nguyên nhân.</div>',
        unsafe_allow_html=True,
    )
    glossary()
    st.sidebar.title("Điều hướng và bộ lọc")
    page = st.sidebar.radio("Trang", ["1 · Phân bố kết quả", "2 · Tài chính và nguồn lực", "3 · Dự báo completion thấp"])
    filtered = global_filters(data["institutions"])
    st.sidebar.caption(f"Đang phân tích {filtered['unitid'].nunique():,} nhóm cơ sở có dữ liệu.")
    if filtered.empty:
        st.warning("Không có dữ liệu phù hợp với tổ hợp bộ lọc hiện tại.")
        st.stop()
    if page.startswith("1"):
        overview_page(data, filtered)
    elif page.startswith("2"):
        factor_page(data, filtered)
    else:
        model_page(data, filtered)
    st.divider()
    st.caption("Nguồn: College Scorecard và NCES IPEDS · Đơn vị trình bày: nhóm cơ sở và nhóm sinh viên.")


main()
