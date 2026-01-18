# frontend/pages/analytics_dashboard.py

import streamlit as st
import requests
from utils.time import format_timestamp
from config import API_BASE

def render():
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
