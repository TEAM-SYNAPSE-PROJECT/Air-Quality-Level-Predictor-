import streamlit as st
from components.page_theme import apply_page_theme
from services.auth_service import is_logged_in, login_button, sync_current_user

st.set_page_config(page_title="Sign In | Air Quality Predictor", page_icon="🔐", layout="wide")
apply_page_theme("login")

st.markdown('<div style="max-width:720px;margin:7vh auto 0;text-align:center">', unsafe_allow_html=True)
st.markdown('<div class="page-chip">SECURE ACCOUNT ACCESS</div>', unsafe_allow_html=True)
st.title("Welcome to Air Quality Intelligence")
st.write("Sign in with your Google account to access your personal profile and unlock authenticated data downloads.")
if is_logged_in():
    user=sync_current_user()
    st.success(f"You are signed in as {user['name']} ({user['email']}).")
    if st.button("👤 Open my profile", use_container_width=True): st.switch_page("pages/18_Profile.py")
    if st.button("🏠 Return to dashboard", use_container_width=True): st.switch_page("app.py")
else:
    login_button("Continue with Google")
    st.caption("Authentication uses Google OpenID Connect. No password is stored by this application.")
st.markdown('</div>', unsafe_allow_html=True)