"""
Command Center Header & Telemetry Navbar.
Renders real-time temporal parameters, dynamic season, active geolocation,
and data provenance status without hardcoding.
"""
import streamlit as st
from utils.time_utils import get_live_time_metrics
from utils.season_utils import get_current_season

def render_command_header(city: str = "Delhi", state: str = "Delhi", lat: float = 28.61, lon: float = 77.20, status: str = "LIVE"):
    """Renders the top environmental command center banner."""
    t_metrics = get_live_time_metrics("Asia/Kolkata")
    season = get_current_season(t_metrics["datetime"])
    
    # Status pill color mapping
    status_class_map = {
        "LIVE": "status-live",
        "RECENT": "status-cached",
        "CACHED": "status-cached",
        "LOCAL DATA": "status-local",
        "DEMO": "status-demo"
    }
    pill_class = status_class_map.get(status, "status-live")
    
    header_html = f"""
    <div class="command-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
            <div>
                <div class="command-title">
                    <span style="font-size: 24px;">🇮🇳</span>
                    <span>AIR QUALITY <span class="accent-gold">LEVEL PREDICTOR</span></span>
                </div>
                <div class="command-subtitle">
                    National Environmental & Air Intelligence Command Center
                </div>
                <div style="display: flex; gap: 12px; align-items: center; margin-top: 10px; flex-wrap: wrap; font-size: 12px; color: #888888;">
                    <span>📍 <strong style="color: #F5F5F5;">{city}, {state}</strong> <span style="color: #555555;">({lat:.4f}°N, {lon:.4f}°E)</span></span>
                    <span style="color: #2A2A2A;">|</span>
                    <span>📅 <strong style="color: #F5F5F5;">{t_metrics['date_str']}</strong> <span style="color: #666666;">({t_metrics['day_name']})</span></span>
                    <span style="color: #2A2A2A;">|</span>
                    <span>🕒 <strong style="color: #F5F5F5;">{t_metrics['time_str']} IST</strong> <span style="color: #C5A368;">(Asia/Kolkata)</span></span>
                    <span style="color: #2A2A2A;">|</span>
                    <span>{season['emoji']} Season: <strong style="color: #C5A368;">{season['name'].upper()}</strong></span>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px;">
                <div class="status-pill {pill_class}">
                    <span>●</span>
                    <span>SOURCE: {status}</span>
                </div>
                <div style="font-size: 10px; color: #555555; font-family: monospace; letter-spacing: 0.05em;">
                    REFRESHED: {t_metrics['time_str']}
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
