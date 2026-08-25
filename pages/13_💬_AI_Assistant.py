"""
Page 13: Fullscreen Conversational Environmental AI Assistant.
"""
import streamlit as st
from utils.time_utils import get_live_time_metrics
from utils.season_utils import get_current_season
from services.air_quality_service import fetch_live_city_air_quality
from services.weather_service import get_live_weather
from services.location_service import load_indian_cities
from ml.forecasting import generate_multi_horizon_forecast
from components.navbar import render_command_header
from components.chatbot_ui import render_embedded_chatbot

st.set_page_config(page_title="AI Assistant | Air Quality Predictor", page_icon="💬", layout="wide")

with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

cities = load_indian_cities()
city_names = [c["city"] for c in cities]

with st.sidebar:
    st.markdown("### 📍 Location Context for Assistant")
    active_city_name = st.selectbox("Active Monitoring City", city_names, index=city_names.index("Delhi") if "Delhi" in city_names else 0)
    city_obj = next((c for c in cities if c["city"] == active_city_name), cities[0])

# Fetch Telemetry Context
t_metrics = get_live_time_metrics("Asia/Kolkata")
season = get_current_season(t_metrics["datetime"])
aq_data = fetch_live_city_air_quality(city_obj["lat"], city_obj["lon"], city_obj["city"], city_obj["state"])
weather = get_live_weather(city_obj["lat"], city_obj["lon"], city_obj["city"])
forecasts = generate_multi_horizon_forecast(aq_data["pollutants"])

live_context = {
    "city": city_obj["city"],
    "state": city_obj["state"],
    "latitude": city_obj["lat"],
    "longitude": city_obj["lon"],
    "aqi": aq_data["aqi"],
    "aqi_category": aq_data["aqi_category"],
    "dominant_pollutant": aq_data["dominant_pollutant"],
    "risk_level": aq_data["risk_level"],
    "risk_details": aq_data.get("risk_details", {}),
    "health_statement": aq_data.get("health_statement", ""),
    "pollutants": aq_data["pollutants"],
    "sub_indices": aq_data.get("sub_indices", {}),
    "temperature": weather["temperature"],
    "feels_like": weather["feels_like"],
    "humidity": weather["humidity"],
    "wind_speed": weather["wind_speed"],
    "wind_direction": weather["wind_direction"],
    "pressure": weather["pressure"],
    "rainfall": weather["rainfall"],
    "weather_condition": weather["weather_condition"],
    "season": season["name"],
    "time_str": t_metrics["time_str"],
    "date_str": t_metrics["date_str"],
    "hour": t_metrics["datetime"].hour,
    "data_status": aq_data["status"],
    "forecasts": forecasts
}

render_command_header(city=city_obj["city"], state=city_obj["state"], lat=city_obj["lat"], lon=city_obj["lon"], status=aq_data["status"])

render_embedded_chatbot(live_context, key_suffix="fullscreen_page")
