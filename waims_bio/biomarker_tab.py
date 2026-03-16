from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    from innerathlete_content import biomarkers_registry, recommendations_registry
except ImportError:
    biomarkers_registry = None
    recommendations_registry = None

try:
    from .mvp_content import ATHLETE_OVERVIEW, BIOMARKER_INSIGHTS, BIOMARKER_RANGES
    from .privacy import load_uploaded_csv, render_privacy_guardrail, validate_demo_upload
except ImportError:
    from mvp_content import ATHLETE_OVERVIEW, BIOMARKER_INSIGHTS, BIOMARKER_RANGES
    from privacy import load_uploaded_csv, render_privacy_guardrail, validate_demo_upload


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "data" / "biomarkers" / "innerathlete_biomarker_template.csv"

STATUS_ORDER = {"Monitor": 0, "Watch": 1, "Optimal": 2}
STATUS_META = {
    "Monitor": {"color": "#dc2626", "bg": "#fee2e2", "label": "Needs immediate attention"},
    "Watch": {"color": "#d97706", "bg": "#fef3c7", "label": "Manage and review closely"},
    "Optimal": {"color": "#16a34a", "bg": "#dcfce7", "label": "Within current target band"},
}


def _load_demo_long_dataframe():
    rows = []
    for metric, details in BIOMARKER_RANGES.items():
        rows.append(
            {
                "Athlete_Code": ATHLETE_OVERVIEW["athlete_code"],
                "Metric": metric,
                "Value": details["value"],
                "Status": details["priority"],
            }
        )
    return pd.DataFrame(rows)


def _normalize_dataframe(df):
    if {"Metric", "Value"}.issubset(df.columns):
        normalized = df.copy()
        if "Athlete_Code" not in normalized.columns and "athlete_code" not in normalized.columns:
            normalized["Athlete_Code"] = ATHLETE_OVERVIEW["athlete_code"]
        return normalized

    if "user_id" in df.columns:
        id_col = "user_id"
    elif "Athlete_Code" in df.columns:
        id_col = "Athlete_Code"
    else:
        id_col = None

    if len(df) == 0:
        return _load_demo_long_dataframe()

    first_row = df.iloc[0]
    rows = []
    for metric in BIOMARKER_RANGES.keys():
        slug = metric.lower().replace(" ", "_")
        source_col = None
        for col in df.columns:
            normalized_col = str(col).strip().lower()
            if normalized_col == slug:
                source_col = col
                break
        if source_col is None:
            continue
        rows.append(
            {
                "Athlete_Code": first_row.get(id_col, ATHLETE_OVERVIEW["athlete_code"]) if id_col else ATHLETE_OVERVIEW["athlete_code"],
                "Metric": metric,
                "Value": first_row[source_col],
                "Status": "",
            }
        )
    return pd.DataFrame(rows) if rows else _load_demo_long_dataframe()


def _metric_status(metric, value):
    optimal_low, optimal_high = BIOMARKER_RANGES[metric]["optimal"]
    if optimal_low <= value <= optimal_high:
        return "Optimal", "#16a34a", "#dcfce7"

    distance = min(abs(value - optimal_low), abs(value - optimal_high))
    span = max(optimal_high - optimal_low, 1)
    if distance <= span * 0.25:
        return "Watch", "#f59e0b", "#fef3c7"
    return "Monitor", "#dc2626", "#fee2e2"


def _build_biomarker_gauge(metric, value, optimal_low, optimal_high):
    axis_min = min(0, optimal_low * 0.75)
    axis_max = max(optimal_high * 1.3, value * 1.1)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"font": {"size": 28}},
            title={"text": metric, "font": {"size": 15}},
            gauge={
                "axis": {"range": [axis_min, axis_max], "tickwidth": 1},
                "bar": {"color": "#0f766e"},
                "steps": [
                    {"range": [axis_min, optimal_low], "color": "#fee2e2"},
                    {"range": [optimal_low, optimal_high], "color": "#dcfce7"},
                    {"range": [optimal_high, axis_max], "color": "#fee2e2"},
                ],
                "threshold": {
                    "line": {"color": "#111827", "width": 4},
                    "thickness": 0.8,
                    "value": value,
                },
            },
        )
    )
    fig.update_layout(height=220, margin=dict(l=20, r=20, t=50, b=10))
    return fig


