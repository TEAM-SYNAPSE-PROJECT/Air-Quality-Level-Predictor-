"""
Page 1: Comprehensive AQI Dashboard & Sub-Index Analytics.
"""
import streamlit as st
import pandas as pd
from utils.time_utils import get_live_time_metrics
from utils.season_utils import get_current_season
from services.air_quality_service import fetch_live_city_air_quality
from services.weather_service import get_live_weather
from services.location_service import load_indian_cities, get_states_and_cities, find_nearest_monitoring_station
from components.navbar import render_command_header
from components.gauges import render_aqi_gauge
from components.cards import render_metric_card, render_pollutant_breakdown_grid
from components.charts import render_pollutant_trends_chart, render_driver_breakdown_chart
from components.location_card import render_location_action_bar, render_location_aqi_table

st.set_page_config(page_title="AQI Dashboard | Air Quality Predictor", page_icon="📊", layout="wide")

# Apply custom CSS
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# State initialization
if "selected_city" not in st.session_state:
    st.session_state.selected_city = "Delhi"
if "selected_state" not in st.session_state:
    st.session_state.selected_state = "Delhi"
if "selected_lat" not in st.session_state:
    st.session_state.selected_lat = 28.6139
if "selected_lon" not in st.session_state:
    st.session_state.selected_lon = 77.2090
if "detected_district" not in st.session_state:
    st.session_state.detected_district = "Central Delhi"
if "is_live_gps" not in st.session_state:
    st.session_state.is_live_gps = False

# Location Controls
with st.sidebar:
    st.markdown("### 📍 Select Monitoring Location")
    state_cities = get_states_and_cities()
    states_list = sorted(list(state_cities.keys()))
    
    sel_state = st.selectbox("State / Territory", states_list, index=states_list.index(st.session_state.selected_state) if st.session_state.selected_state in states_list else 0)
    avail_cities = state_cities.get(sel_state, [])
    city_names = [c["city"] for c in avail_cities]
    
    sel_city = st.selectbox("City", city_names, index=city_names.index(st.session_state.selected_city) if st.session_state.selected_city in city_names else 0)
    
    # Update selected coordinates
    matched = next((c for c in avail_cities if c["city"] == sel_city), None)
    if matched and (matched["city"] != st.session_state.selected_city):
        st.session_state.selected_city = matched["city"]
        st.session_state.selected_state = matched["state"]
        st.session_state.selected_lat = matched["lat"]
        st.session_state.selected_lon = matched["lon"]
        st.session_state.detected_district = matched["city"]
        st.session_state.is_live_gps = False

# Fetch Telemetry & Nearest Station
nearest_stn = find_nearest_monitoring_station(
    st.session_state.selected_lat,
    st.session_state.selected_lon
)

aq_data = fetch_live_city_air_quality(
    st.session_state.selected_lat,
    st.session_state.selected_lon,
    st.session_state.selected_city,
    st.session_state.selected_state
)

weather_data = get_live_weather(
    st.session_state.selected_lat,
    st.session_state.selected_lon,
    st.session_state.selected_city
)

t_metrics = get_live_time_metrics("Asia/Kolkata")
season = get_current_season(t_metrics["datetime"])

# Header
render_command_header(
    city=st.session_state.selected_city,
    state=st.session_state.selected_state,
    lat=st.session_state.selected_lat,
    lon=st.session_state.selected_lon,
    status=aq_data["status"]
)

# Render Location Action & Sensor Card
render_location_action_bar(
    detected_city=st.session_state.selected_city,
    detected_state=st.session_state.selected_state,
    detected_district=st.session_state.detected_district,
    detected_lat=st.session_state.selected_lat,
    detected_lon=st.session_state.selected_lon,
    is_live_gps=st.session_state.is_live_gps,
    nearest_station=nearest_stn
)

# Main Grid: Gauge + Driver Analysis + Weather
col_left, col_mid, col_right = st.columns([1.2, 1.2, 1])

with col_left:
    st.plotly_chart(
        render_aqi_gauge(
            aq_data["aqi"],
            aq_data["aqi_category"],
            dominant_pollutant=aq_data["dominant_pollutant"],
            risk_level=aq_data["risk_level"],
            city_name=st.session_state.selected_city,
            updated_time=aq_data["last_updated"]
        ),
        use_container_width=True
    )

with col_mid:
    st.markdown("#### 🎯 Dominant Pollutant Breakdown")
    drivers = aq_data.get("drivers", {}).get("drivers", [])
    if drivers:
        st.plotly_chart(render_driver_breakdown_chart(drivers), use_container_width=True)
    else:
        st.info("Driver analysis processing...")

with col_right:
    st.markdown("#### 🌦️ Meteorology & Dispersion")
    render_metric_card("Surface Temperature", f"{weather_data['temperature']} °C", f"Feels like {weather_data['feels_like']} °C", "Meteo", "#f59e0b")
    render_metric_card("Relative Humidity", f"{weather_data['humidity']} %", "Atmospheric moisture trapping factor", "Hygro", "#38bdf8")
    render_metric_card("Wind Velocity", f"{weather_data['wind_speed']} km/h", f"Direction: {weather_data['wind_direction']}° | Dispersion Index", "Anemo", "#10b981")

# Pollutant 6-Grid Breakdown
st.markdown("---")
st.markdown("### 🧪 Indian CPCB 6-Pollutant Concentration Breakdown")
render_pollutant_breakdown_grid(aq_data["pollutants"], aq_data.get("sub_indices", {}))

# Comprehensive Location AQI Table
st.markdown("---")
st.markdown("### 📋 Location-Based Comprehensive Environmental Telemetry Table")
render_location_aqi_table(
    aq_data=aq_data,
    weather_data=weather_data,
    nearest_station=nearest_stn,
    user_city=st.session_state.selected_city,
    user_state=st.session_state.selected_state,
    time_metrics=t_metrics,
    season_name=season["name"]
)

# Trend Chart
st.markdown("---")
st.markdown("### 📈 Recent 24-Hour Pollutant Concentrations")
if aq_data.get("hourly_history"):
    df_hist = pd.DataFrame(aq_data["hourly_history"])
    st.plotly_chart(render_pollutant_trends_chart(df_hist, title=f"24-Hour Trend for {st.session_state.selected_city}"), use_container_width=True)
else:
    # Use sample time series
    df_sample = pd.read_csv("data/sample_air_quality.csv").tail(48)
    st.plotly_chart(render_pollutant_trends_chart(df_sample, title=f"Recent Atmospheric Telemetry ({st.session_state.selected_city})"), use_container_width=True)
