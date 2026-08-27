import streamlit as st
import pandas as pd
from components.page_theme import apply_page_theme, render_profile_sidebar
from services.auth_service import is_logged_in, sync_current_user, load_feedback, list_users

st.set_page_config(page_title="Profile | Air Quality Predictor", page_icon="👤", layout="wide")
apply_page_theme("profile")
render_profile_sidebar()

user=sync_current_user()
if not user:
    st.title("👤 Profile")
    st.info("Please sign in with Google to view your profile.")
    st.switch_page("pages/Login.py")

st.markdown('<div class="page-chip">PERSONAL ENVIRONMENT PROFILE</div>', unsafe_allow_html=True)
st.title(f"👤 {user['name']}")
st.caption("Your account information is linked to the Google identity used to sign in.")

c1,c2=st.columns([1,2])
with c1:
    if user.get("picture"): st.image(user["picture"], width=140)
with c2:
    st.markdown(f"**Email:** {user['email']}")
    st.markdown(f"**Email verified:** {'Yes' if user.get('email_verified') else 'Not reported'}")
    st.markdown(f"**First sign-in:** {user.get('first_login_utc','N/A')}")
    st.markdown(f"**Last sign-in:** {user.get('last_login_utc','N/A')}")

st.markdown("---")
st.subheader("📊 Your submitted feedback")
rows=[x for x in load_feedback(200) if x.get("email")==user.get("email")]
if rows: st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
else: st.info("No feedback submitted yet.")
