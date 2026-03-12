from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from privacy import load_uploaded_csv, render_privacy_guardrail, validate_demo_upload


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "data" / "biomarkers" / "innerathlete_biomarker_template.csv"


def _load_demo_dataframe():
    return pd.read_csv(TEMPLATE_PATH)


def run_biomarker_tab():
    st.header("Biomarker Intelligence")
    render_privacy_guardrail()

    uploaded_file = st.file_uploader("Upload anonymized biomarker CSV", type=["csv"], key="biomarker_upload")
    df = _load_demo_dataframe()

    if uploaded_file is not None:
        uploaded_df = load_uploaded_csv(uploaded_file)
        missing, findings = validate_demo_upload(
            uploaded_df,
            required_columns=["Date", "Metric", "Value", "Status"],
        )

        if missing:
            st.error(f"Missing required columns: {', '.join(missing)}")
            return
        if findings:
            st.error("Upload blocked because the file may contain direct identifiers.")
            for finding in findings:
                st.write(f"- {finding}")
            st.info("Replace identifiers with anonymous codes like `ATH-001` and try again.")
            return

        df = uploaded_df
        st.success("Upload accepted. No obvious direct identifiers were detected.")
    else:
        st.info("Showing InnerAthlete demo biomarker data until you upload an anonymized file.")

    df["Date"] = pd.to_datetime(df["Date"])

    latest = df.sort_values("Date").groupby("Metric", as_index=False).tail(1)
    kpi_columns = st.columns(min(len(latest), 4) or 1)
    for idx, (_, row) in enumerate(latest.iterrows()):
        kpi_columns[idx % len(kpi_columns)].metric(
            label=row["Metric"],
            value=row["Value"],
            delta=row.get("Status", ""),
        )

    st.subheader("Longitudinal biomarker trend")
    fig = px.line(
        df.sort_values("Date"),
        x="Date",
        y="Value",
        color="Metric",
        markers=True,
        color_discrete_sequence=["#0f766e", "#14b8a6", "#f59e0b", "#ef4444"],
    )
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Practitioner readout")
    st.dataframe(df.sort_values(["Metric", "Date"], ascending=[True, False]), use_container_width=True, hide_index=True)

    template_data = TEMPLATE_PATH.read_text()
    st.download_button("Download anonymized biomarker CSV template", template_data, "innerathlete_biomarker_template.csv")
