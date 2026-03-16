"""
InnerAthlete role-specific team and athlete views.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from innerathlete_content import biomarkers_registry, genetics_registry
from innerathlete_views import render_personalized_plan


def _athlete_code_map(players_df: pd.DataFrame) -> dict:
    ordered = players_df.sort_values("player_id")["player_id"].tolist()
    return {player_id: f"ATH-{idx:03d}" for idx, player_id in enumerate(ordered, start=1)}


def _safe_float(value, default=0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def _readiness_score(row: pd.Series, fp_row: pd.Series | None = None) -> float:
    sleep = _safe_float(row.get("sleep_hours", 7.5), 7.5)
    soreness = _safe_float(row.get("soreness", 4), 4)
    stress = _safe_float(row.get("stress", 4), 4)
    mood = _safe_float(row.get("mood", 7), 7)
    cmj = _safe_float(fp_row.get("cmj_height_cm"), 30) if fp_row is not None else 30
    rsi = _safe_float(fp_row.get("rsi_modified"), 0.35) if fp_row is not None else 0.35
    score = (
        (sleep / 8) * 30
        + ((10 - soreness) / 10) * 25
        + ((10 - stress) / 10) * 20
        + (mood / 10) * 15
        + min(10, (cmj / 35) * 6)
        + min(10, (rsi / 0.45) * 4)
    )
    return round(max(0, min(100, score)), 1)


def _priority_band(score: float) -> tuple[str, str, str]:
    if score >= 80:
        return "READY", "#16a34a", "#dcfce7"
    if score >= 65:
        return "MONITOR", "#d97706", "#fef3c7"
    return "PROTECT", "#dc2626", "#fee2e2"


def _summary(
    wellness_df: pd.DataFrame,
    players_df: pd.DataFrame,
    force_plate_df: pd.DataFrame,
    training_load_df: pd.DataFrame | None,
    end_date,
) -> pd.DataFrame:
    ref = pd.to_datetime(end_date)
    yesterday = ref - pd.Timedelta(days=1)
    code_map = _athlete_code_map(players_df)
    today = wellness_df[wellness_df["date"] == ref].copy()
    if today.empty:
        return pd.DataFrame()

    latest_fp = force_plate_df[force_plate_df["date"] == ref].copy() if len(force_plate_df) > 0 else pd.DataFrame()
    yesterday_fp = force_plate_df[force_plate_df["date"] == yesterday].copy() if len(force_plate_df) > 0 else pd.DataFrame()
    rows = []
    for _, row in today.iterrows():
        pid = row["player_id"]
        pos_row = players_df[players_df["player_id"] == pid]
        position = pos_row.iloc[0]["position"] if len(pos_row) > 0 else "F"

        fp_row = None
        if not latest_fp.empty:
            sub = latest_fp[latest_fp["player_id"] == pid]
            fp_row = sub.iloc[0] if len(sub) > 0 else None

        readiness = _readiness_score(row, fp_row)
        band, color, bg = _priority_band(readiness)

        y_sub = wellness_df[(wellness_df["player_id"] == pid) & (wellness_df["date"] == yesterday)]
        overnight_delta = None
        if len(y_sub) > 0:
            y_fp = None
            if not yesterday_fp.empty:
                yfp_sub = yesterday_fp[yesterday_fp["player_id"] == pid]
                y_fp = yfp_sub.iloc[0] if len(yfp_sub) > 0 else None
            overnight_delta = round(readiness - _readiness_score(y_sub.iloc[0], y_fp), 1)

        mins_4d = 0
        if training_load_df is not None and len(training_load_df) > 0 and "practice_minutes" in training_load_df.columns:
            tl = training_load_df[
                (training_load_df["player_id"] == pid)
                & (pd.to_datetime(training_load_df["date"]) > ref - pd.Timedelta(days=4))
                & (pd.to_datetime(training_load_df["date"]) <= ref)
            ].copy()
            if len(tl) > 0:
                tl["total_minutes"] = tl.get("practice_minutes", 0).fillna(0) + tl.get("game_minutes", 0).fillna(0)
                mins_4d = round(float(tl["total_minutes"].sum()), 0)

        rows.append(
            {
                "player_id": pid,
                "athlete_code": code_map.get(pid, "ATH-000"),
                "position": position,
                "readiness": readiness,
                "band": band,
                "band_color": color,
                "band_bg": bg,
                "sleep_hours": _safe_float(row.get("sleep_hours"), 7.5),
                "stress": _safe_float(row.get("stress"), 4),
                "soreness": _safe_float(row.get("soreness"), 4),
                "mood": _safe_float(row.get("mood"), 7),
                "cmj_height_cm": _safe_float(fp_row.get("cmj_height_cm"), 0) if fp_row is not None else 0,
                "rsi_modified": _safe_float(fp_row.get("rsi_modified"), 0) if fp_row is not None else 0,
                "overnight_delta": overnight_delta,
                "mins_4d": mins_4d,
            }
        )
    return pd.DataFrame(rows).sort_values(["readiness", "athlete_code"], ascending=[True, True])


def _panel(title: str, lines: list[str], color: str = "#0f172a") -> None:
    body = "".join(f"<div style='font-size:13px;color:#475569;margin-top:6px;'>{line}</div>" for line in lines)
    st.markdown(
        f"<div style='background:#ffffff;border:1px solid #e2e8f0;border-top:4px solid {color};"
        f"padding:16px;border-radius:14px;height:100%;'>"
        f"<div style='font-size:16px;font-weight:800;color:#0f172a;'>{title}</div>{body}</div>",
        unsafe_allow_html=True,
    )


def _coach_bullet(text: str, color: str) -> str:
    icon = "!" if color == "#dc2626" else ("•" if color == "#d97706" else "+")
    return (
        f"<div style='display:flex;gap:12px;align-items:flex-start;padding:9px 0;border-bottom:1px solid #e2e8f0;'>"
        f"<span style='min-width:18px;color:{color};font-weight:800;font-size:15px;'>{icon}</span>"
        f"<span style='font-size:13px;color:#1e293b;line-height:1.5;'>{text}</span>"
        "</div>"
    )


def _roster_card(row: pd.Series) -> str:
    risk_note = ""
    if row["mins_4d"] >= 120:
        risk_note = "<span style='background:#fef3c7;color:#92400e;font-size:10px;font-weight:700;padding:2px 7px;border-radius:4px;'>HEAVY 4D LOAD</span>"

    overnight = ""
    if row["overnight_delta"] is not None and abs(row["overnight_delta"]) >= 2:
        arrow = "▲" if row["overnight_delta"] > 0 else "▼"
        ov_color = "#16a34a" if row["overnight_delta"] > 0 else "#dc2626"
        overnight = f"<span style='font-size:11px;color:{ov_color};font-weight:700;margin-left:6px;'>{arrow}{abs(row['overnight_delta']):.0f}% overnight</span>"

    reasons = []
    if row["sleep_hours"] < 7:
        reasons.append(f"Sleep {row['sleep_hours']:.1f}h")
    if row["soreness"] >= 7:
        reasons.append(f"Soreness {row['soreness']:.0f}/10")
    if row["stress"] >= 7:
        reasons.append(f"Stress {row['stress']:.0f}/10")
    if row["mins_4d"] >= 120:
        reasons.append(f"{int(row['mins_4d'])} min in last 4d")
    if row["cmj_height_cm"] > 0 and row["readiness"] < 70:
        reasons.append("Neuromuscular output worth watching")

    reason_text = " · ".join(reasons[:2]) if reasons else "Cleared for normal plan"
    return (
        f"<div style='background:{row['band_bg']};border:2px solid {row['band_color']};border-radius:12px;padding:14px 16px;min-height:164px;'>"
        f"<div style='display:flex;justify-content:space-between;align-items:flex-start;'>"
        f"<div><div style='font-weight:800;font-size:14px;color:#0f172a;'>{row['athlete_code']}</div>"
        f"<div style='font-size:11px;color:#64748b;margin-top:1px;'>{row['position']}</div></div>"
        f"<span style='background:rgba(255,255,255,0.5);color:{row['band_color']};font-size:10px;font-weight:800;padding:3px 8px;border-radius:5px;letter-spacing:0.06em;'>{row['band']}</span>"
        f"</div>"
        f"<div style='display:flex;justify-content:space-between;align-items:center;margin-top:10px;'>"
        f"<div><span style='font-size:32px;font-weight:800;color:{row['band_color']};font-family:Georgia,serif;line-height:1;'>{row['readiness']:.0f}%</span>{overnight}</div>"
        f"<div>{risk_note}</div></div>"
        f"<div style='font-size:11px;color:#64748b;margin-top:8px;'>4d minutes: {int(row['mins_4d'])}</div>"
        f"<div style='font-size:12px;color:#334155;margin-top:8px;line-height:1.45;'>{reason_text}</div>"
        "</div>"
    )


def _readiness_z_context(
    player_id,
    wellness_df: pd.DataFrame,
    force_plate_df: pd.DataFrame,
    ref_date,
) -> tuple[str, str, str]:
    ref = pd.to_datetime(ref_date)
    history = wellness_df[
        (wellness_df["player_id"] == player_id) & (wellness_df["date"] < ref)
    ].sort_values("date").tail(30)
    if len(history) < 5:
        return "Limited baseline", "#64748b", "#f8fafc"

    scores = []
    for _, hist_row in history.iterrows():
        fp_match = force_plate_df[
            (force_plate_df["player_id"] == player_id)
            & (force_plate_df["date"] == hist_row["date"])
        ]
        fp_row = fp_match.iloc[0] if len(fp_match) > 0 else None
        scores.append(_readiness_score(hist_row, fp_row))

    baseline = pd.Series(scores, dtype=float)
    latest_wellness = wellness_df[
        (wellness_df["player_id"] == player_id) & (wellness_df["date"] == ref)
    ]
    if latest_wellness.empty:
        return "No same-day data", "#64748b", "#f8fafc"

    latest_fp_match = force_plate_df[
        (force_plate_df["player_id"] == player_id) & (force_plate_df["date"] == ref)
    ]
    latest_fp = latest_fp_match.iloc[0] if len(latest_fp_match) > 0 else None
    current = _readiness_score(latest_wellness.iloc[0], latest_fp)
    z = (current - baseline.mean()) / max(float(baseline.std()), 1.0)

    if z <= -1.0:
        return f"{abs(z):.1f} SD below baseline", "#dc2626", "#fee2e2"
    if z >= 1.0:
        return f"{z:.1f} SD above baseline", "#16a34a", "#dcfce7"
    return "Near baseline", "#d97706", "#fef3c7"


def _medical_watchlist_card(row: pd.Series, baseline_text: str, baseline_color: str, baseline_bg: str) -> str:
    return (
        f"<div style='background:{row['band_bg']};border:1px solid {row['band_color']}55;border-left:6px solid {row['band_color']};"
        "border-radius:14px;padding:14px 16px;margin-bottom:10px;'>"
        "<div style='display:flex;justify-content:space-between;align-items:flex-start;gap:10px;'>"
        f"<div><div style='font-size:14px;font-weight:800;color:#0f172a;'>{row['athlete_code']}</div>"
        f"<div style='font-size:11px;color:#64748b;margin-top:2px;'>Sleep {row['sleep_hours']:.1f}h | Stress {row['stress']:.0f}/10 | Soreness {row['soreness']:.0f}/10</div></div>"
        f"<div style='text-align:right;'><div style='font-size:22px;font-weight:800;color:{row['band_color']};'>{row['readiness']:.0f}%</div>"
        f"<div style='font-size:11px;font-weight:800;color:{row['band_color']};letter-spacing:0.08em;text-transform:uppercase;'>{row['band']}</div></div>"
        "</div>"
        "<div style='display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:10px;'>"
        f"<span style='background:{baseline_bg};color:{baseline_color};padding:4px 9px;border-radius:999px;font-size:11px;font-weight:800;'>{baseline_text}</span>"
        f"<span style='font-size:12px;color:#475569;'>CMJ {row['cmj_height_cm']:.1f} cm</span>"
        "</div></div>"
    )


def render_innerathlete_command_center(
    wellness_df: pd.DataFrame,
    players_df: pd.DataFrame,
    force_plate_df: pd.DataFrame,
    training_load_df: pd.DataFrame,
    end_date,
    role: str,
) -> None:
    st.header("Coach Command Center")
    st.caption("Daily staff brief with coach language, key watch items, and an anonymized roster view.")

    summary = _summary(wellness_df, players_df, force_plate_df, training_load_df, end_date)
    if summary.empty:
        st.info("No same-day data available for the coach command center.")
        return

    n_ready = int((summary["band"] == "READY").sum())
    n_monitor = int((summary["band"] == "MONITOR").sum())
    n_protect = int((summary["band"] == "PROTECT").sum())
    date_str = pd.to_datetime(end_date).strftime("%A, %B %d")

    header_html = (
        "<div style='background:linear-gradient(135deg,#0f172a 0%,#111827 55%,#0f766e 100%);border-radius:14px;"
        "padding:22px 28px 18px;margin-bottom:18px;border:1px solid rgba(255,255,255,0.07);'>"
        "<div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;'>"
        "<div>"
        f"<div style='font-size:11px;font-weight:600;letter-spacing:0.22em;text-transform:uppercase;color:#94a3b8;margin-bottom:4px;'>{date_str}</div>"
        "<div style='font-size:22px;font-weight:700;color:#f8fafc;letter-spacing:-0.01em;margin-bottom:6px;'>InnerAthlete Command Center</div>"
        "<div style='display:inline-block;font-size:12px;font-weight:600;color:#14b8a6;background:rgba(20,184,166,0.12);border-radius:6px;padding:3px 10px;letter-spacing:0.04em;'>Training Day</div>"
        "</div>"
        "<div style='display:flex;gap:24px;align-items:center;'>"
        f"<div style='text-align:center;'><div style='font-size:30px;font-weight:800;color:#4ade80;font-family:monospace;line-height:1;'>{n_ready}</div><div style='font-size:10px;color:#86efac;letter-spacing:0.1em;font-weight:700;margin-top:2px;'>READY</div></div>"
        f"<div style='text-align:center;'><div style='font-size:30px;font-weight:800;color:#fbbf24;font-family:monospace;line-height:1;'>{n_monitor}</div><div style='font-size:10px;color:#fde68a;letter-spacing:0.1em;font-weight:700;margin-top:2px;'>MONITOR</div></div>"
        f"<div style='text-align:center;'><div style='font-size:30px;font-weight:800;color:#f87171;font-family:monospace;line-height:1;'>{n_protect}</div><div style='font-size:10px;color:#fca5a5;letter-spacing:0.1em;font-weight:700;margin-top:2px;'>PROTECT</div></div>"
        "</div></div></div>"
    )
    st.markdown(header_html, unsafe_allow_html=True)

    protect_codes = summary[summary["band"] == "PROTECT"]["athlete_code"].tolist()
    heavy_codes = summary[summary["mins_4d"] >= 120]["athlete_code"].tolist()
    overnight = summary.dropna(subset=["overnight_delta"]).sort_values("overnight_delta")

    if protect_codes:
        b1 = f"<b>Check in before practice:</b> {', '.join(protect_codes[:3])} on protect today — modify exposure and confirm recovery plan."
        b1_color = "#dc2626"
    else:
        b1 = f"<b>Availability looks workable.</b> {n_ready} athletes are fully ready and no one is currently in a protect band."
        b1_color = "#16a34a"

    if len(overnight) > 0 and overnight.iloc[0]["overnight_delta"] <= -4:
        athlete = overnight.iloc[0]
        b2 = (
            f"<b>Biggest overnight drop:</b> {athlete['athlete_code']} fell {abs(athlete['overnight_delta']):.0f}% overnight — "
            f"sleep {athlete['sleep_hours']:.1f}h, soreness {athlete['soreness']:.0f}/10, stress {athlete['stress']:.0f}/10."
        )
        b2_color = "#d97706"
    else:
        b2 = "<b>Overnight trend is stable.</b> No major readiness drop showed up across the group from yesterday to today."
        b2_color = "#16a34a"

    if heavy_codes:
        b3 = f"<b>Heavy week load:</b> {', '.join(heavy_codes[:3])} have the highest 4-day minute totals — consider skill over conditioning today."
        b3_color = "#d97706"
    elif n_monitor >= 4:
        b3 = f"<b>{n_monitor} athletes are in monitor.</b> Keep decision load sharp but shorter, and avoid unnecessary fatigue."
        b3_color = "#d97706"
    else:
        b3 = "<b>Plan can stay normal.</b> Group load and recovery balance support a standard training day."
        b3_color = "#16a34a"

    brief_html = (
        "<div style='background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #f59e0b;border-radius:0 8px 8px 0;padding:14px 18px;margin-bottom:16px;'>"
        "<div style='font-size:10px;font-weight:700;letter-spacing:0.15em;color:#94a3b8;text-transform:uppercase;margin-bottom:8px;'>Morning Brief</div>"
        + _coach_bullet(b1, b1_color)
        + _coach_bullet(b2, b2_color)
        + _coach_bullet(b3, b3_color)
        + "</div>"
    )
    st.markdown(brief_html, unsafe_allow_html=True)

    pos_groups = {"G": [], "F": [], "C": []}
    for _, row in summary.iterrows():
        pos = str(row["position"]).upper()
        if pos.startswith("G"):
            pos_groups["G"].append(row["readiness"])
        elif pos.startswith("C"):
            pos_groups["C"].append(row["readiness"])
        else:
            pos_groups["F"].append(row["readiness"])

    def pos_badge(label: str, scores: list[float]) -> str:
        if not scores:
            return ""
        avg = sum(scores) / len(scores)
        status, color, bg = _priority_band(avg)
        return (
            f"<div style='background:{bg};border:1px solid {color}44;border-radius:8px;padding:10px 14px;text-align:center;flex:1;'>"
            f"<div style='font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:{color};margin-bottom:4px;'>{label}</div>"
            f"<div style='font-size:22px;font-weight:800;color:{color};line-height:1;'>{avg:.0f}%</div>"
            f"<div style='font-size:10px;color:{color};font-weight:600;margin-top:2px;'>{status} · {len(scores)} athletes</div>"
            "</div>"
        )

    badges = [
        pos_badge("Guards", pos_groups["G"]),
        pos_badge("Wings / Forwards", pos_groups["F"]),
        pos_badge("Centers / Bigs", pos_groups["C"]),
    ]
    if any(badges):
        st.markdown(
            "<div style='font-size:11px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#94a3b8;margin-bottom:8px;'>Unit Readiness</div>",
            unsafe_allow_html=True,
        )
        st.markdown(f"<div style='display:flex;gap:10px;margin-bottom:16px;'>{''.join(badges)}</div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='font-size:11px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#94a3b8;margin-bottom:10px;'>Roster Status</div>",
        unsafe_allow_html=True,
    )
    ordered = pd.concat(
        [
            summary[summary["band"] == "PROTECT"],
            summary[summary["band"] == "MONITOR"],
            summary[summary["band"] == "READY"],
        ]
    )
    cols = st.columns(3)
    for idx, (_, row) in enumerate(ordered.iterrows()):
        with cols[idx % 3]:
            st.markdown(_roster_card(row), unsafe_allow_html=True)

    if role == "gm":
        st.info("Executive access stays anonymized and summary-first.")


def render_medical_review(
    wellness_df: pd.DataFrame,
    players_df: pd.DataFrame,
    force_plate_df: pd.DataFrame,
    end_date,
) -> None:
    st.header("Medical Review")
    st.caption("A medical-facing workspace focused on recovery support, sample consistency, and cross-pillar interpretation.")

    summary = _summary(wellness_df, players_df, force_plate_df, None, end_date)
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("### Recovery Watchlist")
        if summary.empty:
            st.info("No daily data available.")
        else:
            st.caption("Daily watchlist uses readiness and recent baseline deviation. Blood panels should be reviewed separately from this daily screen.")
            top_watch = summary.head(10).copy()
            for _, row in top_watch.iterrows():
                baseline_text, baseline_color, baseline_bg = _readiness_z_context(
                    row["player_id"],
                    wellness_df,
                    force_plate_df,
                    end_date,
                )
                st.markdown(
                    _medical_watchlist_card(row, baseline_text, baseline_color, baseline_bg),
                    unsafe_allow_html=True,
                )

    with right:
        _panel(
            "Protocol Consistency",
            [
                "Keep blood collection timing and posture consistent across repeat draws.",
                "Avoid uncontrolled pre-collection exercise, food, or caffeine when protocol requires control.",
                "Use daily z-score or baseline-deviation logic for readiness and wellness, not as the only rule for a biomarker panel drawn every few months.",
                "Interpret blood markers with target ranges, prior draw context, collection consistency, wellness, and recent training load.",
            ],
            color="#7c3aed",
        )

    c1, c2 = st.columns(2)
    with c1:
        _panel("Biomarker Domains", [f"{item['label']} · {item['category']}" for item in biomarkers_registry()[:4]], color="#0f766e")
    with c2:
        _panel("Genetics Notes", [f"{item['domain']} · contextual support only" for item in genetics_registry()[:4]], color="#1d4ed8")


def render_athlete_reports(
    wellness_df: pd.DataFrame,
    players_df: pd.DataFrame,
    force_plate_df: pd.DataFrame,
    end_date,
) -> None:
    st.header("Athlete Report")
    st.caption("An anonymized athlete-facing summary built on the InnerAthlete report structure.")

    summary = _summary(wellness_df, players_df, force_plate_df, None, end_date)
    if summary.empty:
        st.info("No athlete report data available for the selected date.")
        return

    selected_code = st.selectbox("Select athlete", summary["athlete_code"].tolist())
    athlete = summary[summary["athlete_code"] == selected_code].iloc[0]

    hero = st.columns(4)
    hero[0].metric("Athlete", selected_code)
    hero[1].metric("Readiness", f"{athlete['readiness']:.1f}%")
    hero[2].metric("Current band", athlete["band"])
    hero[3].metric("Sleep", f"{athlete['sleep_hours']:.1f} h")

    cols = st.columns(3)
    with cols[0]:
        _panel("Blood", ["Use biomarkers to support recovery, fueling, and readiness habits.", "Repeat testing is most useful when collection conditions stay consistent."], color="#0f766e")
    with cols[1]:
        _panel("DNA", ["Use genetics as context for training response, sleep support, and nutrition choices.", "Avoid deterministic or limiting language."], color="#1d4ed8")
    with cols[2]:
        _panel("Cognitive", ["Match decision-load and learning demands to current readiness.", "Simplify new motor-learning demands when recovery support is needed."], color="#7c3aed")

    render_personalized_plan("athlete")
