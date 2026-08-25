"""
Page 15: User Feedback & Continuous Quality Auditing.
"""
import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
from components.navbar import render_command_header

st.set_page_config(page_title="Feedback | Air Quality Predictor", page_icon="⭐", layout="wide")

with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

render_command_header(city="Feedback Center", state="User Feedback & Quality", status="OPERATIONAL")

st.markdown("### ⭐ USER FEEDBACK & EXPERIENCE AUDITING")
st.caption("Help us enhance environmental sensor calibration, model accuracy, and platform capabilities.")

FEEDBACK_FILE = "data/feedback.json"

def load_feedbacks():
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_feedback(entry):
    entries = load_feedbacks()
    entries.insert(0, entry)
    os.makedirs("data", exist_ok=True)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(entries, f, indent=2)

col_f1, col_f2 = st.columns([1.2, 1])

with col_f1:
    st.markdown("#### Submit Your Assessment")
    with st.form("feedback_form", clear_on_submit=True):
        name = st.text_input("Your Name / Organization", placeholder="e.g. Environmental Researcher / Citizen")
        email = st.text_input("Contact Email (Optional)", placeholder="name@domain.com")
        rating = st.select_slider("Overall Platform Rating", options=[1, 2, 3, 4, 5], value=5, format_func=lambda x: "⭐" * x)
        category = st.selectbox("Feedback Category", ["Sensor / Data Accuracy", "ML Forecast Evaluation", "Feature Request", "UI / Usability", "General Experience"])
        comments = st.text_area("Detailed Comments / Suggestions", placeholder="Provide specific feedback on sensor data, predictions, or improvements...")
        
        submitted = st.form_submit_button("🚀 Submit Feedback", use_container_width=True)
        if submitted:
            if comments.strip():
                entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
                    "name": name.strip() or "Anonymous Citizen",
                    "email": email.strip() or "N/A",
                    "rating": rating,
                    "category": category,
                    "comments": comments.strip()
                }
                save_feedback(entry)
                st.success("✅ Thank you! Your feedback has been recorded successfully.")
            else:
                st.error("Please enter your comments before submitting.")

with col_f2:
    st.markdown("#### 📋 Community Assessments Log")
    feedbacks = load_feedbacks()
    if feedbacks:
        df_feed = pd.DataFrame(feedbacks)
        st.dataframe(df_feed[["timestamp", "name", "rating", "category", "comments"]], hide_index=True, use_container_width=True)
    else:
        st.info("No feedback entries recorded yet. Be the first to submit your review!")
