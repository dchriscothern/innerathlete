from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from biomarker_tab import run_biomarker_tab
from cognition_tab import run_cognition_tab
from core.engine import WAIMSEngine
from genomics_tab import run_genomics_tab


BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="InnerAthlete Intelligence Hub", layout="wide")

engine = WAIMSEngine()
meta = engine.get_org_meta()

with st.sidebar:
    st.title("InnerAthlete")
    st.caption("Privacy-first demo workspace")
    st.success(meta["status"])
    st.divider()
    recovery_score = st.slider("Recovery check-in", 1, 10, 7)
    load_score = st.slider("Training load balance", 1, 10, 6)
    biomarker_score = st.slider("Biomarker stability", 1, 100, 82)
    st.divider()
    st.caption("Only anonymized sample files should be uploaded into this demo.")

readiness = engine.get_unified_readiness(
    recovery_score=recovery_score,
    load_score=load_score,
    biomarker_score=biomarker_score,
)

hero_left, hero_right = st.columns([1.4, 1.0])

with hero_left:
    st.title(meta["company"])
    st.subheader(meta["tagline"])
    st.write(
        "This demo site frames InnerAthlete as a performance intelligence company built around "
        "biomarker monitoring, genetic testing, and S2-style cognition testing. All examples in this workspace "
        "should remain anonymized and portfolio-safe."
    )

with hero_right:
    st.metric("Composite readiness", f"{readiness}%")
    st.metric("Program focus", meta["program_focus"])

card_columns = st.columns(3)
for column, card in zip(card_columns, engine.get_program_cards()):
    column.markdown(f"### {card['title']}")
    column.metric(card["title"], card["value"])
    column.caption(card["detail"])

st.divider()

overview = pd.DataFrame(
    {
        "Pillar": ["Biomarkers", "Genetics", "S2 Cognition", "Recovery Workflow"],
        "Maturity": [86, 74, 81, 79],
    }
)
overview_fig = px.area(
    overview,
    x="Pillar",
    y="Maturity",
    markers=True,
    color_discrete_sequence=["#0f766e"],
)
overview_fig.update_layout(height=300, margin=dict(l=10, r=10, t=20, b=10))
st.plotly_chart(overview_fig, use_container_width=True)

tabs = st.tabs(["Program Overview", "Biomarkers", "S2 Cognition", "Genetics"])

with tabs[0]:
    st.subheader("How InnerAthlete positions the platform")
    st.write(
        "InnerAthlete combines longitudinal biomarker trends, genetic context, and S2 cognition testing to help "
        "practitioners understand recovery readiness, neurocognitive stress, and individualized training response."
    )
    st.markdown(
        """
        - Biomarkers support recovery, inflammation, endocrine, and micronutrient decision-making.
        - Genetic testing adds context for power profile, connective-tissue support, and recovery tendencies.
        - S2 cognition testing helps flag perceptual load, tracking speed, and decision strain under fatigue.
        - Coaches and operators should only work from de-identified athlete codes in this demo environment.
        """
    )

    biomarker_template = (BASE_DIR / "data" / "biomarkers" / "innerathlete_biomarker_template.csv").read_text()
    cognition_template = (BASE_DIR / "data" / "cognitive" / "innerathlete_cognition_template.csv").read_text()

    dl_col1, dl_col2 = st.columns(2)
    dl_col1.download_button(
        "Download biomarker template",
        biomarker_template,
        file_name="innerathlete_biomarker_template.csv",
    )
    dl_col2.download_button(
        "Download cognition template",
        cognition_template,
        file_name="innerathlete_cognition_template.csv",
    )

    st.warning(
        "Before adding any example files, strip names, DOB, contact details, team identifiers, and medical record numbers. "
        "Use synthetic or anonymized IDs such as `ATH-001`."
    )

with tabs[1]:
    run_biomarker_tab()

with tabs[2]:
    run_cognition_tab(readiness)

with tabs[3]:
    run_genomics_tab()
