from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    from .mvp_content import ACTION_PLAN, ATHLETE_OVERVIEW, BIOMARKER_INSIGHTS, BIOMARKER_RANGES
    from .privacy import load_uploaded_csv, render_privacy_guardrail, validate_demo_upload
except ImportError:
    from mvp_content import ACTION_PLAN, ATHLETE_OVERVIEW, BIOMARKER_INSIGHTS, BIOMARKER_RANGES
    from privacy import load_uploaded_csv, render_privacy_guardrail, validate_demo_upload


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "data" / "biomarkers" / "innerathlete_biomarker_template.csv"


def _load_demo_long_dataframe():
    rows = []
    for metric, details in BIOMARKER_RANGES.items():
        rows.append(
            {
                "Athlete_Code": ATHLETE_OVERVIEW["athlete_code"],
                "Metric": metric,
                "Value": details["value"],
                "Status": details["priority"],
            }
        )
    return pd.DataFrame(rows)


def _normalize_dataframe(df):
    if {"Metric", "Value"}.issubset(df.columns):
        normalized = df.copy()
        if "Athlete_Code" not in normalized.columns and "athlete_code" not in normalized.columns:
            normalized["Athlete_Code"] = ATHLETE_OVERVIEW["athlete_code"]
        return normalized

    if "user_id" in df.columns:
        id_col = "user_id"
    elif "Athlete_Code" in df.columns:
        id_col = "Athlete_Code"
    else:
        id_col = None

    if len(df) == 0:
        return _load_demo_long_dataframe()

    first_row = df.iloc[0]
    rows = []
    for metric in BIOMARKER_RANGES.keys():
        slug = metric.lower().replace(" ", "_").replace("-", "-")
        source_col = None
        for col in df.columns:
            normalized_col = str(col).strip().lower()
            if normalized_col == slug or normalized_col == slug.replace(" ", "_"):
                source_col = col
                break
        if source_col is None:
            continue
        rows.append(
            {
                "Athlete_Code": first_row.get(id_col, ATHLETE_OVERVIEW["athlete_code"]) if id_col else ATHLETE_OVERVIEW["athlete_code"],
                "Metric": metric,
                "Value": first_row[source_col],
                "Status": "",
            }
        )
    return pd.DataFrame(rows) if rows else _load_demo_long_dataframe()


def _metric_status(metric, value):
    optimal_low, optimal_high = BIOMARKER_RANGES[metric]["optimal"]
    if optimal_low <= value <= optimal_high:
        return "Optimal", "#16a34a", "#dcfce7"

    distance = min(abs(value - optimal_low), abs(value - optimal_high))
    span = max(optimal_high - optimal_low, 1)
    if distance <= span * 0.25:
        return "Watch", "#f59e0b", "#fef3c7"
    return "Monitor", "#dc2626", "#fee2e2"


def _build_biomarker_gauge(metric, value, optimal_low, optimal_high):
    axis_min = min(0, optimal_low * 0.75)
    axis_max = max(optimal_high * 1.3, value * 1.1)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"font": {"size": 28}},
            title={"text": metric, "font": {"size": 15}},
            gauge={
                "axis": {"range": [axis_min, axis_max], "tickwidth": 1},
                "bar": {"color": "#0f766e"},
                "steps": [
                    {"range": [axis_min, optimal_low], "color": "#fee2e2"},
                    {"range": [optimal_low, optimal_high], "color": "#dcfce7"},
                    {"range": [optimal_high, axis_max], "color": "#fee2e2"},
                ],
                "threshold": {
                    "line": {"color": "#111827", "width": 4},
                    "thickness": 0.8,
                    "value": value,
                },
            },
        )
    )
    fig.update_layout(height=220, margin=dict(l=20, r=20, t=50, b=10))
    return fig


def run_biomarker_tab():
    st.header("InnerAthlete Biomarker Dashboard")
    render_privacy_guardrail()

    hero1, hero2, hero3 = st.columns([1.1, 1, 1.2])
    hero1.metric("Athlete", ATHLETE_OVERVIEW["label"])
    hero2.metric("Phase", ATHLETE_OVERVIEW["phase"])
    hero3.metric("Current Flags", "hs-CRP, Ferritin, Vitamin D")
    st.caption("MVP reference based on your final one-pager and big-number dashboard PDFs, with anonymized athlete identity.")

    uploaded_file = st.file_uploader("Upload anonymized biomarker CSV", type=["csv"], key="biomarker_upload")
    df = _load_demo_long_dataframe()

    if uploaded_file is not None:
        uploaded_df = load_uploaded_csv(uploaded_file)
        missing, findings = validate_demo_upload(uploaded_df, required_columns=[])
        if findings:
            st.error("Upload blocked because the file may contain direct identifiers.")
            for finding in findings:
                st.write(f"- {finding}")
            st.info("Replace identifiers with anonymous codes like `ATH-001` and try again.")
            return
        df = _normalize_dataframe(uploaded_df)
        st.success("Upload accepted. The dashboard is rendering anonymized biomarker values.")
    else:
        st.info("Showing the MVP biomarker layout using anonymized demo values from your PDF references.")

    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df = df.dropna(subset=["Value"])

    gauge_cols = st.columns(3)
    metrics = list(BIOMARKER_RANGES.items())
    for idx, (metric, details) in enumerate(metrics):
        row = df[df["Metric"].str.lower() == metric.lower()]
        value = float(row.iloc[0]["Value"]) if len(row) > 0 else details["value"]
        status, status_color, status_bg = _metric_status(metric, value)
        with gauge_cols[idx % 3]:
            st.plotly_chart(
                _build_biomarker_gauge(metric, value, *details["optimal"]),
                use_container_width=True,
                key=f"gauge_{metric}",
            )
            st.markdown(
                f'<div style="margin-top:-8px;margin-bottom:14px;">'
                f'<span style="background:{status_bg};color:{status_color};padding:4px 8px;'
                f'border-radius:999px;font-size:12px;font-weight:700;">{status}</span> '
                f'<span style="font-size:12px;color:#475569;">Optimal: {details["optimal"][0]}-{details["optimal"][1]} {details["unit"]}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("### Personalized Insights")
    insight_cols = st.columns(len(BIOMARKER_INSIGHTS))
    for column, (title, text) in zip(insight_cols, BIOMARKER_INSIGHTS.items()):
        column.markdown(f"**{title}**")
        column.caption(text)

    st.markdown("### Biomarker Detail Table")
    detail_rows = []
    for metric, details in BIOMARKER_RANGES.items():
        row = df[df["Metric"].str.lower() == metric.lower()]
        value = float(row.iloc[0]["Value"]) if len(row) > 0 else details["value"]
        status, _, _ = _metric_status(metric, value)
        detail_rows.append(
            {
                "Metric": metric,
                "Value": value,
                "Unit": details["unit"],
                "Optimal Range": f"{details['optimal'][0]}-{details['optimal'][1]}",
                "Status": status,
            }
        )
    st.dataframe(pd.DataFrame(detail_rows), use_container_width=True, hide_index=True)

    st.markdown("### IA Action Plan")
    plan_cols = st.columns(3)
    action_items = list(ACTION_PLAN.items())
    for idx, (title, bullets) in enumerate(action_items):
        with plan_cols[idx % 3]:
            st.markdown(f"**{title}**")
            for bullet in bullets:
                st.write(f"- {bullet}")

    template_data = TEMPLATE_PATH.read_text()
    st.download_button("Download anonymized biomarker CSV template", template_data, "innerathlete_biomarker_template.csv")
