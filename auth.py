"""
InnerAthlete role-based access control.

This demo auth layer keeps investor access hidden while exposing only the
public demo roles on the login screen.
"""

from pathlib import Path

import streamlit as st


DEMO_USERS = {
    "ia_investor": {
        "password": "InnerDemo2026!",
        "role": "investor_demo",
        "display": "Investor Demo",
        "name": "Investor Product Walkthrough",
        "public_demo": False,
    },
    "coach_demo": {
        "password": "coach123",
        "role": "coach_preview",
        "display": "Coach Preview",
        "name": "Coach Product Preview",
        "public_demo": True,
    },
    "medical_demo": {
        "password": "med123",
        "role": "medical_preview",
        "display": "Medical Preview",
        "name": "Medical Product Preview",
        "public_demo": True,
    },
    "executive_demo": {
        "password": "gm123",
        "role": "executive_preview",
        "display": "Executive Preview",
        "name": "Executive Product Preview",
        "public_demo": True,
    },
    "athlete_demo_1": {
        "password": "athlete123",
        "role": "athlete",
        "display": "Athlete Preview 1",
        "name": "Athlete Portal Preview 1",
        "public_demo": False,
    },
    "athlete_demo_2": {
        "password": "athlete123",
        "role": "athlete",
        "display": "Athlete Preview 2",
        "name": "Athlete Portal Preview 2",
        "public_demo": False,
    },
    "coach": {
        "password": "coach123",
        "role": "head_coach",
        "display": "Head Coach",
        "name": "Coach Demo",
        "public_demo": False,
    },
    "acoach": {
        "password": "acoach123",
        "role": "asst_coach",
        "display": "Asst. Coach",
        "name": "Asst. Coach Demo",
        "public_demo": False,
    },
    "scientist": {
        "password": "sci123",
        "role": "sport_scientist",
        "display": "Sport Scientist / Medical",
        "name": "Sport Scientist Demo",
        "public_demo": False,
    },
    "medical": {
        "password": "med123",
        "role": "medical",
        "display": "Medical / AT",
        "name": "Medical Staff Demo",
        "public_demo": False,
    },
    "gm": {
        "password": "gm123",
        "role": "gm",
        "display": "General Manager",
        "name": "GM Demo",
        "public_demo": False,
    },
    "ia_athlete": {
        "password": "AthletePreview2026!",
        "role": "athlete",
        "display": "Athlete Preview",
        "name": "Athlete Portal Preview",
        "public_demo": False,
    },
}


TAB_ACCESS = {
    "investor_demo": dict(ov=True, bio=True, gen=True, cog=True, how=True, why=True, plan=True),
    "coach_preview": dict(ov=True, cc=True, bio=True, gen=True, cog=True, how=True, plan=True, ath=True),
    "medical_preview": dict(ov=True, med=True, bio=True, gen=True, cog=True, how=True, plan=True, ath=True),
    "executive_preview": dict(ov=True, cc=True, bio=True, gen=True, cog=True, why=True, plan=True, ath=True),
    "head_coach": dict(ov=True, cc=True, bio=True, gen=True, cog=True, plan=True, ath=True),
    "asst_coach": dict(ov=True, cc=True, bio=True, gen=True, cog=True, plan=True, ath=True),
    "sport_scientist": dict(ov=True, cc=True, med=True, bio=True, gen=True, cog=True, plan=True, ath=True, ins=True),
    "medical": dict(ov=True, med=True, bio=True, gen=True, cog=True, plan=True, ath=True),
    "gm": dict(ov=True, cc=True, bio=True, gen=True, cog=True, plan=True),
    "athlete": dict(ov=True, bio=True, gen=True, cog=True, plan=True),
}


TAB_LABELS = {
    "ov": "Performance Map",
    "bio": "Blood",
    "gen": "DNA",
    "cog": "Cognitive",
    "how": "How It Works",
    "why": "Why It Matters",
    "plan": "Personalized Plan",
    "cc": "Coach Command Center",
    "med": "Medical Review",
    "ath": "Athlete Reports",
    "rd": "Today's Readiness",
    "ap": "Athlete Profiles",
    "tr": "Trends & Load",
    "jt": "Jump Testing",
    "inj": "Availability & Injuries",
    "fc": "Forecast",
    "ins": "Insights",
}


DATA_ACCESS = {
    "investor_demo": {
        "show_readiness_score": False,
        "show_raw_wellness": False,
        "show_force_plate_detail": False,
        "show_injury_detail": False,
        "show_gps": False,
    },
    "coach_preview": {
        "show_readiness_score": False,
        "show_raw_wellness": False,
        "show_force_plate_detail": False,
        "show_injury_detail": False,
        "show_gps": False,
    },
    "medical_preview": {
        "show_readiness_score": False,
        "show_raw_wellness": False,
        "show_force_plate_detail": False,
        "show_injury_detail": False,
        "show_gps": False,
    },
    "executive_preview": {
        "show_readiness_score": False,
        "show_raw_wellness": False,
        "show_force_plate_detail": False,
        "show_injury_detail": False,
        "show_gps": False,
    },
    "head_coach": {
        "show_readiness_score": True,
        "show_raw_wellness": False,
        "show_force_plate_detail": False,
        "show_injury_detail": False,
        "show_gps": True,
    },
    "asst_coach": {
        "show_readiness_score": True,
        "show_raw_wellness": False,
        "show_force_plate_detail": False,
        "show_injury_detail": False,
        "show_gps": True,
    },
    "sport_scientist": {
        "show_readiness_score": True,
        "show_raw_wellness": True,
        "show_force_plate_detail": True,
        "show_injury_detail": True,
        "show_gps": True,
    },
    "medical": {
        "show_readiness_score": True,
        "show_raw_wellness": True,
        "show_force_plate_detail": True,
        "show_injury_detail": True,
        "show_gps": True,
    },
    "gm": {
        "show_readiness_score": False,
        "show_raw_wellness": False,
        "show_force_plate_detail": False,
        "show_injury_detail": False,
        "show_gps": False,
    },
    "athlete": {
        "show_readiness_score": True,
        "show_raw_wellness": False,
        "show_force_plate_detail": False,
        "show_injury_detail": False,
        "show_gps": False,
    },
}


