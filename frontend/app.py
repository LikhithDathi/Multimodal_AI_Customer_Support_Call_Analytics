import streamlit as st
import requests
from datetime import datetime


def format_timestamp(ts: str):
    dt = datetime.fromisoformat(ts)
    now = datetime.now()

    if dt.date() == now.date():
        return f"Today, {dt.strftime('%I:%M %p')}"
    elif (now.date() - dt.date()).days == 1:
        return f"Yesterday, {dt.strftime('%I:%M %p')}"
    else:
        return dt.strftime("%b %d, %I:%M %p")


API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Customer Support Intelligence",
    layout="wide"
)

# -----------------------------
# Sidebar Navigation (BASELINE)
# -----------------------------
with st.sidebar:
    st.title("🎧 Customer Support Intelligence")

    page = st.radio(
        "Navigate",
        [
            "Analyze Call",
            "Call History",
            "Analytics Dashboard",
            "System Overview"
        ]
    )

# -----------------------------
# Analyze Call
# -----------------------------
if page == "Analyze Call":
    st.title("🎧 Analyze Customer Support Call")
    st.write("Upload a customer support call and extract insights.")

    uploaded_file = st.file_uploader(
        "Upload audio file",
        type=["wav", "mp3", "m4a", "flac", "ogg"]
    )

    if uploaded_file:
        st.audio(uploaded_file)

        if st.button("Analyze Call"):
            with st.spinner("Analyzing call..."):
                response = requests.post(
                    f"{API_BASE}/analyze-call",
                    files={"file": uploaded_file}
                )

            if response.status_code != 200:
                st.error("Failed to analyze call")
            else:
                data = response.json()

                st.subheader("Transcript")
                st.write(data["transcript"])

                st.subheader("Insights")
                st.json(data["insights"])

