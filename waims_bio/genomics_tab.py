import streamlit as st

try:
    from .mvp_content import ACTION_PLAN, ATHLETE_OVERVIEW, GENOMIC_SUMMARY
    from .privacy import render_privacy_guardrail
except ImportError:
    from mvp_content import ACTION_PLAN, ATHLETE_OVERVIEW, GENOMIC_SUMMARY
    from privacy import render_privacy_guardrail


def run_genomics_tab():
    render_privacy_guardrail(" for genetics")
    st.subheader("Performance Optimization Summary")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Athlete", ATHLETE_OVERVIEW["label"])
    col2.metric("Height / Weight", f"{ATHLETE_OVERVIEW['height']} / {ATHLETE_OVERVIEW['weight']}")
    col3.metric("Age", ATHLETE_OVERVIEW["age"])
    col4.metric("Phase", ATHLETE_OVERVIEW["phase"])

    st.caption("This tab mirrors the final InnerAthlete one-pager and two-pager structure using anonymized example content.")

    st.markdown("### Top Personal Goals")
    st.write(" | ".join(f"{idx + 1}. {goal}" for idx, goal in enumerate(ATHLETE_OVERVIEW["goals"])))
    st.caption(ATHLETE_OVERVIEW["context"])

    st.markdown("### Genomics Summary")
    summary_cols = st.columns(len(GENOMIC_SUMMARY))
    for column, (title, bullets) in zip(summary_cols, GENOMIC_SUMMARY.items()):
        column.markdown(f"**{title}**")
        for bullet in bullets:
            column.write(f"- {bullet}")

    st.markdown("### Personalized Insights and Action Plan")
    plan_cols = st.columns(2)
    items = list(ACTION_PLAN.items())
    left_items = items[:3]
    right_items = items[3:]
    with plan_cols[0]:
        for title, bullets in left_items:
            st.markdown(f"**{title}**")
            for bullet in bullets:
                st.write(f"- {bullet}")
    with plan_cols[1]:
        for title, bullets in right_items:
            st.markdown(f"**{title}**")
            for bullet in bullets:
                st.write(f"- {bullet}")

    st.info(
        "InnerAthlete should present genetics as context for training, recovery, sleep, and nutrition conversations. "
        "It should not present genetics as deterministic or as a selection tool."
    )
