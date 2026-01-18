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
    st.markdown("## 🎧Customer Support Intelligence")
    st.caption("Post-call analysis and insights")

    st.divider()

    st.markdown("### Analysis")
    page = st.radio(
        label="",
        options=["Analyze Call", "Call History", "Analytics Dashboard"],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### About this page")
    if page == "Analyze Call":
        st.caption(
            "Analyze a recorded customer support call to "
            "extract sentiment, urgency, and resolution indicators."
        )
        st.markdown("**To get started:**")
        st.markdown("- Upload a call recording")

    elif page == "Call History":
        st.caption(
            "View and filter previously analyzed support calls "
            "to identify patterns and unresolved issues."
        )

    elif page == "Analytics Dashboard":
        st.caption(
            "Explore trends and risk indicators across "
            "analyzed support calls."
        )

    st.divider()

    st.markdown("### Next steps")
    if page == "Analyze Call":
        st.markdown("- Upload a call")
    elif page == "Call History":
        st.markdown("- Review unresolved calls")
    elif page == "Analytics Dashboard":
        st.markdown("- Identify recurring issues")



# -----------------------------
# Analyze Call
# -----------------------------
if page == "Analyze Call":
    st.title("🎧 Analyze Customer Support Call")
    st.caption("Upload an audio file to extract transcript and insights")
    
    # Upload section with some styling
    with st.container():
        uploaded_file = st.file_uploader(
            "**Select audio file**",
            type=["wav", "mp3", "m4a", "flac", "ogg"],
            help="Supported formats: WAV, MP3, M4A, FLAC, OGG"
        )
    
    if uploaded_file:
        # Show file info
        col1, col2 = st.columns([2, 1])
        with col1:
            st.audio(uploaded_file)
        with col2:
            file_size = f"{uploaded_file.size / (1024 * 1024):.1f} MB"
            st.caption(f"File: {uploaded_file.name}")
            st.caption(f"Size: {file_size}")
        
        # Analyze button
        if st.button("🔍 Analyze Call", type="primary", use_container_width=True):
            with st.spinner("Analyzing call content..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/analyze-call",
                        files={"file": uploaded_file}
                    )
                    
                    if response.status_code != 200:
                        st.error("Failed to analyze call")
                    else:
                        data = response.json()
                        
                        st.success("✅ Analysis complete")
                        
                        # Results section
                        st.divider()
                        st.subheader("Analysis Results")
                        
                        # Create two main columns
                        main_col1, main_col2 = st.columns(2)
                        
                        with main_col1:
                            # Transcript panel
                            st.markdown("#### 📄 Transcript")
                            transcript = data.get("transcript", "")
                            if transcript:
                                with st.expander("View full transcript", expanded=True):
                                    st.write(transcript)
                                    # Add a simple stat
                                    word_count = len(transcript.split())
                                    st.caption(f"Word count: {word_count}")
                            else:
                                st.info("No transcript available")
                        
                        with main_col2:
                            # Insights panel
                            st.markdown("#### 📊 Insights")
                            insights = data.get("insights", {})
                            
                            if insights:
                                # Display key insights in a clean list
                                for key in ["sentiment", "issue_category", "urgency", "call_outcome"]:
                                    if key in insights:
                                        value = insights[key]
                                        # Add some visual indicators
                                        if key == "sentiment":
                                            icon = "😊" if value == "positive" else "😐" if value == "neutral" else "😠"
                                            st.write(f"{icon} **Sentiment:** {value.title()}")
                                        elif key == "urgency":
                                            icon = "🔴" if value == "high" else "🟡" if value == "medium" else "🟢"
                                            st.write(f"{icon} **Urgency:** {value.title()}")
                                        elif key == "call_outcome":
                                            icon = "✅" if value == "resolved" else "❌"
                                            st.write(f"{icon} **Outcome:** {value.title()}")
                                        else:
                                            st.write(f"**{key.replace('_', ' ').title()}:** {value.title()}")
                                
                                # Show any additional insights
                                other_keys = [k for k in insights.keys() if k not in ["sentiment", "issue_category", "urgency", "call_outcome"]]
                                if other_keys:
                                    with st.expander("Additional details"):
                                        for key in other_keys:
                                            st.write(f"**{key.replace('_', ' ').title()}:** {insights[key]}")
                            else:
                                st.info("No insights generated")
                        
                        # Simple export options at the bottom
                        st.divider()
                        col_export1, col_export2 = st.columns(2)
                        
                        with col_export1:
                            if transcript:
                                st.download_button(
                                    "📥 Download Transcript",
                                    data=transcript,
                                    file_name=f"transcript_{uploaded_file.name.split('.')[0]}.txt",
                                    use_container_width=True
                                )
                        
                        with col_export2:
                            if insights:
                                import json
                                st.download_button(
                                    "📊 Download Insights",
                                    data=json.dumps(insights, indent=2),
                                    file_name=f"insights_{uploaded_file.name.split('.')[0]}.json",
                                    mime="application/json",
                                    use_container_width=True
                                )
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Could not connect to the analysis service")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    else:
        # Simple empty state
        st.info("👆 **Upload an audio file to begin analysis**")
        
        # Quick info in columns
        col_info1, col_info2, col_info3 = st.columns(3)

        with col_info1:
            st.markdown("""
            **Best results when:**
            - Audio is clear and audible  
            - Minimal background noise  
            - Speakers do not talk over each other  
            - Conversation is primarily in English  
            """)

        
        with col_info2:
            st.markdown("""
            **What you'll get:**
            - Full call transcript
            - Sentiment analysis
            - Issue categorization
            - Urgency assessment
            """)
        
        with col_info3:
            st.markdown("""
            **Supported formats:**
            - WAV
            - MP3  
            - M4A
            - FLAC
            - OGG
            """)

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
        
        # ==================== COMPACT VIEW & SORT CONTROLS ====================
        # Put View Mode and Sort controls side-by-side in one row
        col_view, col_sort = st.columns(2)
        
        with col_view:
            # View toggle
            view_mode = st.radio(
                "**View Mode**",
                ["📋 Card View", "📊 Table View"],
                horizontal=True,
                index=0
            )
        
        with col_sort:
            # Sort control
            sort_order = st.radio(
                "**Sort by**",
                ["Newest First", "Oldest First"],
                horizontal=True,
                index=0
            )
        
        sort_newest_first = sort_order == "Newest First"
        sorted_calls = sorted(
            filtered_calls,
            key=lambda c: c["created_at"],
            reverse=sort_newest_first
        )
        
        order_label = "newest to oldest" if sort_newest_first else "oldest to newest"
        st.markdown("---")

        st.caption(f"Showing {len(sorted_calls)} calls from {order_label}")
        
        
        # Rest of your code remains the same...
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
    st.caption("Performance metrics and actionable insights")

    try:
        response = requests.get(f"{API_BASE}/calls")
        response.raise_for_status()
        calls = response.json()
    except requests.RequestException:
        st.error("Failed to load analytics data")
        st.stop()

    if not calls:
        st.info("No data available for analytics")
        st.stop()

    total_calls = len(calls)
    
    # Key metrics
    resolved_calls = [c for c in calls if c.get("call_outcome") == "resolved"]
    unresolved_calls = [c for c in calls if c.get("call_outcome") != "resolved"]
    high_urgency = [c for c in calls if c.get("urgency") == "high"]
    negative_sentiment = [c for c in calls if c.get("sentiment") == "negative"]
    
    # High-risk calls (unresolved + high urgency)
    high_risk_calls = [
        c for c in calls 
        if c.get("call_outcome") != "resolved" and c.get("urgency") == "high"
    ]

    # ==================== KEY METRICS ====================
    st.subheader("📊 Performance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Calls",
            total_calls,
            help="Total calls in the system"
        )
    
    with col2:
        resolution_rate = (len(resolved_calls) / total_calls * 100) if total_calls else 0
        st.metric(
            "Resolution Rate",
            f"{resolution_rate:.1f}%",
            delta=f"{len(resolved_calls)} resolved",
            delta_color="normal",
            help="Percentage of resolved calls"
        )
    
    with col3:
        st.metric(
            "High Urgency",
            len(high_urgency),
            delta=f"{(len(high_urgency) / total_calls * 100):.1f}%",
            delta_color="inverse" if len(high_urgency) > 0 else "off",
            help="Calls marked as high urgency"
        )
    
    with col4:
        negative_rate = (len(negative_sentiment) / total_calls * 100) if total_calls else 0
        st.metric(
            "Negative Sentiment",
            f"{negative_rate:.1f}%",
            delta=f"{len(negative_sentiment)} calls",
            delta_color="inverse" if negative_rate > 20 else "off",
            help="Calls with negative sentiment"
        )
    
    # ==================== DISTRIBUTIONS ====================
    st.markdown("---")
    st.subheader("📈 Distributions")
    
    # Prepare data for distributions
    issue_counts = {}
    sentiment_counts = {}
    urgency_counts = {}
    
    for c in calls:
        issue = c.get("issue_category", "other").capitalize()
        sentiment = c.get("sentiment", "neutral").capitalize()
        urgency = c.get("urgency", "low").capitalize()
        
        issue_counts[issue] = issue_counts.get(issue, 0) + 1
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
    
    # Display distributions in tabs
    tab1, tab2, tab3 = st.tabs(["Issue Categories", "Sentiment", "Urgency"])
    
    with tab1:
        if issue_counts:
            st.bar_chart(issue_counts)
            top_issue = max(issue_counts, key=issue_counts.get)
            st.caption(f"Most common issue: **{top_issue}** ({issue_counts[top_issue]} calls)")
        else:
            st.info("No issue category data available")
    
    with tab2:
        if sentiment_counts:
            st.bar_chart(sentiment_counts)
            dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)
            st.caption(f"Dominant sentiment: **{dominant_sentiment}**")
        else:
            st.info("No sentiment data available")
    
    with tab3:
        if urgency_counts:
            st.bar_chart(urgency_counts)
            high_count = urgency_counts.get('High', 0)
            if high_count > 0:
                st.caption(f"**{high_count}** high urgency calls requiring attention")
        else:
            st.info("No urgency data available")
    
    # ==================== RISK ASSESSMENT ====================
    st.markdown("---")
    st.subheader("⚠️ Risk Assessment")
    
    if high_risk_calls:
        with st.container():
            st.error(f"**{len(high_risk_calls)} High-Risk Calls**")
            st.write("Unresolved calls marked as high urgency require immediate attention.")
            
            # Show high-risk calls in a compact table
            if high_risk_calls:
                high_risk_data = []
                for c in high_risk_calls[:5]:  # Show top 5
                    high_risk_data.append({
                        "Call ID": c.get('id'),
                        "Issue": c.get('issue_category', 'N/A').capitalize(),
                        "Sentiment": c.get('sentiment', 'N/A').capitalize(),
                        "Created": format_timestamp(c.get('created_at', ''))
                    })
                
                if high_risk_data:
                    import pandas as pd
                    df_high_risk = pd.DataFrame(high_risk_data)
                    st.dataframe(df_high_risk, use_container_width=True, hide_index=True)
                    
                    if len(high_risk_calls) > 5:
                        st.caption(f"... and {len(high_risk_calls) - 5} more high-risk calls")
    else:
        st.success("✅ No high-risk calls detected")
        st.caption("All high urgency calls have been resolved")
    
    # ==================== TOP INSIGHTS ====================
    st.markdown("---")
    st.subheader("💡 Top Insights")
    
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        with st.container():
            st.markdown("#### 📊 Resolution Performance")
            
            if len(resolved_calls) > len(unresolved_calls):
                st.success("**Good** - More calls resolved than unresolved")
            else:
                st.warning("**Needs attention** - Unresolved calls exceed resolved")
            
            st.metric("Resolved", len(resolved_calls))
            st.metric("Unresolved", len(unresolved_calls))
    
    with insight_col2:
        with st.container():
            st.markdown("#### ⏱️ Urgency Trends")
            
            if len(high_urgency) > 0:
                high_urgency_rate = (len(high_urgency) / total_calls * 100)
                if high_urgency_rate > 30:
                    st.warning(f"**High** - {high_urgency_rate:.1f}% of calls are urgent")
                elif high_urgency_rate > 15:
                    st.info(f"**Moderate** - {high_urgency_rate:.1f}% of calls are urgent")
                else:
                    st.success(f"**Low** - Only {high_urgency_rate:.1f}% urgent calls")
            else:
                st.success("**Excellent** - No high urgency calls")
    
    # ==================== ACTIONABLE RECOMMENDATIONS ====================
    st.markdown("---")
    st.subheader("🎯 Actionable Recommendations")
    
    recommendations = []
    
    # Recommendation 1: High-risk calls
    if high_risk_calls:
        recommendations.append({
            "priority": "High",
            "action": "Immediate escalation",
            "details": f"Escalate {len(high_risk_calls)} unresolved high-urgency calls"
        })
    
    # Recommendation 2: Negative sentiment
    negative_rate = (len(negative_sentiment) / total_calls * 100) if total_calls else 0
    if negative_rate > 25:
        recommendations.append({
            "priority": "Medium",
            "action": "Improve customer satisfaction",
            "details": f"Negative sentiment rate is {negative_rate:.1f}% - review communication protocols"
        })
    
    # Recommendation 3: Top issue category
    if issue_counts:
        top_issue = max(issue_counts, key=issue_counts.get)
        top_issue_count = issue_counts[top_issue]
        if top_issue_count / total_calls > 0.3:  # If >30% of calls
            recommendations.append({
                "priority": "Medium",
                "action": "Address recurring issue",
                "details": f"'{top_issue}' accounts for {top_issue_count} calls ({top_issue_count/total_calls*100:.1f}%)"
            })
    
    # Recommendation 4: Resolution rate
    resolution_rate = (len(resolved_calls) / total_calls * 100) if total_calls else 0
    if resolution_rate < 70:
        recommendations.append({
            "priority": "High",
            "action": "Improve resolution process",
            "details": f"Resolution rate is {resolution_rate:.1f}% - target should be >80%"
        })
    
    # Display recommendations
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            priority_color = {
                "High": "🔴",
                "Medium": "🟡",
                "Low": "🟢"
            }.get(rec["priority"], "⚪")
            
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown(f"### {priority_color}")
                    st.caption(rec["priority"])
                with col2:
                    st.markdown(f"**{rec['action']}**")
                    st.write(rec["details"])
                if i < len(recommendations):
                    st.divider()
    else:
        st.success("✅ All metrics within target ranges")
        st.caption("No immediate actions required - continue monitoring")
    
    # ==================== QUICK STATS ====================
    st.markdown("---")
    
    with st.expander("📋 Quick Statistics", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Call Outcomes**")
            st.write(f"• Resolved: {len(resolved_calls)}")
            st.write(f"• Unresolved: {len(unresolved_calls)}")
        
        with col2:
            st.write("**Sentiment Distribution**")
            for sentiment, count in sentiment_counts.items():
                st.write(f"• {sentiment}: {count}")
        
        with col3:
            st.write("**Urgency Levels**")
            for urgency, count in urgency_counts.items():
                st.write(f"• {urgency}: {count}")
    
    # Last update timestamp
    if calls:
        latest_call = max(calls, key=lambda x: x.get('created_at', ''))
        st.caption(f"📅 Data updated: {format_timestamp(latest_call.get('created_at', ''))}")

