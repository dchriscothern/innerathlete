from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from privacy import render_privacy_guardrail


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "data" / "cognitive" / "innerathlete_cognition_template.csv"


def run_cognition_tab(readiness_score):
    render_privacy_guardrail(" for cognition")
    st.subheader("S2 Cognition Testing")

    readiness_adjustment = max(0, (100 - readiness_score) * 0.5)
    tracking = round(min(99, 90 + (readiness_score - 75) * 0.12), 1)
    perception_speed = round(235 + readiness_adjustment, 1)
    decision_load = round(min(99, 78 + readiness_score * 0.1), 1)

    col1, col2, col3 = st.columns(3)
    col1.metric("Tracking accuracy", f"{tracking}%")
    col2.metric("Perception speed", f"{perception_speed} ms", delta=f"{235 - perception_speed:.1f}", delta_color="inverse")
    col3.metric("Decision efficiency", f"{decision_load}%")

    st.caption("S2-style outputs are shown as anonymized demo examples rather than real athlete testing records.")

    cognition_data = pd.read_csv(TEMPLATE_PATH)
    fig = px.line(
        cognition_data,
        x="Session_Date",
        y=["Tracking_Accuracy", "Decision_Complexity", "Inhibition_Control"],
        markers=True,
        color_discrete_sequence=["#1d4ed8", "#0f766e", "#9333ea"],
    )
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10), legend_title_text="Metric")
    st.plotly_chart(fig, use_container_width=True)

    reaction_fig = px.bar(
        cognition_data,
        x="Session_Date",
        y="Perception_Speed_ms",
        color="Perception_Speed_ms",
        color_continuous_scale=["#dcfce7", "#86efac", "#15803d"],
    )
    reaction_fig.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=10), coloraxis_showscale=False)
    st.plotly_chart(reaction_fig, use_container_width=True)

    if readiness_score < 70:
        st.warning("Cognitive strain is elevated in this scenario. InnerAthlete would typically recommend lighter decision-load work and repeat testing.")
    else:
        st.success("Current demo profile suggests stable perceptual processing and decision efficiency.")