def _meter_html(metric, value, low, high, unit, status, status_color, status_bg):
    span = max(high - low, 1)
    meter_min = max(0.0, low - span)
    meter_max = high + span
    pct = max(0, min(100, ((value - meter_min) / max(meter_max - meter_min, 1)) * 100))
    low_pct = ((low - meter_min) / max(meter_max - meter_min, 1)) * 100
    high_pct = ((high - meter_min) / max(meter_max - meter_min, 1)) * 100
    zone_width = max(high_pct - low_pct, 2)

    return (
        f"<div style='background:{status_bg};border:1px solid #e2e8f0;border-left:6px solid {status_color};border-radius:14px;padding:16px 18px;margin-bottom:12px;'>"
        "<div style='display:flex;justify-content:space-between;align-items:flex-start;gap:10px;'>"
        f"<div><div style='font-size:16px;font-weight:800;color:#0f172a;'>{metric}</div>"
        f"<div style='font-size:12px;color:#64748b;margin-top:4px;'>Optimal {low:g}-{high:g} {unit}</div></div>"
        f"<div style='text-align:right;'><div style='font-size:22px;font-weight:800;color:#0f172a;'>{value:g}</div>"
        f"<div style='font-size:11px;color:#64748b;'>{unit}</div></div></div>"
        "<div style='margin-top:14px;position:relative;padding-top:24px;'>"
        f"<div style='position:absolute;left:calc({pct:.1f}% - 26px);top:0;background:#ffffff;color:{status_color};border:1px solid {status_color}55;"
        "border-radius:999px;padding:3px 8px;font-size:11px;font-weight:800;min-width:52px;text-align:center;box-shadow:0 1px 2px rgba(15,23,42,0.08);'>"
        f"{value:g}</div>"
        "<div style='position:relative;height:16px;background:#e5e7eb;border-radius:999px;overflow:hidden;border:1px solid #d1d5db;'>"
        f"<div style='position:absolute;left:0;width:{low_pct:.1f}%;top:0;bottom:0;background:#fecaca;'></div>"
        f"<div style='position:absolute;left:{low_pct:.1f}%;width:{zone_width:.1f}%;top:0;bottom:0;background:#86efac;'></div>"
        f"<div style='position:absolute;left:{high_pct:.1f}%;right:0;top:0;bottom:0;background:#fecaca;'></div>"
        f"<div style='position:absolute;left:calc({pct:.1f}% - 2px);top:-2px;bottom:-2px;width:4px;background:{status_color};border-radius:999px;box-shadow:0 1px 3px rgba(15,23,42,0.18);'></div>"
        "</div>"
        "<div style='display:flex;justify-content:space-between;gap:8px;margin-top:8px;font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.04em;'>"
        "<span>Below</span><span>Optimal</span><span>Above</span></div>"
        "</div>"
        "<div style='display:flex;justify-content:space-between;align-items:center;margin-top:10px;'>"
        f"<span style='background:#ffffff;color:{status_color};padding:4px 9px;border-radius:999px;font-size:11px;font-weight:800;border:1px solid {status_color}33;'>{status}</span>"
        "<span style='font-size:12px;color:#475569;'>Trend over single value</span></div>"
        "</div>"
    )


def _summary_card(title: str, value: str, detail: str, accent: str) -> str:
    return (
        "<div style='background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;padding:16px 18px;height:100%;'>"
        f"<div style='font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:{accent};margin-bottom:6px;'>{title}</div>"
        f"<div style='font-size:24px;font-weight:800;color:#0f172a;margin-bottom:6px;'>{value}</div>"
        f"<div style='font-size:13px;color:#475569;line-height:1.55;'>{detail}</div>"
        "</div>"
    )


