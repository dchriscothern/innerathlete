import streamlit as st

try:
    from innerathlete_content import genetics_registry, recommendations_registry
except ImportError:
    genetics_registry = None
    recommendations_registry = None

try:
    from .mvp_content import ATHLETE_OVERVIEW
    from .privacy import render_privacy_guardrail
except ImportError:
    from mvp_content import ATHLETE_OVERVIEW
    from privacy import render_privacy_guardrail


def _card(title: str, body: str, eyebrow: str | None = None, tone: str = "#1d4ed8") -> str:
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


def _summary_card(title: str, value: str, detail: str, accent: str) -> str:
    return (
        "<div style='background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;padding:16px 18px;height:100%;'>"
        f"<div style='font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:{accent};margin-bottom:6px;'>{title}</div>"
        f"<div style='font-size:22px;font-weight:800;color:#0f172a;margin-bottom:6px;'>{value}</div>"
        f"<div style='font-size:13px;color:#475569;line-height:1.55;'>{detail}</div>"
        "</div>"
    )


def _action_card(title: str, owner: str, horizon: str, body: str, color: str) -> str:
    return (
        "<div style='background:#ffffff;border:1px solid #e2e8f0;border-top:4px solid "
        f"{color};border-radius:14px;padding:16px 18px;height:100%;margin-bottom:12px;'>"
        f"<div style='font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:{color};margin-bottom:6px;'>{owner} | {horizon}</div>"
        f"<div style='font-size:16px;font-weight:800;color:#0f172a;margin-bottom:8px;'>{title}</div>"
        f"<div style='font-size:13px;color:#475569;line-height:1.55;'>{body}</div>"
        "</div>"
    )


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


def _domain_copy(domain: dict, audience: str) -> str:
    if audience == "athlete":
        return domain["athlete_safe_copy"]
    if audience == "investor":
        return domain["practitioner_copy"]
    if audience == "coach":
        if "training" in domain["domain"].lower() or "sleep" in domain["domain"].lower():
            return domain["practitioner_copy"]
        return domain["athlete_safe_copy"]
    return domain["practitioner_copy"]


def _role_use_case(role: str | None) -> str:
    audience = _audience_from_role(role)
    return {
        "investor": "Product workflow demo",
        "coach": "Training and communication context",
        "medical": "Context for recovery and follow-up",
        "athlete": "Simple habit and expectation guidance",
        "practitioner": "Integrated performance support",
    }[audience]


def _role_action_plan(domains: list[dict], role: str | None):
    audience = _audience_from_role(role)
    recommendations = recommendations_registry() if recommendations_registry else []

    sleep_copy = recommendations[0]["coach_copy"] if recommendations else "Keep sleep and recovery support simple and repeatable."
    nutrition_copy = recommendations[1]["practitioner_copy"] if len(recommendations) > 1 else "Use genetics to sharpen fueling support, not replace behavior and labs."
    brain_copy = recommendations[2]["coach_copy"] if len(recommendations) > 2 else "Use DNA as context for cueing and drill progression, not as a label."

    action_map = {
        "coach": {
            "What to Coach": {"color": "#dc2626", "items": [
                {"title": "Match training emphasis to response profile", "owner": "Coach", "horizon": "This block", "body": "Use the DNA profile to support decisions around speed-strength emphasis, aerobic support, and mixed training tolerance."},
                {"title": "Keep recovery language practical", "owner": "Coach", "horizon": "Daily", "body": sleep_copy},
            ]},
            "What to Build": {"color": "#d97706", "items": [
                {"title": "Fuel for the profile", "owner": "Performance + Athlete", "horizon": "This week", "body": nutrition_copy},
                {"title": "Adjust cueing and learning load", "owner": "Coach", "horizon": "This week", "body": brain_copy},
            ]},
        },
        "medical": {
            "What to Use": {"color": "#dc2626", "items": [
                {"title": "Use DNA as context, not conclusion", "owner": "Medical", "horizon": "Now", "body": "DNA should support recovery, sleep, and tissue discussions without being treated as a fixed risk label."},
                {"title": "Pair DNA with blood and history", "owner": "Medical", "horizon": "Ongoing", "body": "The genetics layer becomes more useful when it sits next to biomarkers, wellness, and previous response patterns."},
            ]},
            "What to Support": {"color": "#d97706", "items": [
                {"title": "Sleep and recovery routines", "owner": "Medical + Athlete", "horizon": "This week", "body": sleep_copy},
                {"title": "Practical nutrition follow-through", "owner": "Medical + Performance", "horizon": "This week", "body": nutrition_copy},
            ]},
        },
        "athlete": {
            "What It Means": {"color": "#dc2626", "items": [
                {"title": "This is your context, not your ceiling", "owner": "Athlete", "horizon": "Always", "body": "Your DNA profile helps explain tendencies. It does not define who you can become or what role you can play."},
                {"title": "Use it to guide habits", "owner": "Athlete", "horizon": "Daily", "body": "The profile is most useful when it helps you sleep better, fuel better, and recover more consistently."},
            ]},
            "What To Do": {"color": "#d97706", "items": [
                {"title": "Keep recovery simple and repeatable", "owner": "Athlete", "horizon": "This week", "body": sleep_copy},
                {"title": "Fuel for your workload", "owner": "Athlete", "horizon": "This week", "body": "Use the DNA report to support better choices, not to overcomplicate nutrition."},
            ]},
        },
        "investor": {
            "Product Value": {"color": "#dc2626", "items": [
                {"title": "Translate complexity into a usable profile", "owner": "Platform", "horizon": "Instant", "body": "The DNA layer converts technical genetics language into domain-level performance context that coaches and athletes can actually use."},
                {"title": "Keep the output responsible", "owner": "Platform", "horizon": "Always", "body": "The product avoids deterministic claims and presents genetics as one contextual layer inside a broader performance map."},
            ]},
            "Workflow": {"color": "#d97706", "items": [
                {"title": "Connect DNA to action", "owner": "Platform", "horizon": "Workflow", "body": "The strongest product outcome is not the profile alone. It is the ability to move from DNA insight to sleep, fueling, and coaching action."},
                {"title": "Support multiple audiences", "owner": "Platform", "horizon": "Workflow", "body": "The same DNA layer can be rendered differently for coaches, athletes, medical staff, and executives without changing the underlying model."},
            ]},
        },
        "practitioner": {
            "Use Now": {"color": "#dc2626", "items": [
                {"title": "Shape the plan, not the label", "owner": "Performance", "horizon": "Now", "body": "Use DNA to support training emphasis, sleep strategy, and fueling choices rather than fixed athlete labels."},
                {"title": "Integrate across pillars", "owner": "Performance", "horizon": "Ongoing", "body": "The DNA page is most valuable when it supports what blood, brain, and readiness data are already showing."},
            ]},
            "Build Next": {"color": "#d97706", "items": [
                {"title": "Tighten the recovery layer", "owner": "Staff", "horizon": "This week", "body": sleep_copy},
                {"title": "Refine fueling support", "owner": "Staff", "horizon": "This week", "body": nutrition_copy},
            ]},
        },
    }
    return action_map[audience]


