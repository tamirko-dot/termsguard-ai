import streamlit as st

BORDER_COLORS = {"red": "#e53e3e", "yellow": "#d69e2e", "green": "#38a169"}
BADGE_COLORS = {"red": "#fff5f5", "yellow": "#fffff0", "green": "#f0fff4"}
ICONS = {"red": "🔴", "yellow": "🟡", "green": "🟢"}


def render_finding_card(finding: dict, index: int) -> None:
    risk = finding.get("risk", "green")
    border = BORDER_COLORS.get(risk, "#cbd5e0")
    bg = BADGE_COLORS.get(risk, "#f7fafc")
    icon = ICONS.get(risk, "⚪")

    with st.container():
        st.markdown(
            f"""
            <div style="
                border-left: 4px solid {border};
                background: {bg};
                padding: 12px 16px;
                border-radius: 6px;
                margin-bottom: 12px;
            ">
                <div style="font-weight:700; font-size:1rem;">
                    {icon} {finding.get("title", "Finding")}
                </div>
                <div style="margin-top:6px; color:#4a5568;">
                    {finding.get("explanation", "")}
                </div>
                <details style="margin-top:8px;">
                    <summary style="cursor:pointer; color:#718096; font-size:0.85rem;">
                        View source quote
                    </summary>
                    <blockquote style="
                        margin:8px 0 0 0;
                        padding:8px;
                        background:#edf2f7;
                        border-radius:4px;
                        font-size:0.85rem;
                        color:#2d3748;
                        font-style:italic;
                    ">
                        "{finding.get("source_quote", "")}"
                    </blockquote>
                </details>
            </div>
            """,
            unsafe_allow_html=True,
        )