def _section_header(title: str, subtitle: str, color: str, bg: str, count: int) -> str:
    return (
        "<div style='display:flex;justify-content:space-between;align-items:center;"
        f"background:{bg};border:1px solid {bg};border-radius:14px;padding:12px 14px;margin-bottom:12px;'>"
        f"<div><div style='font-size:12px;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;color:{color};'>{title}</div>"
        f"<div style='font-size:12px;color:#475569;margin-top:4px;'>{subtitle}</div></div>"
        f"<div style='font-size:24px;font-weight:800;color:{color};'>{count}</div>"
        "</div>"
    )


def _action_card(title: str, priority: str, owner: str, horizon: str, body: str, color: str) -> str:
    return (
        "<div style='background:#ffffff;border:1px solid #e2e8f0;border-top:4px solid "
        f"{color};border-radius:14px;padding:16px 18px;height:100%;margin-bottom:12px;'>"
        f"<div style='font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:{color};margin-bottom:6px;'>{priority} | {owner} | {horizon}</div>"
        f"<div style='font-size:16px;font-weight:800;color:#0f172a;margin-bottom:8px;'>{title}</div>"
        f"<div style='font-size:13px;color:#475569;line-height:1.55;'>{body}</div>"
        "</div>"
    )


def _detail_note_html(title: str, body: str) -> str:
    return (
        "<div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:14px 16px;height:100%;'>"
        f"<div style='font-size:13px;font-weight:800;color:#0f172a;margin-bottom:6px;'>{title}</div>"
        f"<div style='font-size:12px;color:#475569;line-height:1.55;'>{body}</div>"
        "</div>"
    )


def _top_focus_metrics(detail_rows, count: int = 3):
    focus = [row for row in detail_rows if row[3] != "Optimal"]
    if len(focus) < count:
        remaining = [row for row in detail_rows if row not in focus]
        focus.extend(remaining[: count - len(focus)])
    return focus[:count]


def _audience_from_role(role: str | None) -> str:
    if role == "athlete":
        return "athlete"
    if role == "investor_demo":
        return "investor"
    if role in {"coach_preview", "head_coach", "asst_coach", "executive_preview", "gm"}:
        return "coach"
    if role in {"medical_preview", "medical", "sport_scientist"}:
        return "medical"
    return "practitioner"


