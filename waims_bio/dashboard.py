import streamlit as st
import pandas as pd
import plotly.express as px
from core.engine import WAIMSEngine
from biomarker_tab import run_biomarker_tab
from cognition_tab import run_cognition_tab

# 1. Page Configuration
st.set_page_config(page_title="WAIMS // BIO-SYNC", layout="wide")

# 2. Initialize Core Engine
engine = WAIMSEngine(athlete_id="Joe Bailey")
meta = engine.get_athlete_meta()

# 3. Sidebar Configuration
with st.sidebar:
    st.title("WAIMS CONTROL")
    st.info(f"System: {meta['status']}")
    st.divider()
    st.subheader("Quick Input")
    s_sleep = st.slider("Sleep Quality", 1, 10, 7)
    e_load = st.number_input("Session RPE", 0, 10, 5)

# 4. Main Header & Key Metrics
st.title("WAIMS // COACH COMMAND")
st.markdown(f"### {meta['name']} | {meta['status']}")

# Calculate live readiness from engine
readiness = engine.get_unified_readiness(sub_wellness=s_sleep, ext_load=e_load * 10)

col1, col2, col3 = st.columns(3)
col1.metric("READINESS", f"{readiness}%")
col2.metric("GENOMIC TYPE", meta['genomic_type'])
col3.metric("RECOVERY RATE", "High (ACTN3-RR)")

st.divider()

# 5. Modular Tab System
tabs = st.tabs(["Performance", "Biomarkers", "Cognition", "Genomics"])

with tabs[0]: # Performance Tab
    st.subheader("Athlete Performance Radar")
    # Visualization logic
    df_radar = pd.DataFrame(dict(
        r=[85, 90, 70, 88, 65],
        theta=['Power','Speed','Endurance','Cognition','Recovery']))
    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#00FFA3')
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig)

with tabs[1]: # Biomarkers Tab
    # This calls your external logic from biomarker_tab.py
    run_biomarker_tab()

with tabs[2]: # Cognition Tab
    # We pass the readiness score so the cognition data reacts to the athlete's state
    run_cognition_tab(readiness)

with tabs[3]: # Genomics Tab
    st.subheader("Genomic Profile")
    st.write(f"Primary Profile: **{meta['genomic_type']}**")
    st.write("Detailed SNP analysis visualization pending.")