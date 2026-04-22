import streamlit as st

COLORS = {"red": "#e53e3e", "yellow": "#d69e2e", "green": "#38a169"}
LABELS = {"red": "HIGH RISK", "yellow": "MEDIUM RISK", "green": "LOW RISK"}
ICONS = {"red": "🔴", "yellow": "🟡", "green": "🟢"}


def render_traffic_light(level: str) -> None:
    color = COLORS.get(level, "#718096")
    label = LABELS.get(level, level.upper())
    icon = ICONS.get(level, "⚪")
    st.markdown(
        f"""
        <div style="
            background:{color};
            color:white;
            padding:16px 24px;
            border-radius:12px;
            font-size:1.4rem;
            font-weight:700;
            text-align:center;
            letter-spacing:0.05em;
        ">
            {icon} {label}
        </div>
        """,
        unsafe_allow_html=True,
    )
