"""
Shared InnerAthlete product-demo views used by investor and practitioner roles.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from innerathlete_content import (
    biomarkers_registry,
    brand_asset,
    cognition_registry,
    genetics_registry,
    recommendations_registry,
    report_contracts_registry,
    workflow_registry,
)
from waims_bio.mvp_content import ACTION_PLAN, ATHLETE_OVERVIEW, BIOMARKER_RANGES, S2_METRICS


BRAND_TEXT = "#070917"
BRAND_MUTED = "#475569"
BRAND_ACCENT = "#0f766e"
BRAND_SURFACE = "#f8fafc"


def _logo_path(theme: str = "dark", lockup: str = "horizontal") -> Path:
    return brand_asset(f"innerathlete-{lockup}-{theme}.svg")


def render_brand_lockup(theme: str = "dark", lockup: str = "horizontal", width: int = 320) -> None:
    logo = _logo_path(theme=theme, lockup=lockup)
    if logo.exists():
        st.image(str(logo), width=width)
    else:
        st.markdown("## InnerAthlete")


def _tag(text: str, color: str = BRAND_ACCENT, bg: str = "#ccfbf1") -> str:
    return (
        f"<span style='display:inline-block;background:{bg};color:{color};"
        f"padding:4px 10px;border-radius:999px;font-size:12px;font-weight:700;margin-right:6px;'>{text}</span>"
    )


def render_performance_map(role: str) -> None:
    render_brand_lockup(theme="dark", lockup="horizontal", width=280)
    st.markdown("### Performance Map")
    st.caption(
        "A privacy-safe product view that combines Blood, DNA, and Brain into one personalized decision layer."
    )

    hero1, hero2, hero3, hero4 = st.columns(4)
    hero1.metric("Profile", ATHLETE_OVERVIEW["label"])
    hero2.metric("Code", ATHLETE_OVERVIEW["athlete_code"])
    hero3.metric("Phase", ATHLETE_OVERVIEW["phase"])
    hero4.metric("Current Focus", "Recovery + Skill Precision")

    st.markdown(
        _tag("Privacy-first") + _tag("Anonymized demo", bg="#dbeafe", color="#1d4ed8") + _tag("Context, not destiny", bg="#ede9fe", color="#6d28d9"),
        unsafe_allow_html=True,
    )

    left, center, right = st.columns(3)
    with left:
        st.markdown("#### Blood")
        st.write("Core biomarkers create a recovery and readiness layer with practical next steps.")
        st.caption("Focus: inflammation, micronutrients, stress physiology, and recovery context.")
    with center:
        st.markdown("#### DNA")
        st.write("Domain-based genetics helps personalize training, recovery, sleep, and nutrition conversations.")
        st.caption("Focus: contextual guidance only, never talent ID or deterministic claims.")
    with right:
        st.markdown("#### Brain")
        st.write("S2-style cognition translates attention, timing, and decision metrics into coaching language.")
        st.caption("Focus: readiness-aware decision making, learning, and reaction quality.")

    st.markdown("### How the Signal Stack Works")
    workflow_cols = st.columns(3)
    for column, step in zip(workflow_cols, workflow_registry()):
        column.markdown(f"**{step['step']}**")
        column.caption(step["description"])

    st.markdown("### Current Performance Priorities")
    priorities = [
        "Support recovery quality before adding more training density.",
        "Use DNA and blood context to guide nutrition and sleep conversations.",
        "Keep cognitive skill progressions short, sharp, and readiness-aware.",
    ]
    for item in priorities:
        st.write(f"- {item}")

    if role == "investor_demo":
        st.info(
            "This hidden view is designed as a product walkthrough: how InnerAthlete turns multimodal inputs into a practical personalized plan."
        )
    elif role == "athlete":
        st.info("Athlete self-service is planned as a later secure layer built on this same report anatomy.")
    else:
        st.info(
            "Practitioner roles see this product layer first, then operational monitoring tabs for readiness, trends, availability, and forecast."
        )


def render_how_it_works() -> None:
    st.markdown("### How It Works")
    st.caption("A clean product story for investor and stakeholder walkthroughs.")

    steps = [
        ("1. Input collection", "Biomarker, DNA, cognition, and wellness signals are gathered through a privacy-first process."),
        ("2. Expert interpretation", "Signals are reviewed with domain context, not treated as isolated one-off numbers."),
        ("3. Structured synthesis", "InnerAthlete connects the pillars into a usable performance map."),
        ("4. Personalized output", "The end product is a practical report and action plan for the right audience."),
    ]
    for title, body in steps:
        st.markdown(f"**{title}**")
        st.write(body)

    st.markdown("### Report Audiences")
    cols = st.columns(3)
    for column, contract in zip(cols, report_contracts_registry()):
        column.markdown(f"**{contract['audience'].title()}**")
        column.caption(f"Tone: {contract['tone'].replace('_', ' ')}")
        for section in contract["sections"][:5]:
            column.write(f"- {section.replace('_', ' ').title()}")


def render_why_it_matters() -> None:
    st.markdown("### Why It Matters")
    st.caption("This view stays product-focused: why the workflow is useful for performance teams and athletes.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Why teams care**")
        st.write("- Brings blood, DNA, and cognition into one practical workflow.")
        st.write("- Turns fragmented results into a consistent story and plan.")
        st.write("- Supports conversations across coaches, science, and medical staff.")
        st.write("- Keeps privacy and role-based access visible in the product itself.")
    with col2:
        st.markdown("**Why athletes care**")
        st.write("- Makes testing outputs easier to understand and act on.")
        st.write("- Connects recovery, sleep, nutrition, and skill work to personal context.")
        st.write("- Keeps the interpretation non-deterministic and human-centered.")
        st.write("- Creates a roadmap toward future athlete self-service and secure report access.")


def render_personalized_plan(role: str) -> None:
    st.markdown("### Personalized Plan")
    st.caption("A shared report-style action layer for investor demos and practitioner workflows.")

    recommendations = recommendations_registry()
    cols = st.columns(2)
    for idx, item in enumerate(recommendations):
        target = cols[idx % 2]
        copy_key = "athlete_copy" if role == "athlete" else "coach_copy" if role == "investor_demo" else "practitioner_copy"
        with target:
            st.markdown(f"**{item['headline']}**")
            st.caption(f"{item['domain']} priority · {item['priority'].title()}")
            st.write(item[copy_key])

    st.markdown("### Pillar-Specific Actions")
    plan_cols = st.columns(3)
    plan_items = list(ACTION_PLAN.items())
    for idx, (title, bullets) in enumerate(plan_items):
        with plan_cols[idx % 3]:
            st.markdown(f"**{title}**")
            for bullet in bullets[:3]:
                st.write(f"- {bullet}")

    st.warning(
        "InnerAthlete guidance is educational and performance-support oriented. It should be interpreted with expert context and appropriate consent workflows."
    )


def render_blood_snapshot() -> None:
    st.markdown("### Blood Snapshot")
    markers = list(BIOMARKER_RANGES.items())[:4]
    cols = st.columns(len(markers))
    for column, (label, details) in zip(cols, markers):
        column.metric(label, f"{details['display']} {details['unit']}")
        column.caption(f"Optimal: {details['optimal'][0]}-{details['optimal'][1]}")

    for marker in biomarkers_registry():
        with st.expander(marker["label"]):
            st.write(marker["athlete_safe_copy"])
            st.caption(marker["monitoring_notes"])
            st.write("Sample context:")
            for note in marker["sample_notes"]:
                st.write(f"- {note}")


def render_dna_snapshot() -> None:
    st.markdown("### DNA Snapshot")
    for domain in genetics_registry():
        with st.container(border=True):
            st.markdown(f"**{domain['domain']}**")
            st.write(domain["athlete_safe_copy"])
            st.caption(domain["caution_copy"])


def render_brain_snapshot() -> None:
    st.markdown("### Brain Snapshot")
    top_metrics = sorted(S2_METRICS, key=lambda item: item["value"], reverse=True)[:4]
    cols = st.columns(len(top_metrics))
    for column, metric in zip(cols, top_metrics):
        column.metric(metric["metric"], f"{metric['value']}%")
        column.caption(metric["band"])

    for metric in cognition_registry():
        with st.expander(metric["metric"]):
            st.write(metric["athlete_safe_copy"])
            st.caption(metric["coach_copy"])
