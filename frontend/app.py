import streamlit as st
from config import APP_TITLE, APP_LAYOUT

from pages.analyze_call import render as analyze_call
from pages.call_history import render as call_history
from pages.analytics_dashboard import render as analytics_dashboard

st.set_page_config(page_title=APP_TITLE, layout=APP_LAYOUT)

# Hide Streamlit's default page navigation
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Initialize page state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Analyze Call"

# ==================== SIDEBAR ====================
with st.sidebar:
    # Header
    st.markdown("## 🎧 Customer Support Intelligence")
    st.caption("Post-call analysis and insights")
    st.divider()
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["Analyze Call", "Call History", "Analytics Dashboard"],
        label_visibility="collapsed"
    )
    
    # Update session state
    st.session_state.current_page = page
    
    st.divider()
    
    # Page info
    st.markdown("### About this page")
    if page == "Analyze Call":
        st.caption("Analyze a recorded support call to extract structured insights.")
    elif page == "Call History":
        st.caption("Review and filter previously analyzed calls.")
    else:
        st.caption("View trends and risk indicators across calls.")
    
    st.divider()
    
    # Next steps
    st.markdown("### Next steps")
    if page == "Analyze Call":
        st.markdown("- Upload a call")
    elif page == "Call History":
        st.markdown("- Review unresolved calls")
    else:
        st.markdown("- Identify recurring issues")

# ==================== MAIN CONTENT ====================
if st.session_state.current_page == "Analyze Call":
    analyze_call()
elif st.session_state.current_page == "Call History":
    call_history()
elif st.session_state.current_page == "Analytics Dashboard":
    analytics_dashboard()