def run_genomics_tab(role: str | None = None):
    audience = _audience_from_role(role)
    render_privacy_guardrail(" for genetics")
    st.subheader("DNA Performance Profile")
    st.caption("A cleaner domain-based DNA view built for real decision support, not raw SNP reporting.")

    top = st.columns(4)
    top[0].metric("Athlete", ATHLETE_OVERVIEW["label"])
    top[1].metric("Profile code", ATHLETE_OVERVIEW["athlete_code"])
    top[2].metric("Phase", ATHLETE_OVERVIEW["phase"])
    top[3].metric("Use case", _role_use_case(role))

    domains = genetics_registry() if genetics_registry else []
    if domains:
        summary_cols = st.columns(4)
        summary_cols[0].markdown(
            _summary_card("Training", "Response Profile", "Use DNA to frame how training emphasis may land, not to prescribe a fixed athlete type.", "#1d4ed8"),
            unsafe_allow_html=True,
        )
        summary_cols[1].markdown(
            _summary_card("Recovery", "Support Layer", "Recovery and resilience signals are most useful when they sharpen recovery habits and follow-up timing.", "#0f766e"),
            unsafe_allow_html=True,
        )
        summary_cols[2].markdown(
            _summary_card("Fueling", "Personalized Context", "Nutrition and micronutrient themes become stronger when combined with labs, behavior, and goals.", "#d97706"),
            unsafe_allow_html=True,
        )
        summary_cols[3].markdown(
            _summary_card("Interpretation", "Context Only", "DNA should guide conversations and planning, not ceiling, role, or talent labels.", "#7c3aed"),
            unsafe_allow_html=True,
        )

        st.markdown("### DNA Key Takeaways")
        takeaway_cols = st.columns(3)
        for column, domain in zip(takeaway_cols, domains[:3]):
            column.markdown(
                _card(
                    domain["domain"],
                    _domain_copy(domain, audience),
                    eyebrow=f"Confidence: {domain['evidence_confidence'].title()}",
                ),
                unsafe_allow_html=True,
            )

        st.markdown("### Full Domain Breakdown")
        breakdown_cols = st.columns(2)
        for idx, domain in enumerate(domains):
            with breakdown_cols[idx % 2]:
                st.markdown(
                    _card(
                        domain["domain"],
                        _domain_copy(domain, audience),
                        eyebrow=f"Confidence: {domain['evidence_confidence'].title()}",
                    ),
                    unsafe_allow_html=True,
                )

    st.markdown("### DNA Priorities")
    st.caption("What this profile should change in planning and communication.")
    action_map = _role_action_plan(domains, role)
    action_cols = st.columns(2)
    for column, (lane, config) in zip(action_cols, action_map.items()):
        with column:
            st.markdown(
                f"<div style='font-size:11px;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;color:{config['color']};margin-bottom:10px;'>{lane}</div>",
                unsafe_allow_html=True,
            )
            for item in config["items"]:
                st.markdown(
                    _action_card(
                        item["title"],
                        item["owner"],
                        item["horizon"],
                        item["body"],
                        config["color"],
                    ),
                    unsafe_allow_html=True,
                )

    with st.expander("Research and interpretation notes"):
        for domain in domains:
            st.markdown(f"**{domain['domain']}**")
            st.caption(domain["caution_copy"])
        st.caption(
            "Genetics should be treated as contextual support for training, recovery, sleep, and nutrition planning. "
            "It should not be used for talent identification, exclusion, or deterministic prediction."
        )
