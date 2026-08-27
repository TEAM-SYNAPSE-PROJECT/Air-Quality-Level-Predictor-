import streamlit as st
import pandas as pd
from components.navbar import render_command_header
from services.auth_service import is_logged_in, sync_current_user, save_feedback, load_feedback
from components.page_theme import prepare_page

st.set_page_config(page_title="Feedback | Air Quality Predictor", page_icon="⭐", layout="wide")
prepare_page()
render_command_header(city="Feedback Center",state="User Feedback & Quality",status="OPERATIONAL")
st.markdown('<div class="page-chip">COMMUNITY QUALITY LOOP</div>',unsafe_allow_html=True)
st.title("⭐ Feedback Center")
st.caption("Feedback is stored in the persistent SQLite database and associated with the signed-in Google account.")

user=sync_current_user()
if not user:
    st.info("Please sign in with Google before submitting feedback so your feedback is tied to a real account.")
    st.stop()

left,right=st.columns([1.05,1.25])
with left:
    st.markdown(f"**Signed in:** {user['name']}  ")
    st.caption(user['email'])
    with st.form("feedback_form",clear_on_submit=True):
        rating=st.select_slider("Overall Platform Rating",options=[1,2,3,4,5],value=5,format_func=lambda x:"⭐"*x)
        category=st.selectbox("Feedback Category",["Sensor / Data Accuracy","ML Forecast Evaluation","Feature Request","UI / Usability","General Experience"])
        comments=st.text_area("Detailed Comments / Suggestions",placeholder="Tell us what worked, what felt dull, or what should improve.")
        if st.form_submit_button("🚀 Submit Feedback",use_container_width=True):
            if comments.strip():
                save_feedback(user,rating,category,comments.strip()); st.success("Feedback saved to the database.")
            else: st.error("Please enter your comments.")
with right:
    st.markdown("### 📋 Recent Community Feedback")
    rows=load_feedback(100)
    if rows: st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
    else: st.info("No feedback has been submitted yet.")
