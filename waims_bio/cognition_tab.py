import streamlit as st
import pandas as pd
import plotly.express as px

def run_cognition_tab(readiness_score):
    st.subheader("🧠 S2 Cognition Metrics")
    
    # Simulate S2 Metrics based on Readiness
    # If readiness is low, Perception Speed "drops"
    base_perception = 92 
    current_perception = base_perception * (readiness_score / 100)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Tracking Capacity", "88th %", delta="Stable")
    col2.metric("Perception Speed", f"{current_perception:.1f} ms", 
                delta=f"{current_perception - base_perception:.1f}", delta_color="inverse")
    col3.metric("Decision Complexity", "High", delta="Elite")

    st.divider()
    
    # Trend Data Visualization
    st.write("### Cognitive Load vs. Reaction Time")
    cognition_data = pd.DataFrame({
        "Session": [1, 2, 3, 4, 5],
        "Reaction Time (ms)": [240, 235, 255, 280, 245],
        "Impulsivity": [12, 10, 15, 22, 11]
    })
    
    fig = px.bar(cognition_data, x="Session", y="Reaction Time (ms)", 
                 color="Impulsivity", color_continuous_scale="Viridis")
    fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    if readiness_score < 70:
        st.warning("⚠️ High Cognitive Fatigue detected. Perception Speed is currently inhibited.")