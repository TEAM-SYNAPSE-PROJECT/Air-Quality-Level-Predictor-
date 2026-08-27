"""Shared visual system for distinct page backgrounds, profile controls and polished UI."""
from pathlib import Path
import inspect
import streamlit as st
from services.auth_service import sync_current_user, is_logged_in, login_button, logout_button

THEMES = {
    "dashboard": ("#071b2d", "#081f1a", "#102a43"),
    "india": ("#21103b", "#102a43", "#301934"),
    "alerts": ("#2a0f1b", "#24101f", "#402218"),
    "map": ("#062c2c", "#08243a", "#123c4a"),
    "pollutants": ("#102d20", "#201438", "#12334a"),
    "eda": ("#20152f", "#102b36", "#2d1f0d"),
    "prediction": ("#18104a", "#0b2d42", "#32153f"),
    "weather": ("#092a45", "#123b56", "#17364d"),
    "risk": ("#321116", "#2a1b0b", "#3a162b"),
    "anomaly": ("#24122e", "#10253b", "#321f0c"),
    "calculator": ("#0c2933", "#18213d", "#102f22"),
    "reduce": ("#0b2e26", "#123b2a", "#26320f"),
    "assistant": ("#071a3d", "#24104f", "#063b3b"),
    "reports": ("#2c1b08", "#18233b", "#32132b"),
    "feedback": ("#2b1836", "#172e43", "#362014"),
    "about": ("#101a2f", "#26324a", "#132e2a"),
    "deep": ("#160f35", "#0b3040", "#30200f"),
    "profile": ("#101d36", "#172d28", "#2b1938"),
    "login": ("#071b2d", "#20103d", "#123b35"),
}

def _theme_from_file():
    name=Path(__file__).stem
    caller=Path(inspect.stack()[2].filename).name.lower()
    page=Path(st.session_state.get("_active_page_file", caller)).name.lower()
    mapping={"01_":"dashboard","02_":"india","03_":"alerts","04_":"map","05_":"pollutants","06_":"eda","07_":"prediction","08_":"weather","09_":"risk","10_":"anomaly","11_":"calculator","12_":"reduce","13_":"assistant","14_":"reports","15_":"feedback","16_":"about","17_":"deep","18_":"profile","00_":"login"}
    for key,val in mapping.items():
        if page.startswith(key): return val
    return "dashboard"

def apply_page_theme(theme=None):
    if theme is None:
        theme=_theme_from_file()
    a,b,c=THEMES.get(theme, THEMES["dashboard"])
    css = """<style>
    :root { --page-a:__A__; --page-b:__B__; --page-c:__C__; }
    [data-testid="stAppViewContainer"] { background: radial-gradient(circle at 8% 8%, __A__ 0%, transparent 34%), radial-gradient(circle at 92% 18%, __B__ 0%, transparent 36%), radial-gradient(circle at 50% 100%, __C__ 0%, #060912 62%); background-attachment: fixed; }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 1.4rem; padding-bottom: 4rem; }
    .telemetry-card { backdrop-filter: blur(14px); background: rgba(11,16,29,.70) !important; border:1px solid rgba(255,255,255,.10) !important; box-shadow:0 12px 34px rgba(0,0,0,.22); border-radius:18px !important; }
    .telemetry-card:hover { transform: translateY(-2px); border-color: rgba(255,255,255,.20) !important; }
    .command-header { background: linear-gradient(135deg, rgba(255,255,255,.08), rgba(255,255,255,.025)) !important; border:1px solid rgba(255,255,255,.12) !important; border-radius:22px !important; box-shadow:0 18px 55px rgba(0,0,0,.25) !important; }
    div[data-testid="stSidebar"] { background: linear-gradient(180deg, rgba(5,10,22,.96), rgba(12,18,34,.94)) !important; }
    .page-chip { display:inline-block; padding:6px 11px; border-radius:999px; background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.12); color:#dbeafe; font-size:11px; letter-spacing:.12em; text-transform:uppercase; }
    .profile-mini { padding:12px; border-radius:16px; background:rgba(255,255,255,.055); border:1px solid rgba(255,255,255,.09); margin:8px 0 14px; }
    </style>"""
    css=css.replace("__A__",a).replace("__B__",b).replace("__C__",c)
    st.markdown(css, unsafe_allow_html=True)

def render_profile_sidebar():
    user=sync_current_user()
    st.sidebar.markdown("### 👤 Account")
    if user:
        picture=user.get("picture")
        if picture:
            st.sidebar.image(picture, width=54)
        st.sidebar.markdown(f'<div class="profile-mini"><b>{user.get("name","Google User")}</b><br><span style="color:#9ca3af;font-size:12px">{user.get("email","")}</span></div>', unsafe_allow_html=True)
        if st.sidebar.button("👤 Open Profile", use_container_width=True):
            st.switch_page("pages/18_👤_Profile.py")
        logout_button()
    else:
        st.sidebar.caption("Sign in to save your profile and unlock downloads.")
        login_button()

def prepare_page():
    st.session_state["_active_page_file"] = inspect.stack()[1].filename
    apply_page_theme()
    render_profile_sidebar()
