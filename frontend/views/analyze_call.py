# frontend/pages/analyze_call.py

import streamlit as st
import requests
import json
from config import API_BASE

def render():
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
