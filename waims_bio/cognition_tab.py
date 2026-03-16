import plotly.graph_objects as go
import streamlit as st

try:
    from .mvp_content import ATHLETE_OVERVIEW, S2_ACTIONS, S2_METRICS, score_band
    from .privacy import render_privacy_guardrail
except ImportError:
    from mvp_content import ATHLETE_OVERVIEW, S2_ACTIONS, S2_METRICS, score_band
    from privacy import render_privacy_guardrail


def _score_band_strip():
    bands = [
        ("0% - 20%", "Basic"),
        ("20% - 40%", "Lower Average"),
        ("40% - 60%", "Average"),
        ("60% - 80%", "Higher Average"),
        ("80% - 100%", "Elite"),
    ]
    html = ['<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:18px;">']
    for label, name in bands:
        _, color, bg = score_band(int(label.split("%")[0]))
        html.append(
            f'<div style="background:{bg};border:1px solid {color}55;border-radius:10px;padding:12px;text-align:center;">'
            f'<div style="font-size:12px;font-weight:700;color:#334155;">{label}</div>'
            f'<div style="font-size:11px;letter-spacing:0.04em;text-transform:uppercase;color:{color};">{name}</div>'
            f"</div>"
        )
    html.append("</div>")
    return "".join(html)


def _metric_chart():
    fig = go.Figure()
    for item in S2_METRICS:
        _, color, _ = score_band(item["value"])
        fig.add_trace(
            go.Bar(
                x=[item["metric"]],
                y=[item["value"]],
                marker_color=color,
                text=[f"{item['value']}%"],
                textposition="outside",
                hovertemplate="%{x}<br>%{y}%<extra></extra>",
            )
        )
    fig.update_layout(
        barmode="group",
        height=360,
        margin=dict(l=10, r=10, t=10, b=60),
        yaxis=dict(range=[0, 100], title="Score"),
        showlegend=False,
    )
    return fig


def run_cognition_tab(readiness_score, role=None):
    render_privacy_guardrail(" for cognition")
    st.subheader("S2 Cognitive Testing")

    meta1, meta2, meta3 = st.columns(3)
    meta1.metric("Athlete", ATHLETE_OVERVIEW["label"])
    meta2.metric("Phase", ATHLETE_OVERVIEW["phase"])
    meta3.metric("Composite readiness", f"{readiness_score:.1f}%")

    st.markdown(_score_band_strip(), unsafe_allow_html=True)

    st.plotly_chart(_metric_chart(), use_container_width=True)

    st.markdown("### Cognitive Profile")
    for item in S2_METRICS:
        band, color, bg = score_band(item["value"])
        st.markdown(
            f'<div style="background:{bg};border-left:4px solid {color};padding:12px 14px;margin-bottom:10px;border-radius:0 10px 10px 0;">'
            f'<div style="display:flex;justify-content:space-between;gap:12px;align-items:center;">'
            f'<div style="font-weight:700;color:#0f172a;">{item["metric"]}</div>'
            f'<div style="font-weight:700;color:{color};">{item["value"]}% · {band}</div>'
            f'</div>'
            f'<div style="font-size:13px;color:#475569;margin-top:6px;">{item["description"]}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    audience = "athlete" if role == "athlete" else ("investor" if role == "investor_demo" else ("medical" if role in ("medical", "medical_preview", "sport_scientist") else "coach"))

    st.markdown("### Cognitive Priorities")
    if audience == "athlete":
        actions = [
            "Use good sleep and recovery habits to help decision speed and attention stay sharp.",
            "Build read-react work gradually instead of trying to master too much complexity at once.",
            "Treat lower scores as trainable skills, not fixed limitations.",
        ]
    elif audience == "medical":
        actions = [
            "Interpret cognitive results alongside sleep, stress, recovery support, and recent load.",
            "Use downturns as a cue to check context before changing training recommendations.",
            "Support coaches with simple decision-load guidance rather than technical jargon.",
        ]
    elif audience == "investor":
        actions = [
            "The cognitive layer turns reaction, timing, and learning signals into usable coaching language.",
            "The value is not the raw score alone. It is the way the platform connects cognition to daily decisions.",
            "This pillar becomes stronger when it sits beside blood, DNA, and readiness context.",
        ]
    else:
        actions = list(S2_ACTIONS)

    for action in actions:
        st.write(f"- {action}")

    if readiness_score < 70:
        st.warning("Current readiness suggests decision speed may be more vulnerable today. Keep decision-load work short and sharp.")
    else:
        st.success("Current readiness supports normal decision-speed and perceptual training exposure.")
