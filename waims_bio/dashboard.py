import streamlit as st
import pandas as pd
from core.engine import WAIMSEngine
from biomarker_tab import run_biomarker_tab

# 1. Setup
st.set_page_config(page_title="WAIMS // BIO-SYNC", layout="wide")

# 2. Connection to Engine
engine = WAIMSEngine(athlete_id="Joe Bailey")
meta = engine.get_athlete_meta()

# 3. Sidebar
with st.sidebar:
    st.title("WAIMS CONTROL")
    st.info(f"System: {meta['status']}")

# 4. Dashboard Header
st.title("WAIMS // COACH COMMAND")
st.divider()

# 5. Modular Tabs
tabs = st.tabs(["Performance", "Biomarkers", "Cognition", "Genomics"])

with tabs[0]:
    st.subheader("Athlete Overview")
    st.write("Welcome to the WAIMS Performance Portal.")

with tabs[1]:
    # This calls the file you created earlier
    run_biomarker_tab()

with tabs[2]:
    st.subheader("S2 Cognition")
    st.warning("Module under development.")

with tabs[3]:
    st.subheader("Genomic Analysis")
    st.write("Raw genomic data processing pending.")