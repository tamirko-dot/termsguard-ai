import streamlit as st


def render_source_viewer(raw_text: str, findings: list[dict]) -> None:
    """Show the original document with finding positions highlighted."""
    st.markdown("### Original Document")

    if not findings:
        st.text_area("Full text", raw_text, height=300)
        return

    # Build list of (char_start, char_end, risk) sorted by position
    spans = sorted(
        [(f["char_start"], f["char_end"], f["risk"]) for f in findings if "char_start" in f],
        key=lambda x: x[0],
    )

    colors = {"red": "#fed7d7", "yellow": "#fefcbf", "green": "#c6f6d5"}
    html_parts: list[str] = []
    cursor = 0

    for start, end, risk in spans:
        if start > cursor:
            html_parts.append(raw_text[cursor:start].replace("<", "&lt;").replace(">", "&gt;"))
        color = colors.get(risk, "#e2e8f0")
        snippet = raw_text[start:end].replace("<", "&lt;").replace(">", "&gt;")
        html_parts.append(f'<mark style="background:{color};">{snippet}</mark>')
        cursor = end

    html_parts.append(raw_text[cursor:].replace("<", "&lt;").replace(">", "&gt;"))

    st.markdown(
        f'<div style="white-space:pre-wrap; font-size:0.85rem; '
        f'max-height:400px; overflow-y:auto; padding:12px; '
        f'background:#f7fafc; border-radius:6px;">{"".join(html_parts)}</div>',
        unsafe_allow_html=True,
    )