# -----------------------------
# Call History
# -----------------------------
elif page == "Call History":
    st.title("🗂 Call History")
    st.write("Previously analyzed calls")

    try:
        response = requests.get(f"{API_BASE}/calls")
        response.raise_for_status()
        calls = response.json()
    except requests.RequestException as e:
        st.error("Failed to load calls")
        st.caption(str(e))

    if not calls:
        st.info("No calls found")
    else:
        # ==================== SIMPLE FILTERING SECTION ====================
        with st.expander("🔍 Filter Calls", expanded=False):
            # Get unique values for dropdowns
            issue_categories = sorted(set([c.get('issue_category', 'Unknown') for c in calls]))
            sentiments = sorted(set([c.get('sentiment', 'Unknown') for c in calls]))
            urgency_levels = sorted(set([c.get('urgency', 'Unknown') for c in calls]))
            
            # Get date range
            try:
                dates = [datetime.fromisoformat(c.get('created_at', '')) for c in calls]
                min_date = min(dates).date()
                max_date = max(dates).date()
            except:
                min_date, max_date = None, None
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Status filter
                all_statuses = ["All", "Resolved", "Unresolved"]
                selected_status = st.selectbox(
                    "Status",
                    all_statuses,
                    index=0
                )
            
            with col2:
                # Issue category filter
                issue_options = ["All"] + issue_categories
                selected_issue = st.selectbox(
                    "Issue Category",
                    issue_options,
                    index=0
                )
            
            with col3:
                # Sentiment filter
                sentiment_options = ["All"] + sentiments
                selected_sentiment = st.selectbox(
                    "Sentiment",
                    sentiment_options,
                    index=0
                )
            
            # Second row of filters
            col4, col5 = st.columns(2)
            
            with col4:
                # Urgency filter
                urgency_options = ["All"] + urgency_levels
                selected_urgency = st.selectbox(
                    "Urgency",
                    urgency_options,
                    index=0
                )
            
            with col5:
                # Date range filter
                if min_date and max_date:
                    date_range = st.date_input(
                        "Date Range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                    
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                    else:
                        start_date, end_date = min_date, max_date
                else:
                    start_date, end_date = None, None
        
        # ==================== APPLY FILTERS ====================
        filtered_calls = calls.copy()
        
        # Apply status filter
        if selected_status != "All":
            if selected_status == "Resolved":
                filtered_calls = [c for c in filtered_calls if c.get('call_outcome') == "resolved"]
            else:  # Unresolved
                filtered_calls = [c for c in filtered_calls if c.get('call_outcome') != "resolved"]
        
        # Apply issue category filter
        if selected_issue != "All":
            filtered_calls = [c for c in filtered_calls if c.get('issue_category') == selected_issue]
        
        # Apply sentiment filter
        if selected_sentiment != "All":
            filtered_calls = [c for c in filtered_calls if c.get('sentiment') == selected_sentiment]
        
        # Apply urgency filter
        if selected_urgency != "All":
            filtered_calls = [c for c in filtered_calls if c.get('urgency') == selected_urgency]
        
        # Apply date range filter
        if start_date and end_date:
            filtered_calls = [
                c for c in filtered_calls
                if start_date <= datetime.fromisoformat(c.get('created_at', '')).date() <= end_date
            ]
        
        # Show filter summary
        if len(filtered_calls) != len(calls):
            st.success(f"📊 Showing {len(filtered_calls)} of {len(calls)} calls")
        
        # ==================== VIEW TOGGLE & SORTING ====================
        # View toggle
        view_mode = st.radio(
            "View Mode",
            ["📋 Card View", "📊 Table View"],
            horizontal=True,
            index=0
        )
        
        # Sort control
        sort_order = st.radio(
            "Sort calls by",
            ["Newest First", "Oldest First"],
            horizontal=True
        )
        
        sort_newest_first = sort_order == "Newest First"
        sorted_calls = sorted(
            filtered_calls,
            key=lambda c: c["created_at"],
            reverse=sort_newest_first
        )
        
        order_label = "newest to oldest" if sort_newest_first else "oldest to newest"
        st.caption(f"Showing {len(sorted_calls)} calls from {order_label}")
        
        if view_mode == "📋 Card View":
            # CARD VIEW
            for c in sorted_calls:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**📞 Call #{c['id']}**")
                    with col2:
                        status = "✅ Resolved" if c.get('call_outcome') == "resolved" else "❌ Unresolved"
                        st.markdown(f"**{status}**")
                    
                    # Issue, sentiment, urgency in columns
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.markdown(f"**Issue:** {c.get('issue_category', 'N/A').capitalize()}")
                    with col_b:
                        st.markdown(f"**Sentiment:** {c.get('sentiment', 'N/A').capitalize()}")
                    with col_c:
                        st.markdown(f"**Urgency:** {c.get('urgency', 'N/A').capitalize()}")
                    
                    # Timestamp
                    st.caption(f"🕒 {format_timestamp(c.get('created_at', ''))}")
                    
                    # Single expander for transcript
                    transcript = c.get('transcript', '')
                    if transcript:
                        # Show preview with "Show more" expander
                        preview_length = 200
                        show_preview = len(transcript) > preview_length
                        
                        if show_preview:
                            st.write("**Transcript Preview:**")
                            st.write(transcript[:preview_length] + "...")
                            
                            with st.expander("📄 View Full Transcript", expanded=False):
                                st.write(transcript)
                        else:
                            st.write("**Transcript:**")
                            st.write(transcript)
                    else:
                        st.caption("No transcript available")
                    
                    # Divider
                    st.divider()
        
        else:  # TABLE VIEW
            import pandas as pd
            
            # Prepare data for table
            table_data = []
            for c in sorted_calls:
                table_data.append({
                    "ID": c.get('id'),
                    "Status": "✅ Resolved" if c.get('call_outcome') == "resolved" else "❌ Unresolved",
                    "Issue": c.get('issue_category', 'N/A').capitalize(),
                    "Sentiment": c.get('sentiment', 'N/A').capitalize(),
                    "Urgency": c.get('urgency', 'N/A').capitalize(),
                    "Time": format_timestamp(c.get('created_at', '')),
                    "Transcript": len(c.get('transcript', ''))
                })
            
            df = pd.DataFrame(table_data)
            
            # Display the table
            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("Call ID", width="small"),
                    "Status": st.column_config.TextColumn("Status", width="medium"),
                    "Issue": st.column_config.TextColumn("Issue Category", width="medium"),
                    "Sentiment": st.column_config.TextColumn("Sentiment", width="small"),
                    "Urgency": st.column_config.TextColumn("Urgency", width="small"),
                    "Time": st.column_config.TextColumn("Time", width="small"),
                    "Transcript": st.column_config.NumberColumn("Transcript Length", width="small")
                }
            )
            
            # --- Quick Actions ---
            st.markdown("---")
            
            # Initialize show_details in session state
            if 'show_details' not in st.session_state:
                st.session_state.show_details = True
            
            # Call selection at the top (only show filtered calls)
            call_options = [f"Call #{c['id']}" for c in sorted_calls]
            if not call_options:
                st.warning("No calls match the selected filters")
                selected_call_option = None
                selected_call = None
            else:
                selected_call_option = st.selectbox(
                    "Select a call to view details:",
                    call_options,
                    index=0
                )
                
                # Get selected call
                selected_id = int(selected_call_option.replace("Call #", ""))
                selected_call = next((c for c in sorted_calls if c['id'] == selected_id), None)
            
            # Simple buttons row
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Export button
                if st.button("📥 Export CSV", use_container_width=True):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="call_history.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col2:
                # Refresh button
                if st.button("🔄 Refresh Data", use_container_width=True):
                    st.rerun()
            
            with col3:
                # Clear button - hides details
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.show_details = False
            
            # --- Details Pane ---
            st.markdown("---")
            
            # Only show details if show_details is True and we have a selected call
            if selected_call and st.session_state.show_details:
                st.subheader(f"Details for Call #{selected_id}")
                
                # Key metrics in columns
                col1, col2, col3 = st.columns(3)
                with col1:
                    status = "✅ Resolved" if selected_call.get('call_outcome') == "resolved" else "❌ Unresolved"
                    st.metric("Status", status)
                with col2:
                    st.metric("Issue", selected_call.get('issue_category', 'N/A').capitalize())
                with col3:
                    st.metric("Sentiment", selected_call.get('sentiment', 'N/A').capitalize())
                
                # Additional info (from your schema)
                col4, col5 = st.columns(2)
                with col4:
                    st.write(f"**Urgency:** {selected_call.get('urgency', 'N/A').capitalize()}")
                    st.write(f"**Agent Behavior:** {selected_call.get('agent_behavior', 'N/A').capitalize()}")
                with col5:
                    st.write(f"**Time:** {format_timestamp(selected_call.get('created_at', ''))}")
                    if selected_call.get('audio_path'):
                        st.write(f"**Audio File:** {selected_call.get('audio_path')}")
                
                # Transcript (OPEN BY DEFAULT)
                transcript = selected_call.get('transcript', '')
                if transcript:
                    with st.expander("📄 Transcript", expanded=True):
                        st.write(transcript)
                else:
                    st.info("No transcript available")
            elif not st.session_state.show_details and selected_call:
                st.info("👈 Select a call and details will appear here")
        
        # ==================== SIMPLE FILTER STATISTICS ====================
        if len(filtered_calls) != len(calls):
            st.markdown("---")
            
            # Show some quick stats about the filtered results
            resolved_count = sum(1 for c in filtered_calls if c.get('call_outcome') == "resolved")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Filtered Calls", len(filtered_calls))
            with col2:
                st.metric("Resolved", resolved_count, f"{resolved_count/len(filtered_calls)*100:.1f}%" if filtered_calls else "0%")
        
        # Total calls at bottom
        st.caption(f"Total calls in database: {len(calls)} • Filtered: {len(filtered_calls)}")

        
# -----------------------------
# Analytics Dashboard (MINIMAL)
# -----------------------------
elif page == "Analytics Dashboard":
    st.title("📈 Analytics Dashboard")

    response = requests.get(f"{API_BASE}/calls")

    if response.status_code != 200:
        st.error("Failed to load analytics")
    else:
        calls = response.json()

        st.metric("Total Calls", len(calls))

# -----------------------------
# System Overview
# -----------------------------
elif page == "System Overview":
    st.title("ℹ️ System Overview")
    st.write("Customer Support Call Analytics System")