def get_role_color(role: str) -> str:
    return {
        "investor_demo": "#0f766e",
        "coach_preview": "#1d4ed8",
        "medical_preview": "#7c3aed",
        "executive_preview": "#b45309",
        "head_coach": "#1e3a5f",
        "asst_coach": "#2563eb",
        "sport_scientist": "#059669",
        "medical": "#7c3aed",
        "gm": "#b45309",
        "athlete": "#0ea5e9",
    }.get(role, "#6b7280")


def _role_summary(role: str) -> str:
    if role == "investor_demo":
        return "Hidden investor product walkthrough"
    if role == "coach_preview":
        return "Public product preview - coach lens"
    if role == "medical_preview":
        return "Public product preview - medical lens"
    if role == "executive_preview":
        return "Public product preview - executive lens"
    if role in ("sport_scientist", "medical"):
        return "Full performance platform access"
    if role in ("head_coach", "asst_coach"):
        return "Coach view with restricted raw wellness"
    if role == "athlete":
        return "Athlete self-service preview"
    return "Executive summary access only"


def render_login_page():
    st.markdown(
        """
    <style>
    section[data-testid="stMain"] > div { padding-top: 2rem; }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            '<div style="text-align:center;margin-bottom:24px;">'
            '<div style="font-size:30px;font-weight:800;color:#0f172a;">InnerAthlete</div>'
            '<div style="font-size:14px;color:#64748b;margin-top:4px;">'
            'Blood | DNA | Cognitive<br>Privacy-first platform demo</div>'
            "</div>",
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="e.g. coach_demo")
                password = st.text_input("Password", type="password", placeholder="Password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                user = DEMO_USERS.get(username.strip().lower())
                if user and user["password"] == password.strip():
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username.strip().lower()
                    st.session_state["role"] = user["role"]
                    st.session_state["display_role"] = user["display"]
                    st.session_state["user_name"] = user["name"]
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(
                "<div style='font-size:12px;font-weight:700;color:#0f172a;margin-bottom:10px;'>Demo Credentials</div>",
                unsafe_allow_html=True,
            )
            public_creds = [
                (username, config["password"], config["display"], get_role_color(config["role"]))
                for username, config in DEMO_USERS.items()
                if config.get("public_demo", False)
            ]
            for username, password, role_str, color in public_creds:
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;'
                    f'padding:4px 0;border-bottom:1px solid #f1f5f9;font-size:12px;">'
                    f'<span style="color:#374151;">{username} / {password}</span>'
                    f'<span style="color:{color};font-weight:700;">{role_str}</span>'
                    "</div>",
                    unsafe_allow_html=True,
                )

    return False


def render_user_badge():
    role = st.session_state.get("role", "")
    name = st.session_state.get("display_role", "")
    color = get_role_color(role)

    st.sidebar.markdown(
        f"""
    <div style="background:{color}18; border-left:4px solid {color};
                padding:10px 14px; border-radius:8px; margin-bottom:12px;">
      <div style="font-size:11px; color:{color}; font-weight:700; text-transform:uppercase;
                  letter-spacing:0.5px;">Signed in as</div>
      <div style="font-size:15px; font-weight:800; color:#1f2937; margin-top:2px;">{name}</div>
      <div style="font-size:11px; color:#64748b; margin-top:2px;">{_role_summary(role)}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Sign Out", use_container_width=True):
        for key in ["authenticated", "username", "role", "display_role", "user_name"]:
            st.session_state.pop(key, None)
        st.rerun()

    st.sidebar.markdown("<div style='flex:1;'></div>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    logo = Path("assets/branding/innerathlete/innerathlete-icon-dark.svg")
    if logo.exists():
        st.sidebar.image(str(logo), width=48)
    st.sidebar.markdown(
        "<div style='font-size:10px;color:#94a3b8;'>InnerAthlete platform demo</div>",
        unsafe_allow_html=True,
    )


def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)


def current_role() -> str:
    return st.session_state.get("role", "")


def can_see(tab_key: str) -> bool:
    role = current_role()
    return TAB_ACCESS.get(role, {}).get(tab_key, False)


def data_access() -> dict:
    return DATA_ACCESS.get(current_role(), DATA_ACCESS["gm"])


def get_visible_tabs() -> list[tuple[str, str]]:
    role = current_role()
    access = TAB_ACCESS.get(role, {})
    return [(k, TAB_LABELS[k]) for k, visible in access.items() if visible]
