import streamlit as st
import pandas as pd
import plotly.express as px
from core.engine import WAIMSEngine
from biomarker_tab import run_biomarker_tab

# 1. Page Config
st.set_page_config(page_title="WAIMS // BIO-SYNC", layout="wide")

# 2. Initialize Engine
engine = WAIMSEngine(athlete_id="Joe Bailey")
meta = engine.get_athlete_meta()

# 3. Sidebar Inputs
with st.sidebar:
    st.title("ATHLETE INPUT")
    st.subheader("Subjective Monitoring")
    s_sleep = st.slider("Sleep Quality", 1, 10, 7)
    s_soreness = st.slider("Muscle Soreness", 1, 10, 5)
    
    st.divider()
    st.subheader("External Load")
    e_intensity = st.number_input("Session RPE", 0, 10, 5)

# 4. Main UI Header
st.title("WAIMS // COACH COMMAND")
st.markdown(f"### {meta['name']} | {meta['status']}")

# 5. Top Level Metrics
readiness = engine.get_unified_readiness(sub_wellness=s_sleep, ext_load=e_intensity * 10)

col1, col2, col3 = st.columns(3)
col1.metric("READINESS", f"{readiness}%", delta="Stable")
col2.metric("GENOMIC TYPE", meta['genomic_type'])
col3.metric("RECOVERY RATE", "High (ACTN3-RR)")

st.divider()

# 6. Tabs System
tabs = st.tabs(["Profile", "Genomics", "Biomarkers", "S2 Cognition", "Load Analysis"])

with tabs[0]: # Profile Tab (Replacement for the missing module)
    st.subheader("Athlete Performance Radar")
    
    # Simple Radar Chart Data
    df_radar = pd.DataFrame(dict(
        r=[80, 90, 70, 85, 60],
        theta=['Power','Speed','Endurance','Cognition','Recovery']))
    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#00FFA3')
    st.plotly_chart(fig)

with tabs[1]:
    st.subheader("Genetic Marker Analysis")
    st.info("Awaiting genomic CSV upload...")

with tabs[3]:
    st.subheader("S2 Cognition Metrics")
    st.write("Tracking: 92% | Perception: 48% (Fatigued)")