import streamlit as st

from components.finding_card import render_finding_card
from components.source_viewer import render_source_viewer
from components.traffic_light import render_traffic_light
from services.api_client import analyze, health

st.set_page_config(
    page_title="TermsGuard AI",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ TermsGuard AI")
st.caption("Paste a Terms of Service or Privacy Policy and get a plain-English risk report.")

# Sidebar — backend status
with st.sidebar:
    st.header("Backend Status")
    try:
        info = health()
        st.success(f"Online — v{info.get('version', '?')}")
    except Exception:
        st.error("Backend offline — start the backend first")

    st.markdown("---")
    st.header("Settings")
    show_source = st.checkbox("Show source document with highlights", value=True)

# Input
tab_url, tab_text = st.tabs(["Paste URL (coming soon)", "Paste Text"])

with tab_url:
    st.info("URL fetching will be available in a future release. Use the Paste Text tab for now.")

with tab_text:
    raw_text = st.text_area(
        "Paste the full ToS / Privacy Policy text here",
        height=250,
        placeholder="Paste the document text...",
    )
    url_input = st.text_input("Source URL (optional)", placeholder="https://example.com/terms")

    analyze_btn = st.button("Analyze", type="primary", disabled=not raw_text.strip())

if analyze_btn and raw_text.strip():
    with st.spinner("Analyzing with TermsGuard AI — this may take up to 60 seconds..."):
        try:
            result = analyze(raw_text, url=url_input or None)
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
            st.stop()

    st.markdown("---")

    col1, col2 = st.columns([1, 3])
    with col1:
        render_traffic_light(result["traffic_light"])
        st.markdown(f"**{len(result['findings'])} finding(s)** · {result['processing_ms']} ms")

    with col2:
        st.markdown("#### Summary")
        st.write(result["summary"])

    st.markdown("---")
    st.markdown("### Findings")

    red = [f for f in result["findings"] if f["risk"] == "red"]
    yellow = [f for f in result["findings"] if f["risk"] == "yellow"]
    green = [f for f in result["findings"] if f["risk"] == "green"]

    for finding in red + yellow + green:
        render_finding_card(finding, index=result["findings"].index(finding))

    if show_source and raw_text:
        st.markdown("---")
        render_source_viewer(raw_text, result["findings"])
