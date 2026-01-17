import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Customer Support Call Analytics",
    layout="wide"
)

st.title("📞 Customer Support Call Analytics")
st.write("Upload a customer support call and extract insights using AI.")


st.header("Upload Call Audio")

uploaded_file = st.file_uploader(
    "Upload a .wav audio file",
    type=["wav"]
)

if uploaded_file:
    st.audio(uploaded_file)

    if st.button("Analyze Call"):
        with st.spinner("Analyzing call..."):
            files = {
                "file": (uploaded_file.name, uploaded_file, "audio/wav")
            }

            response = requests.post(
                f"{API_BASE}/analyze-call",
                files=files
            )

        if response.status_code == 200:
            result = response.json()

            st.success("Analysis completed!")

            st.subheader("Transcript")
            st.write(result["transcript"])

            st.subheader("Extracted Insights")
            st.json(result["insights"])
        else:
            st.error(f"Error: {response.text}")


st.divider()
st.header("📊 Call Analytics Summary")

if st.button("Refresh Analytics"):
    summary_response = requests.get(f"{API_BASE}/calls/summary")

    if summary_response.status_code == 200:
        summary = summary_response.json()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Sentiment Distribution")
            st.bar_chart(summary.get("sentiment_distribution", {}))

        with col2:
            st.subheader("Urgency Distribution")
            st.bar_chart(summary.get("urgency_distribution", {}))

        with col3:
            st.subheader("Call Outcome Distribution")
            st.bar_chart(summary.get("call_outcome_distribution", {}))
    else:
        st.error("Failed to fetch analytics")
