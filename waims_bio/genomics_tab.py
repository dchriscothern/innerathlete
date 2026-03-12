import pandas as pd
import plotly.express as px
import streamlit as st

from privacy import render_privacy_guardrail


def run_genomics_tab():
    render_privacy_guardrail(" for genetics")
    st.subheader("Genetic Testing Summary")

    profile = pd.DataFrame(
        [
            {"Domain": "Power Expression", "Signal": "ACTN3 pattern", "Interpretation": "Power-speed leaning"},
            {"Domain": "Soft-Tissue Support", "Signal": "COL5A1 pattern", "Interpretation": "Monitor tendon volume progression"},
            {"Domain": "Recovery Response", "Signal": "IL6 / TNF pattern", "Interpretation": "Bias toward recovery support after dense blocks"},
        ]
    )
    st.dataframe(profile, use_container_width=True, hide_index=True)

    chart_df = pd.DataFrame(
        {
            "Category": ["Power", "Recovery", "Tissue Resilience", "Cognitive Load Tolerance"],
            "Score": [88, 74, 69, 81],
        }
    )
    fig = px.bar(
        chart_df,
        x="Category",
        y="Score",
        color="Score",
        color_continuous_scale=["#d9f99d", "#65a30d", "#14532d"],
        range_y=[0, 100],
    )
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=20), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "Genetics should guide context, not destiny. InnerAthlete uses these signals to personalize recovery "
        "and training conversations rather than to make selection decisions."
    )