def _build_action_plan(detail_rows, role: str | None):
    audience = _audience_from_role(role)
    flagged = [item for item in detail_rows if item[3] != "Optimal"]
    flagged_metrics = [item[0] for item in flagged]

    has_recovery = any(metric in {"hs-CRP", "Cortisol", "Testosterone"} for metric in flagged_metrics)
    has_fueling = any(metric in {"Vitamin D", "Ferritin", "Glucose"} for metric in flagged_metrics)

    primary_focus = "Recovery Load" if has_recovery else "Performance Maintenance"
    secondary_focus = "Fueling + Micronutrients" if has_fueling else "Collection Consistency"
    owner_today = {
        "coach": "Coach + Performance",
        "medical": "Medical + Performance",
        "athlete": "Athlete + Support Staff",
        "investor": "InnerAthlete workflow",
        "practitioner": "Performance staff",
    }[audience]
    review_cadence = {
        "coach": "Daily check-in, weekly review",
        "medical": "Daily context, next draw review",
        "athlete": "Daily habits, next support touchpoint",
        "investor": "Signal to plan in one workflow",
        "practitioner": "Daily check-in, weekly review",
    }[audience]

    recommendations = recommendations_registry() if recommendations_registry else []
    coach_sleep = recommendations[0]["coach_copy"] if recommendations else "Protect sleep quality and keep recovery messaging simple."
    practitioner_nutrition = recommendations[1]["practitioner_copy"] if len(recommendations) > 1 else "Use blood context, training phase, and behavior before adding supplements."
    monitor_copy = recommendations[3]["practitioner_copy"] if len(recommendations) > 3 else "Anchor decisions to baselines, timing, context, and repeated measures."

    lane_map = {
        "coach": {
            "Today": {
                "color": "#dc2626",
                "detail": "How the session and message should change right now.",
                "items": [
                    {"title": "Adjust session density", "owner": "Coach", "horizon": "Today", "body": "Protect quality over volume when recovery markers are elevated. Keep decision-making work sharp, not excessive."},
                    {"title": "Recovery message to athlete", "owner": "Coach", "horizon": "Today", "body": coach_sleep},
                ],
            },
            "This Week": {
                "color": "#d97706",
                "detail": "Support habits that reinforce the current blood profile.",
                "items": [
                    {"title": "Fuel around workload", "owner": "Performance + Athlete", "horizon": "This week", "body": practitioner_nutrition},
                    {"title": "Keep the basics consistent", "owner": "Athlete", "horizon": "Daily", "body": "Sleep timing, hydration, and post-session nutrition should be stable before anything more advanced is added."},
                ],
            },
            "Track": {
                "color": "#1d4ed8",
                "detail": "What staff should review before changing the next block.",
                "items": [
                    {"title": "Trend the blood picture", "owner": "Coach + Medical", "horizon": "7-14 days", "body": monitor_copy},
                    {"title": "Link blood to readiness", "owner": "Performance", "horizon": "Daily", "body": "Use blood signals alongside sleep, wellness, and training load instead of treating any one value as the whole story."},
                ],
            },
        },
        "medical": {
            "Today": {
                "color": "#dc2626",
                "detail": "Clinical-style context without turning the page into a diagnosis tool.",
                "items": [
                    {"title": "Frame the signal correctly", "owner": "Medical", "horizon": "Today", "body": "Use blood markers as context for recovery and follow-up, not as standalone conclusions."},
                    {"title": "Support coach-facing guidance", "owner": "Medical + Coach", "horizon": "Today", "body": "Translate the current panel into simple training guidance rather than raw lab language."},
                ],
            },
            "This Week": {
                "color": "#d97706",
                "detail": "What should be tightened operationally before the next panel.",
                "items": [
                    {"title": "Standardize collection conditions", "owner": "Medical", "horizon": "Next draw", "body": "Keep timing, posture, hydration, and training proximity consistent so the next panel is decision-useful."},
                    {"title": "Reinforce nutrition support", "owner": "Medical + Athlete", "horizon": "This week", "body": practitioner_nutrition},
                ],
            },
            "Track": {
                "color": "#1d4ed8",
                "detail": "The review layer behind the immediate staff conversation.",
                "items": [
                    {"title": "Anchor to symptoms and trend", "owner": "Medical", "horizon": "7-14 days", "body": monitor_copy},
                    {"title": "Connect blood to broader context", "owner": "Medical + Performance", "horizon": "Weekly", "body": "Review biomarkers with recovery history, current load, wellness notes, and any repeat testing."},
                ],
            },
        },
        "athlete": {
            "Today": {
                "color": "#dc2626",
                "detail": "The two things that matter most right away.",
                "items": [
                    {"title": "Sleep and recover on purpose", "owner": "Athlete", "horizon": "Tonight", "body": "Treat sleep like training. Protect bedtime, hydration, and your post-workout routine."},
                    {"title": "Do not chase extras first", "owner": "Athlete", "horizon": "Today", "body": "Get the basics right before adding advanced recovery tools or supplements."},
                ],
            },
            "This Week": {
                "color": "#d97706",
                "detail": "Habits that help the current blood picture improve.",
                "items": [
                    {"title": "Fuel for training quality", "owner": "Athlete", "horizon": "This week", "body": "Use consistent carbohydrate timing and nutrient-dense meals to support energy and recovery."},
                    {"title": "Stay consistent", "owner": "Athlete", "horizon": "Daily", "body": "One perfect day will not move the trend. Repeating good habits is what changes the profile."},
                ],
            },
            "Track": {
                "color": "#1d4ed8",
                "detail": "How to think about the next review.",
                "items": [
                    {"title": "Look for trends", "owner": "Athlete + Staff", "horizon": "Next review", "body": "Your profile is more useful across time than from one single test result."},
                    {"title": "Ask better questions", "owner": "Athlete", "horizon": "Next check-in", "body": "Use the next conversation to understand what changed, what helped, and what still needs work."},
                ],
            },
        },
        "investor": {
            "Signal": {
                "color": "#dc2626",
                "detail": "What the blood layer identifies quickly.",
                "items": [
                    {"title": "Flag meaningful priorities", "owner": "InnerAthlete", "horizon": "Instant", "body": "The product surfaces the few biomarker signals that matter most right now instead of handing over a raw lab sheet."},
                    {"title": "Make the result readable", "owner": "InnerAthlete", "horizon": "Instant", "body": "Status color, target band, and meter position let coaches and athletes understand the panel in seconds."},
                ],
            },
            "Workflow": {
                "color": "#d97706",
                "detail": "How the blood page moves from result to decision.",
                "items": [
                    {"title": "Turn data into ownership", "owner": "Platform", "horizon": "Workflow", "body": "Each flagged signal is translated into a staff-ready plan with role clarity, cadence, and next actions."},
                    {"title": "Support different audiences", "owner": "Platform", "horizon": "Workflow", "body": "The same biomarker layer can speak to coaches, medical staff, and athletes without creating three separate systems."},
                ],
            },
            "Outcome": {
                "color": "#1d4ed8",
                "detail": "Why this is useful as a product experience.",
                "items": [
                    {"title": "Improve decision quality", "owner": "Staff", "horizon": "Ongoing", "body": "The point is not more data. The point is faster, clearer, better decisions around recovery, fueling, and readiness."},
                    {"title": "Create a report worth using", "owner": "Athlete + Team", "horizon": "Ongoing", "body": "A blood report becomes valuable when it is easy to read, role-aware, and tied to action instead of static interpretation."},
                ],
            },
        },
        "practitioner": {
            "Today": {
                "color": "#dc2626",
                "detail": "Immediate interpretation and response.",
                "items": [
                    {"title": "Prioritize the main signal", "owner": "Performance", "horizon": "Today", "body": "Use the flagged biomarker pattern to shape the next conversation and the next practice decision."},
                    {"title": "Reinforce the first-line intervention", "owner": "Performance + Athlete", "horizon": "Today", "body": coach_sleep},
                ],
            },
            "This Week": {
                "color": "#d97706",
                "detail": "Support choices that stabilize the profile.",
                "items": [
                    {"title": "Nutrition and micronutrient support", "owner": "Performance", "horizon": "This week", "body": practitioner_nutrition},
                    {"title": "Protect collection quality", "owner": "Medical", "horizon": "Next draw", "body": "Keep collection conditions tight so repeated measures can actually be compared."},
                ],
            },
            "Track": {
                "color": "#1d4ed8",
                "detail": "Longitudinal review and handoff.",
                "items": [
                    {"title": "Trend, do not chase noise", "owner": "Performance", "horizon": "7-14 days", "body": monitor_copy},
                    {"title": "Merge blood with readiness", "owner": "Staff", "horizon": "Weekly", "body": "Connect biomarkers to training load, wellness, and cognition when shaping the next block."},
                ],
            },
        },
    }

    return {
        "primary_focus": primary_focus,
        "secondary_focus": secondary_focus,
        "owner_today": owner_today,
        "review_cadence": review_cadence,
        "lanes": lane_map[audience],
        "audience": audience,
    }


