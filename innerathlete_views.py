"""
Shared InnerAthlete product and report views.
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
    workflow_registry,
)
from waims_bio.mvp_content import ATHLETE_OVERVIEW, BIOMARKER_RANGES, S2_METRICS


BRAND_ACCENT = "#0f766e"


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


def _card(title: str, body: str, eyebrow: str | None = None, tone: str = "#0f172a") -> str:
    eyebrow_html = (
        f"<div style='font-size:11px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#64748b;margin-bottom:6px;'>{eyebrow}</div>"
        if eyebrow
        else ""
    )
    return (
        "<div style='background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;padding:16px 18px;height:100%;'>"
        f"{eyebrow_html}"
        f"<div style='font-size:17px;font-weight:800;color:{tone};margin-bottom:8px;'>{title}</div>"
        f"<div style='font-size:13px;color:#475569;line-height:1.55;'>{body}</div>"
        "</div>"
    )


def _audience_key(role: str) -> str:
    if role == "athlete":
        return "athlete"
    if role in ("investor_demo", "coach_preview", "medical_preview", "executive_preview"):
        return "coach"
    return "practitioner"


def render_performance_map(role: str) -> None:
    render_brand_lockup(theme="dark", lockup="horizontal", width=280)
    st.markdown("### Performance Map")
    st.caption("A privacy-safe view of how Blood, DNA, and Cognitive combine into one practical performance profile.")

    hero1, hero2, hero3, hero4 = st.columns(4)
    hero1.metric("Profile", ATHLETE_OVERVIEW["label"])
    hero2.metric("Code", ATHLETE_OVERVIEW["athlete_code"])
    hero3.metric("Phase", ATHLETE_OVERVIEW["phase"])
    hero4.metric("Current Focus", "Recovery + Decision Quality")

    st.markdown(
        _tag("Privacy-first") + _tag("Anonymized demo", bg="#dbeafe", color="#1d4ed8") + _tag("Context, not destiny", bg="#ede9fe", color="#6d28d9"),
        unsafe_allow_html=True,
    )

    left, center, right = st.columns(3)
    with left:
        st.markdown(
            _card(
                "Blood",
                "Flags recovery capacity, nutrient support, and stress load so staff can act before performance quality slips.",
                eyebrow="Recovery layer",
                tone="#0f766e",
            ),
            unsafe_allow_html=True,
        )
    with center:
        st.markdown(
            _card(
                "DNA",
                "Frames training response, sleep support, and fueling decisions with domain-level context rather than deterministic claims.",
                eyebrow="Context layer",
                tone="#1d4ed8",
            ),
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            _card(
                "Cognitive",
                "Translates timing, attention, and decision metrics into coaching language that can shape daily demand and skill work.",
                eyebrow="Decision layer",
                tone="#7c3aed",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("### Workflow")
    workflow_cols = st.columns(3)
    for column, step in zip(workflow_cols, workflow_registry()):
        column.markdown(_card(step["step"], step["description"], eyebrow="Signal flow"), unsafe_allow_html=True)

    st.markdown("### Current Priorities")
    p1, p2, p3 = st.columns(3)
    p1.metric("Priority 1", "Recovery")
    p1.caption("Protect sleep quality and reduce avoidable recovery friction.")
    p2.metric("Priority 2", "Fueling")
    p2.caption("Use blood and DNA context to sharpen carbohydrate timing and micronutrient support.")
    p3.metric("Priority 3", "Skill Load")
    p3.caption("Match decision-speed and learning demands to current readiness.")

    if role == "investor_demo":
        st.info("This view shows the product story: multimodal inputs translated into a usable performance plan.")
    elif role == "athlete":
        st.info("This is the foundation for the future athlete self-service experience.")
    else:
        st.info("Practitioner roles see this performance map first, then role-specific coaching, medical, and athlete-report workspaces.")


def render_how_it_works() -> None:
    st.markdown("### How It Works")
    st.caption("A concise product walkthrough for stakeholders, staff, and athletes.")

    steps = [
        ("1. Collect", "Blood, DNA, cognition, and wellness inputs are captured through a privacy-first process."),
        ("2. Interpret", "Signals are reviewed with expert context rather than treated as isolated one-off values."),
        ("3. Integrate", "InnerAthlete connects the pillars into one performance profile."),
        ("4. Act", "Each audience receives a practical plan with the right level of detail."),
    ]
    cols = st.columns(2)
    for idx, (title, body) in enumerate(steps):
        cols[idx % 2].markdown(_card(title, body, eyebrow="Workflow"), unsafe_allow_html=True)

def render_why_it_matters() -> None:
    st.markdown("### Why It Matters")
    st.caption("A professional summary of why the workflow is useful, not a pitch deck.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            _card(
                "For Teams",
                "Combines fragmented testing outputs into one decision layer, improves staff alignment, and supports more consistent athlete conversations.",
                eyebrow="Performance operations",
            ),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            _card(
                "For Athletes",
                "Makes complex inputs understandable, personal, and actionable without turning genetics or biomarkers into deterministic labels.",
                eyebrow="Athlete experience",
            ),
            unsafe_allow_html=True,
        )


def render_personalized_plan(role: str) -> None:
    st.markdown("### Personalized Plan")
    st.caption("A staff-ready action board with priorities, ownership, and execution windows.")

    audience = _audience_key(role)
    copy_key = {
        "athlete": "athlete_copy",
        "coach": "coach_copy",
        "practitioner": "practitioner_copy",
    }[audience]

    recommendations = recommendations_registry()
    top = st.columns(4)
    top[0].metric("Priority now", "Recovery")
    top[1].metric("Primary owner", "Coach + Athlete" if audience != "practitioner" else "Performance staff")
    top[2].metric("Execution window", "Next 7 days")
    top[3].metric("Review cadence", "Daily + weekly")

    lanes = {
        "Do Now": {
            "color": "#dc2626",
            "items": [item for item in recommendations if item["priority"] == "high"][:2],
        },
        "Monitor": {
            "color": "#d97706",
            "items": [item for item in recommendations if item["domain"] in ("Monitoring", "Brain")][:2],
        },
        "Build": {
            "color": "#1d4ed8",
            "items": [item for item in recommendations if item["domain"] in ("Nutrition", "Recovery")][-2:],
        },
    }

    lane_cols = st.columns(3)
    for column, (lane, config) in zip(lane_cols, lanes.items()):
        with column:
            st.markdown(
                f"<div style='font-size:11px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:{config['color']};margin-bottom:10px;'>{lane}</div>",
                unsafe_allow_html=True,
            )
            for item in config["items"]:
                owner = "Coach + Athlete" if item["domain"] in ("Recovery", "Nutrition", "Brain") else "Performance staff"
                horizon = "Immediate" if lane == "Do Now" else ("This week" if lane == "Monitor" else "Build over block")
                st.markdown(
                    _card(
                        item["headline"],
                        item[copy_key],
                        eyebrow=f"{item['domain']} · {owner} · {horizon}",
                    ),
                    unsafe_allow_html=True,
                )

    st.markdown("### Staff Actions")
    action_cols = st.columns(3)
    actions = [
        ("Coach", "Adjust practice density, decision load, and communication cues to match current recovery status."),
        ("Medical", "Track recovery support, collection consistency, and context around blood or wellness changes."),
        ("Athlete", "Execute the basics first: sleep, fueling, hydration, and clean recovery routines."),
    ]
    for column, (title, body) in zip(action_cols, actions):
        column.markdown(_card(title, body, eyebrow="Owner"), unsafe_allow_html=True)

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

    st.markdown("### Interpretation")
    marker_cols = st.columns(2)
    for idx, marker in enumerate(biomarkers_registry()):
        with marker_cols[idx % 2]:
            st.markdown(
                _card(
                    marker["label"],
                    marker["why_it_matters"],
                    eyebrow=marker["category"],
                    tone="#0f766e",
                ),
                unsafe_allow_html=True,
            )
            st.caption(marker["monitoring_notes"])


def render_dna_snapshot(role: str) -> None:
    st.markdown("### DNA Snapshot")
    if role == "athlete":
        st.caption("Short athlete-safe summary after the full DNA profile.")
    elif role == "investor_demo":
        st.caption("Short product-demo summary showing how the DNA layer lands after the main profile.")
    elif role in ("medical", "medical_preview", "sport_scientist"):
        st.caption("Quick medical-facing DNA summary for follow-up and cross-pillar context.")
    else:
        st.caption("Quick coach-facing DNA summary after the full performance profile.")

    domains = genetics_registry()
    top_row = st.columns(3)
    for column, domain in zip(top_row, domains[:3]):
        body = domain["athlete_safe_copy"] if role == "athlete" else domain["practitioner_copy"]
        column.markdown(
            _card(
                domain["domain"],
                body,
                eyebrow=domain["evidence_confidence"].title(),
                tone="#1d4ed8",
            ),
            unsafe_allow_html=True,
        )

    bottom_row = st.columns(2)
    for column, domain in zip(bottom_row, domains[3:]):
        with column:
            body = domain["athlete_safe_copy"] if role == "athlete" else domain["practitioner_copy"]
            st.markdown(
                _card(
                    domain["domain"],
                    body,
                    eyebrow=domain["evidence_confidence"].title(),
                    tone="#1d4ed8",
                ),
                unsafe_allow_html=True,
            )
            with st.expander("Research and interpretation notes"):
                st.caption(domain["caution_copy"])


def render_brain_snapshot() -> None:
    st.markdown("### Cognitive Snapshot")
    top_metrics = sorted(S2_METRICS, key=lambda item: item["value"], reverse=True)[:4]
    cols = st.columns(len(top_metrics))
    for column, metric in zip(cols, top_metrics):
        column.metric(metric["metric"], f"{metric['value']}%")
        column.caption(metric["band"])

    st.markdown("### Coaching Translation")
    card_cols = st.columns(2)
    for idx, metric in enumerate(cognition_registry()):
        with card_cols[idx % 2]:
            st.markdown(
                _card(
                    metric["metric"],
                    metric["coach_copy"],
                    eyebrow="Cognitive performance",
                    tone="#7c3aed",
                ),
                unsafe_allow_html=True,
            )
