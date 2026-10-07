from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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
    "muted": "#64748B",
    "light": "#E2E8F0",
}

RISK_COLORS = {
    "Cao": COLORS["risk"],
    "Trung bình": COLORS["warning"],
    "Thấp": COLORS["safe"],
}


st.set_page_config(
    page_title="Kết quả học tập đại học Hoa Kỳ",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
    [data-testid="stMetric"] {
        background: white; border: 1px solid #e2e8f0; border-radius: 14px;
        padding: 14px 16px; box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
    }
    .story-card {
        border-left: 5px solid #0f766e; background: #f0fdfa; border-radius: 10px;
        padding: 0.85rem 1rem; margin: 0.55rem 0;
    }
    .definition {
        background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;
        padding: 0.65rem 0.9rem; color: #334155;
    }
    h1, h2, h3 {color: #0f172a;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, Any]:
    required = {
        "institutions": DATA / "institutions.csv",
        "states": DATA / "state_summary.csv",
        "fields": DATA / "field_summary.csv",
        "field_state": DATA / "field_state_summary.csv",
        "equity": DATA / "equity_long.csv",
        "predictions": DATA / "model_predictions.csv",
        "correlations": EDA / "factor_correlations.csv",
        "equity_summary": EDA / "equity_summary.csv",
        "disadvantage": EDA / "disadvantage_summary.csv",
        "importance": MODEL / "feature_importance.csv",
        "confusion": MODEL / "confusion_matrix.csv",
        "metrics": MODEL / "metrics.json",
        "insights": EDA / "insights.json",
    }
    missing = [str(path) for path in required.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Thiếu đầu ra pipeline:\n" + "\n".join(missing))
    loaded: dict[str, Any] = {}
    for key, path in required.items():
        if path.suffix == ".csv":
            loaded[key] = pd.read_csv(path, low_memory=False)
        else:
            loaded[key] = json.loads(path.read_text(encoding="utf-8"))
    return loaded


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    valid = values.notna() & weights.notna() & (weights > 0)
    if not valid.any():
        return float("nan")
    return float(np.average(values[valid], weights=weights[valid]))


def format_percent(value: float) -> str:
    return "—" if pd.isna(value) else f"{value:.1%}"


def filter_institutions(frame: pd.DataFrame) -> pd.DataFrame:
    states = sorted(frame["state"].dropna().unique())
    controls = sorted(frame["control"].dropna().unique())
    degrees = sorted(frame["predominant_degree"].dropna().unique())
    locales = sorted(frame["locale_group"].dropna().unique())
    distance = sorted(frame["distance_only"].dropna().unique())

    selected_states = st.sidebar.multiselect("Bang/lãnh thổ", states)
    selected_controls = st.sidebar.multiselect("Loại hình cơ sở", controls)
    selected_degrees = st.sidebar.multiselect("Bậc đào tạo chính", degrees)
    selected_locales = st.sidebar.multiselect("Địa bàn", locales)
    selected_distance = st.sidebar.multiselect("Hình thức đào tạo", distance)

    result = frame.copy()
    filters = [
        ("state", selected_states),
        ("control", selected_controls),
        ("predominant_degree", selected_degrees),
        ("locale_group", selected_locales),
        ("distance_only", selected_distance),
    ]
    for column, values in filters:
        if values:
            result = result[result[column].isin(values)]
    return result


def aggregate_states(frame: pd.DataFrame) -> pd.DataFrame:
    records = []
    valid = frame[frame["state"].astype("string").str.fullmatch(r"[A-Z]{2}").fillna(False)]
    for state, part in valid.groupby("state"):
        weights = part["undergrad_enrollment"].clip(lower=0)
        eligible = part["low_completion"].notna()
        records.append(
            {
                "state": state,
                "institution_count": part["unitid"].nunique(),
                "undergrad_enrollment": weights.sum(min_count=1),
                "completion_rate": weighted_mean(part["completion_rate"], weights),
                "retention_rate": weighted_mean(part["retention_rate"], weights),
                "pell_share": weighted_mean(part["pell_share"], weights),
                "low_completion_share": part.loc[eligible, "low_completion"].mean()
                if eligible.any()
                else np.nan,
            }
        )
    return pd.DataFrame(records)


def insight_card(insight: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="story-card">
          <strong>{insight['id']} · {insight['title']}</strong><br>
          {insight['statement']}<br>
          <small><b>Giới hạn:</b> {insight['caveat']}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_overview(data: dict[str, Any], filtered: pd.DataFrame) -> None:
    st.header("1 · Bức tranh kết quả học tập trên toàn quốc")
    st.caption(
        "Mục tiêu: xác định nơi nào và loại hình cơ sở nào có tỷ lệ hoàn thành thấp. "
        "Các tỷ lệ tổng hợp được trọng số theo quy mô sinh viên đại học."
    )

    weights = filtered["undergrad_enrollment"].clip(lower=0)
    completion = weighted_mean(filtered["completion_rate"], weights)
    retention = weighted_mean(filtered["retention_rate"], weights)
    eligible = filtered["low_completion"].notna()
    low_share = filtered.loc[eligible, "low_completion"].mean() if eligible.any() else np.nan

    cols = st.columns(4)
    cols[0].metric("Cơ sở", f"{filtered['unitid'].nunique():,}")
    cols[1].metric("Sinh viên đại học", f"{weights.sum():,.0f}")
    cols[2].metric("Tỷ lệ hoàn thành", format_percent(completion))
    cols[3].metric("Cơ sở hoàn thành thấp", format_percent(low_share))

    states = aggregate_states(filtered)
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Geographic Map · Tỷ lệ hoàn thành theo bang")
        map_figure = px.choropleth(
            states,
            locations="state",
            locationmode="USA-states",
            scope="usa",
            color="completion_rate",
            hover_name="state",
            hover_data={
                "completion_rate": ":.1%",
                "retention_rate": ":.1%",
                "institution_count": ":,",
                "undergrad_enrollment": ":,.0f",
                "state": False,
            },
            color_continuous_scale="RdYlGn",
            range_color=(0.3, 0.8),
            labels={"completion_rate": "Hoàn thành"},
        )
        map_figure.update_layout(height=520, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(map_figure, width="stretch", key="overview_state_map")
        st.caption(
            "Màu thể hiện tỷ lệ hoàn thành có trọng số. Chọn bang ở bộ lọc để drill-down tới cơ sở."
        )

    with right:
        st.subheader("Bang có kết quả thấp/cao nhất")
        ranked = states[
            (states["institution_count"] >= 5) & states["completion_rate"].notna()
        ]
        ranked = pd.concat(
            [ranked.nsmallest(7, "completion_rate"), ranked.nlargest(7, "completion_rate")]
        ).drop_duplicates("state")
        ranked = ranked.sort_values("completion_rate")
        bar = px.bar(
            ranked,
            x="completion_rate",
            y="state",
            orientation="h",
            color="completion_rate",
            color_continuous_scale="RdYlGn",
            text_auto=".1%",
            labels={"completion_rate": "Tỷ lệ hoàn thành", "state": "Bang"},
        )
        bar.update_layout(height=520, coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(bar, width="stretch")

    st.subheader("Drill-down · Cơ cấu kết quả theo loại hình cơ sở")
    structure = (
        filtered.dropna(subset=["low_completion"])
        .groupby(["control", "risk_label"])["unitid"]
        .nunique()
        .rename("institution_count")
        .reset_index()
    )
    structure["share"] = structure["institution_count"] / structure.groupby("control")[
        "institution_count"
    ].transform("sum")
    stacked = px.bar(
        structure,
        x="control",
        y="share",
        color="risk_label",
        barmode="stack",
        text_auto=".1%",
        color_discrete_map={
            "Tỷ lệ hoàn thành thấp": COLORS["risk"],
            "Không thuộc nhóm thấp": COLORS["safe"],
        },
        labels={"share": "Tỷ trọng", "control": "Loại hình", "risk_label": "Kết quả"},
    )
    stacked.update_yaxes(tickformat=".0%")
    stacked.update_layout(height=420, legend_title_text="")
    st.plotly_chart(stacked, width="stretch")

    point_data = filtered.dropna(subset=["latitude", "longitude", "completion_rate"]).copy()
    if len(point_data) > 3500:
        point_data = point_data.nlargest(3500, "undergrad_enrollment")
    st.subheader("Bản đồ điểm · Drill-down tới từng cơ sở")
    point_map = px.scatter_geo(
        point_data,
        lat="latitude",
        lon="longitude",
        scope="usa",
        color="completion_rate",
        size=point_data["undergrad_enrollment"].clip(lower=1),
        size_max=18,
        hover_name="institution_name",
        hover_data={
            "state": True,
            "control": True,
            "completion_rate": ":.1%",
            "retention_rate": ":.1%",
            "undergrad_enrollment": ":,.0f",
            "latitude": False,
            "longitude": False,
        },
        color_continuous_scale="RdYlGn",
        range_color=(0.2, 0.9),
    )
    point_map.update_layout(height=600, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(point_map, width="stretch")

    insight_card(data["insights"][0])
    insight_card(data["insights"][1])


def page_factors(data: dict[str, Any], filtered: pd.DataFrame) -> None:
    st.header("2 · Tác nhân liên quan và khoảng cách giữa các nhóm")
    st.caption(
        "Trang này trả lời yếu tố nào đi cùng kết quả cao/thấp. Mọi nhận định là liên hệ thống kê, "
        "không phải kết luận nhân quả."
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Duy trì năm đầu và hoàn thành")
        scatter_data = filtered.dropna(
            subset=["retention_rate", "completion_rate", "control"]
        ).copy()
        if len(scatter_data) > 3000:
            scatter_data = scatter_data.sample(3000, random_state=42)
        scatter = px.scatter(
            scatter_data,
            x="retention_rate",
            y="completion_rate",
            color="control",
            size="undergrad_enrollment",
            size_max=18,
            opacity=0.55,
            hover_name="institution_name",
            hover_data={"state": True, "pell_share": ":.1%"},
            labels={
                "retention_rate": "Duy trì sau năm đầu",
                "completion_rate": "Hoàn thành",
                "control": "Loại hình",
            },
        )
        valid = scatter_data[["retention_rate", "completion_rate"]].dropna()
        if len(valid) >= 2:
            slope, intercept = np.polyfit(valid["retention_rate"], valid["completion_rate"], 1)
            x_line = np.linspace(valid["retention_rate"].min(), valid["retention_rate"].max(), 100)
            scatter.add_trace(
                go.Scatter(
                    x=x_line,
                    y=slope * x_line + intercept,
                    mode="lines",
                    name="Xu hướng chung",
                    line=dict(color="#111827", width=2),
                )
            )
        scatter.update_xaxes(tickformat=".0%")
        scatter.update_yaxes(tickformat=".0%")
        scatter.update_layout(height=510)
        st.plotly_chart(scatter, width="stretch")

    with right:
        st.subheader("Phân bố hoàn thành theo loại hình")
        box = px.box(
            filtered.dropna(subset=["completion_rate", "control"]),
            x="control",
            y="completion_rate",
            color="control",
            points="outliers",
            labels={"control": "Loại hình", "completion_rate": "Hoàn thành"},
        )
        box.update_yaxes(tickformat=".0%")
        box.update_layout(height=510, showlegend=False)
        st.plotly_chart(box, width="stretch")

    st.subheader("Heatmap · Mức liên hệ đơn biến với tỷ lệ hoàn thành")
    corr = data["correlations"].sort_values("spearman_rho")
    heat = go.Figure(
        data=go.Heatmap(
            z=corr[["spearman_rho"]].to_numpy(),
            y=corr["factor_label"],
            x=["Spearman rho"],
            colorscale="RdBu",
            zmid=0,
            zmin=-1,
            zmax=1,
            text=corr[["spearman_rho"]].map(lambda value: f"{value:.2f}").to_numpy(),
            texttemplate="%{text}",
            hovertemplate="%{y}<br>rho=%{z:.3f}<extra></extra>",
        )
    )
    heat.update_layout(height=470, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(heat, width="stretch")

    left, right = st.columns(2)
    with left:
        st.subheader("Khoảng cách theo Pell Grant và thế hệ đầu")
        equity = data["equity_summary"].melt(
            id_vars="student_group",
            value_vars=["completion_3yr_rate", "withdrawal_3yr_rate"],
            var_name="outcome",
            value_name="rate",
        )
        equity["outcome"] = equity["outcome"].map(
            {
                "completion_3yr_rate": "Hoàn thành sau 3 năm",
                "withdrawal_3yr_rate": "Rút khỏi cơ sở sau 3 năm",
            }
        )
        equity_chart = px.bar(
            equity,
            x="student_group",
            y="rate",
            color="outcome",
            barmode="group",
            text_auto=".1%",
            color_discrete_map={
                "Hoàn thành sau 3 năm": COLORS["primary"],
                "Rút khỏi cơ sở sau 3 năm": COLORS["risk"],
            },
            labels={"student_group": "Nhóm sinh viên", "rate": "Tỷ lệ", "outcome": ""},
        )
        equity_chart.update_yaxes(tickformat=".0%")
        equity_chart.update_layout(height=500, legend_orientation="h")
        st.plotly_chart(equity_chart, width="stretch")

    with right:
        st.subheader("Bất lợi cộng dồn")
        disadvantage = data["disadvantage"]
        combined = make_subplots(specs=[[{"secondary_y": True}]])
        combined.add_trace(
            go.Bar(
                x=disadvantage["disadvantage_count"],
                y=disadvantage["median_completion_rate"],
                name="Trung vị hoàn thành",
                marker_color=COLORS["blue"],
                text=[f"{value:.1%}" for value in disadvantage["median_completion_rate"]],
                textposition="outside",
            ),
            secondary_y=False,
        )
        combined.add_trace(
            go.Scatter(
                x=disadvantage["disadvantage_count"],
                y=disadvantage["low_completion_share"],
                name="Tỷ lệ cơ sở hoàn thành thấp",
                mode="lines+markers",
                line=dict(color=COLORS["risk"], width=3),
            ),
            secondary_y=True,
        )
        combined.update_yaxes(tickformat=".0%", secondary_y=False)
        combined.update_yaxes(tickformat=".0%", secondary_y=True)
        combined.update_xaxes(title="Số yếu tố bất lợi đồng thời", dtick=1)
        combined.update_layout(height=500, legend_orientation="h")
        st.plotly_chart(combined, width="stretch")

    st.subheader("Treemap · Văn bằng được cấp theo ngành và bậc đào tạo")
    fields = data["fields"].dropna(subset=["credentials_awarded"]).copy()
    top_names = (
        fields.groupby("field_name")["credentials_awarded"].sum().nlargest(30).index
    )
    fields = fields[fields["field_name"].isin(top_names)]
    tree = px.treemap(
        fields,
        path=["credential_name", "field_name"],
        values="credentials_awarded",
        color="median_debt",
        color_continuous_scale="YlOrRd",
        hover_data={
            "credentials_awarded": ":,.0f",
            "institution_count": ":,",
            "median_debt": ":$,.0f",
        },
        labels={"credentials_awarded": "Văn bằng", "median_debt": "Nợ trung vị"},
    )
    tree.update_layout(height=650, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(tree, width="stretch")
    st.caption(
        "Diện tích là số văn bằng IPEDSCOUNT2 năm gần nhất; đây là số văn bằng được cấp, "
        "không phải tỷ lệ hoàn thành ngành. Một người có thể nhận nhiều văn bằng."
    )

    for insight in data["insights"][2:5]:
        insight_card(insight)


def page_model(data: dict[str, Any], filtered: pd.DataFrame) -> None:
    st.header("3 · Logistic Regression và cảnh báo sớm")
    st.caption(
        "Mô hình nhận diện cơ sở có tỷ lệ hoàn thành dưới 40%. Đây là công cụ ưu tiên kiểm tra, "
        "không phải phán quyết về chất lượng trường hay cá nhân sinh viên."
    )
    metrics = data["metrics"]
    selected = metrics["models"][metrics["selected_model"]]
    cols = st.columns(5)
    cols[0].metric("Accuracy", f"{selected['accuracy']:.1%}")
    cols[1].metric("Balanced Accuracy", f"{selected['balanced_accuracy']:.1%}")
    cols[2].metric("Recall rủi ro", f"{selected['recall']:.1%}")
    cols[3].metric("F1", f"{selected['f1']:.1%}")
    cols[4].metric("ROC-AUC", f"{selected['roc_auc']:.3f}")

    predictions = data["predictions"].merge(
        filtered[["unitid"]].drop_duplicates(), on="unitid", how="inner"
    )
    risk_levels = st.multiselect(
        "Lọc mức rủi ro",
        ["Cao", "Trung bình", "Thấp"],
        default=["Cao", "Trung bình", "Thấp"],
    )
    predictions = predictions[predictions["risk_level"].isin(risk_levels)]

    left, right = st.columns([0.9, 1.1])
    with left:
        average_risk = predictions["risk_probability"].mean()
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=average_risk * 100 if pd.notna(average_risk) else 0,
                number={"suffix": "%", "valueformat": ".1f"},
                title={"text": "Xác suất rủi ro trung bình"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": COLORS["risk"]},
                    "steps": [
                        {"range": [0, 40], "color": "#DCFCE7"},
                        {"range": [40, 70], "color": "#FEF3C7"},
                        {"range": [70, 100], "color": "#FEE2E2"},
                    ],
                    "threshold": {"line": {"color": "#111827", "width": 3}, "value": 50},
                },
            )
        )
        gauge.update_layout(height=360, margin=dict(l=30, r=30, t=70, b=20))
        st.plotly_chart(gauge, width="stretch")

        risk_distribution = predictions["risk_level"].value_counts().rename_axis("risk_level").reset_index(name="count")
        donut = px.pie(
            risk_distribution,
            names="risk_level",
            values="count",
            hole=0.55,
            color="risk_level",
            color_discrete_map=RISK_COLORS,
        )
        donut.update_layout(height=350, legend_title_text="Mức rủi ro")
        st.plotly_chart(donut, width="stretch")

    with right:
        st.subheader("Ma trận nhầm lẫn trên tập test")
        matrix = np.array(metrics["confusion_matrix"])
        confusion = go.Figure(
            data=go.Heatmap(
                z=matrix,
                x=["Dự báo không thấp", "Dự báo thấp"],
                y=["Thực tế không thấp", "Thực tế thấp"],
                colorscale="Blues",
                text=matrix,
                texttemplate="%{text:,}",
                hovertemplate="%{y}<br>%{x}<br>N=%{z:,}<extra></extra>",
            )
        )
        confusion.update_layout(height=390, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(confusion, width="stretch")
        st.markdown(
            "Ma trận cho biết mô hình bỏ sót bao nhiêu cơ sở rủi ro và tạo bao nhiêu cảnh báo nhầm. "
            "Recall được ưu tiên vì bỏ sót nhóm hoàn thành thấp gây hậu quả lớn hơn kiểm tra thêm một cảnh báo."
        )

        st.subheader("Yếu tố đóng góp vào khả năng phân loại")
        importance = data["importance"].nlargest(10, "importance_mean").sort_values("importance_mean")
        importance_chart = px.bar(
            importance,
            x="importance_mean",
            y="feature",
            orientation="h",
            error_x="importance_std",
            color="importance_mean",
            color_continuous_scale="Teal",
            labels={"importance_mean": "Mức giảm Balanced Accuracy khi xáo trộn", "feature": "Biến"},
        )
        importance_chart.update_layout(height=430, coloraxis_showscale=False)
        st.plotly_chart(importance_chart, width="stretch")

    st.subheader("Danh sách cơ sở cần ưu tiên kiểm tra")
    action = predictions.sort_values("risk_probability", ascending=False).head(250).copy()
    action["risk_probability"] = action["risk_probability"] * 100
    action["completion_rate"] = action["completion_rate"] * 100
    st.dataframe(
        action[
            [
                "unitid",
                "institution_name",
                "state",
                "control",
                "predominant_degree",
                "risk_level",
                "risk_probability",
                "completion_rate",
            ]
        ],
        hide_index=True,
        width="stretch",
        column_config={
            "unitid": "UNITID",
            "institution_name": "Cơ sở",
            "state": "Bang",
            "control": "Loại hình",
            "predominant_degree": "Bậc chính",
            "risk_level": "Mức rủi ro",
            "risk_probability": st.column_config.ProgressColumn(
                "Xác suất rủi ro", min_value=0, max_value=100, format="%.1f%%"
            ),
            "completion_rate": st.column_config.NumberColumn(
                "Hoàn thành thực tế", format="%.1f%%"
            ),
        },
        height=520,
    )

    with st.expander("Mô hình dự báo cái gì và không dự báo cái gì?", expanded=True):
        st.markdown(
            """
            - **Dự báo:** cơ sở có tỷ lệ hoàn thành dưới 40%, dựa trên loại hình, địa bàn,
              quy mô, Pell Grant, vay liên bang, tỷ lệ sinh viên/giảng viên, chi phí và duy trì năm đầu.
            - **Không dự báo:** danh tính hoặc tương lai của từng sinh viên.
            - **Không phải quan hệ nhân quả:** feature importance cho biết giá trị dự báo, không chứng minh
              thay đổi một yếu tố sẽ trực tiếp làm thay đổi kết quả.
            - **Cutoff phân loại:** 0,50; ba mức hiển thị là thấp `<0,40`, trung bình `0,40–0,70`, cao `≥0,70`.
            """
        )


def main() -> None:
    try:
        data = load_data()
    except FileNotFoundError as error:
        st.error(str(error))
        st.code(
            "python scripts/build_dataset.py\n"
            "python scripts/run_eda.py\n"
            "python scripts/train_model.py"
        )
        st.stop()

    st.title("🎓 Các yếu tố liên quan đến kết quả học tập đại học")
    st.markdown(
        '<div class="definition"><b>Kết quả học tập</b> được đo bằng hoàn thành chương trình, '
        "duy trì sau năm đầu và rút khỏi cơ sở. Thu nhập chỉ là thông tin bổ sung. "
        "Dữ liệu ở cấp cơ sở/nhóm, không phải hồ sơ từng sinh viên.</div>",
        unsafe_allow_html=True,
    )

    st.sidebar.title("Điều hướng và bộ lọc")
    page = st.sidebar.radio(
        "Trang",
        [
            "1 · Bức tranh toàn quốc",
            "2 · Tác nhân & khoảng cách",
            "3 · Dự báo & cảnh báo",
        ],
    )
    filtered = filter_institutions(data["institutions"])
    st.sidebar.caption(f"Đang hiển thị {filtered['unitid'].nunique():,} cơ sở")

    if filtered.empty:
        st.warning("Không có dữ liệu phù hợp tổ hợp bộ lọc hiện tại.")
        st.stop()
    if page.startswith("1"):
        page_overview(data, filtered)
    elif page.startswith("2"):
        page_factors(data, filtered)
    else:
        page_model(data, filtered)

    st.divider()
    st.caption(
        "Nguồn: U.S. Department of Education College Scorecard và NCES IPEDS. "
        "Một số chỉ số chỉ bao phủ người nhận Title IV; các ô nhỏ có thể bị ẩn để bảo vệ riêng tư."
    )


main()