def run_biomarker_tab(role: str | None = None):
    audience = _audience_from_role(role)
    st.header("InnerAthlete Biomarker Dashboard")
    render_privacy_guardrail()

    hero1, hero2, hero3 = st.columns([1.1, 1, 1.2])
    hero1.metric("Athlete", ATHLETE_OVERVIEW["label"])
    hero2.metric("Phase", ATHLETE_OVERVIEW["phase"])
    hero3.metric("Current Flags", "hs-CRP, Ferritin, Vitamin D")
    st.caption("Professional blood view for staff review, athlete reporting, and role-specific action planning.")

    uploaded_file = st.file_uploader("Upload anonymized biomarker CSV", type=["csv"], key="biomarker_upload")
    df = _load_demo_long_dataframe()

    if uploaded_file is not None:
        uploaded_df = load_uploaded_csv(uploaded_file)
        missing, findings = validate_demo_upload(uploaded_df, required_columns=[])
        if findings:
            st.error("Upload blocked because the file may contain direct identifiers.")
            for finding in findings:
                st.write(f"- {finding}")
            st.info("Replace identifiers with anonymous codes like `ATH-001` and try again.")
            return
        df = _normalize_dataframe(uploaded_df)
        st.success("Upload accepted. The dashboard is rendering anonymized biomarker values.")
    else:
        st.info("Showing the InnerAthlete blood layout using anonymized demo values.")

    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df = df.dropna(subset=["Value"])

    detail_rows = []
    for metric, details in BIOMARKER_RANGES.items():
        row = df[df["Metric"].str.lower() == metric.lower()]
        value = float(row.iloc[0]["Value"]) if len(row) > 0 else details["value"]
        status, status_color, status_bg = _metric_status(metric, value)
        detail_rows.append((metric, value, details, status, status_color, status_bg))

    detail_rows = sorted(detail_rows, key=lambda item: STATUS_ORDER[item[3]])
    sections = {"Monitor": [], "Watch": [], "Optimal": []}
    for item in detail_rows:
        sections[item[3]].append(item)

    if audience in {"athlete", "investor"}:
        summary_title = "Athlete Blood Summary" if audience == "athlete" else "Blood Summary"
        summary_caption = (
            "A few headline signals with simplified reading before the detailed breakdown."
            if audience == "athlete"
            else "A clean product-demo summary showing how the blood layer surfaces the most important signals."
        )
        st.markdown(f"### {summary_title}")
        st.caption(summary_caption)
        gauge_cols = st.columns(3)
        for idx, (metric, value, details, status, status_color, status_bg) in enumerate(_top_focus_metrics(detail_rows, 3)):
            with gauge_cols[idx]:
                st.plotly_chart(
                    _build_biomarker_gauge(metric, value, *details["optimal"]),
                    use_container_width=True,
                    key=f"gauge_{audience}_{metric}",
                )
                st.markdown(
                    f'<div style="margin-top:-8px;margin-bottom:14px;">'
                    f'<span style="background:{status_bg};color:{status_color};padding:4px 8px;'
                    f'border-radius:999px;font-size:12px;font-weight:700;">{status}</span> '
                    f'<span style="font-size:12px;color:#475569;">Optimal: {details["optimal"][0]:g}-{details["optimal"][1]:g} {details["unit"]}</span>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
    else:
        st.markdown("### Blood Status Overview")
        st.caption("Built for fast staff scanning: see the red, amber, and green picture first, then go to the detailed board.")
        summary_cols = st.columns(3)
        for column, status in zip(summary_cols, ["Monitor", "Watch", "Optimal"]):
            meta = STATUS_META[status]
            subtitle = meta["label"]
            if status == "Monitor":
                subtitle = "What needs immediate attention today."
            elif status == "Watch":
                subtitle = "What needs management and review this week."
            else:
                subtitle = "What can stay stable while focus goes elsewhere."
            column.markdown(
                _summary_card(status, str(len(sections[status])), subtitle, meta["color"]),
                unsafe_allow_html=True,
            )

    st.markdown("### Performance Insights")
    if audience == "athlete":
        athlete_cols = st.columns(3)
        athlete_insights = [
            ("Recovery", BIOMARKER_INSIGHTS["Recovery & Resilience"]),
            ("Sleep", BIOMARKER_INSIGHTS["Sleep"]),
            ("Fueling", BIOMARKER_INSIGHTS["Nutrition & Vitamins"]),
        ]
        for column, (title, text) in zip(athlete_cols, athlete_insights):
            column.markdown(f"**{title}**")
            column.caption(text)
    else:
        insight_cols = st.columns(len(BIOMARKER_INSIGHTS))
        for column, (title, text) in zip(insight_cols, BIOMARKER_INSIGHTS.items()):
            column.markdown(f"**{title}**")
            column.caption(text)

    st.markdown("### Biomarker Detail Board")
    st.caption(
        "Color groups are ordered by urgency so staff can scan red, then amber, then green."
        if audience not in {"athlete", "investor"}
        else "Detailed marker view with color-coded bands and simplified reading."
    )

    section_cols = st.columns(3)
    for column, status in zip(section_cols, ["Monitor", "Watch", "Optimal"]):
        meta = STATUS_META[status]
        items = sections[status]
        with column:
            st.markdown(_section_header(status, meta["label"], meta["color"], meta["bg"], len(items)), unsafe_allow_html=True)
            max_items = len(items)
            if audience == "athlete" and status == "Optimal":
                max_items = min(len(items), 2)
            for metric, value, details, metric_status, status_color, status_bg in items[:max_items]:
                st.markdown(
                    _meter_html(
                        metric,
                        value,
                        details["optimal"][0],
                        details["optimal"][1],
                        details["unit"],
                        metric_status,
                        status_color,
                        status_bg,
                    ),
                    unsafe_allow_html=True,
                )
            if audience == "athlete" and status == "Optimal" and len(items) > max_items:
                st.caption(f"+ {len(items) - max_items} more markers currently in range")

    st.markdown("### IA Action Board")
    st.caption("This is the operating layer: what matters, who owns it, and what changes next.")

    action_plan = _build_action_plan(detail_rows, role)
    summary_cols = st.columns(4)
    summary_cols[0].markdown(
        _summary_card("Primary Focus", action_plan["primary_focus"], "The main performance lever from the current blood picture.", "#dc2626"),
        unsafe_allow_html=True,
    )
    summary_cols[1].markdown(
        _summary_card("Secondary Focus", action_plan["secondary_focus"], "The next support layer to clean up this week.", "#d97706"),
        unsafe_allow_html=True,
    )
    summary_cols[2].markdown(
        _summary_card("Owner Today", action_plan["owner_today"], "Who should drive the first conversation and first change.", "#0f766e"),
        unsafe_allow_html=True,
    )
    summary_cols[3].markdown(
        _summary_card("Review Cadence", "48h + weekly", action_plan["review_cadence"], "#1d4ed8"),
        unsafe_allow_html=True,
    )

    action_cols = st.columns(3)
    for column, (lane, config) in zip(action_cols, action_plan["lanes"].items()):
        with column:
            st.markdown(
                f"<div style='margin-bottom:12px;'><div style='font-size:11px;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;color:{config['color']};margin-bottom:4px;'>{lane}</div><div style='font-size:13px;color:#475569;'>{config['detail']}</div></div>",
                unsafe_allow_html=True,
            )
            for item in config["items"]:
                st.markdown(
                    _action_card(
                        item["title"],
                        lane,
                        item["owner"],
                        item["horizon"],
                        item["body"],
                        config["color"],
                    ),
                    unsafe_allow_html=True,
                )

    st.markdown("### Staff Notes")
    note_cols = st.columns(3)
    note_cols[0].markdown(
        _detail_note_html(
            "Coach Lens",
            "Translate the blood picture into training design. Usually that means changing density, repeatability, and decision load before changing everything else.",
        ),
        unsafe_allow_html=True,
    )
    note_cols[1].markdown(
        _detail_note_html(
            "Medical Lens",
            "Use blood markers as context, not diagnosis. Anchor next steps to symptoms, collection quality, current phase, and longitudinal trend.",
        ),
        unsafe_allow_html=True,
    )
    note_cols[2].markdown(
        _detail_note_html(
            "Athlete Lens",
            "The athlete version should stay simple: sleep better, fuel better, recover better, and understand why those basics matter now.",
        ),
        unsafe_allow_html=True,
    )

    if biomarkers_registry:
        with st.expander("Research and interpretation notes"):
            for marker in biomarkers_registry():
                st.markdown(f"**{marker['label']}**")
                st.caption(marker["monitoring_notes"])

    template_data = TEMPLATE_PATH.read_text()
    st.download_button("Download anonymized biomarker CSV template", template_data, "innerathlete_biomarker_template.csv")
