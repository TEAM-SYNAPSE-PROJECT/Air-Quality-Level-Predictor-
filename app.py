"""
Air Quality Level Predictor - Main Command Center.
Live India-Wide Air Quality & Environmental Intelligence Platform.
Full support for Live Browser GPS Location, Nearest Monitoring Station Analytics,
Dynamic CPCB AQI Calculation, Weather Integration, and Embedded AI Assistance.
"""
import streamlit as st
import pandas as pd
from utils.time_utils import get_live_time_metrics
from utils.season_utils import get_current_season
from services.air_quality_service import (
    fetch_live_city_air_quality,
    get_india_wide_monitoring_status
)
from services.weather_service import get_live_weather
from services.location_service import (
    load_indian_cities,
    get_states_and_cities,
    find_nearest_monitoring_station,
    reverse_geocode_coordinates
)
from ml.forecasting import generate_multi_horizon_forecast
from ml.early_warning import evaluate_early_warnings
from components.navbar import render_command_header
from components.gauges import render_aqi_gauge
from components.cards import render_metric_card, render_pollutant_breakdown_grid
from components.charts import render_forecast_horizon_chart
from components.alerts import render_alert_banners
from components.page_theme import prepare_page
from components.location_card import (
    render_location_action_bar,
    render_accuracy_warning_banner,
    render_location_aqi_table
)

# Page configuration
st.set_page_config(
    page_title="Air Quality Level Predictor | Command Center",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

prepare_page()

# Load custom CSS
try:
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

# Session State Initialization
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
if "gps_denied" not in st.session_state:
    st.session_state.gps_denied = False

# Process URL query parameters if browser GPS was triggered
query_params = st.query_params
if "user_lat" in query_params and "user_lon" in query_params:
    try:
        q_lat = float(query_params["user_lat"])
        q_lon = float(query_params["user_lon"])
        
        # Perform reverse geocoding on coordinates
        rev_geo = reverse_geocode_coordinates(q_lat, q_lon)
        st.session_state.selected_lat = q_lat
        st.session_state.selected_lon = q_lon
        st.session_state.selected_city = rev_geo.get("city") or "Detected Location"
        st.session_state.selected_state = rev_geo.get("state") or "India"
        st.session_state.detected_district = rev_geo.get("district") or st.session_state.selected_city
        st.session_state.is_live_gps = True
        st.session_state.gps_denied = False
    except Exception:
        pass
elif "loc_error" in query_params:
    st.session_state.gps_denied = True

# Sidebar: Navigation & Manual Location Selector
with st.sidebar:
    st.markdown("### 📍 Location Navigation")
    state_cities = get_states_and_cities()
    states_list = sorted(list(state_cities.keys()))
    
    # State selector
    current_state_idx = states_list.index(st.session_state.selected_state) if st.session_state.selected_state in states_list else 0
    sel_state = st.selectbox("Select State / UT", states_list, index=current_state_idx)
    
    avail_cities = state_cities.get(sel_state, [])
    city_names = [c["city"] for c in avail_cities]
    
    current_city_idx = city_names.index(st.session_state.selected_city) if st.session_state.selected_city in city_names else 0
    sel_city = st.selectbox("Select City", city_names, index=current_city_idx)
    
    matched_city = next((c for c in avail_cities if c["city"] == sel_city), None)
    if matched_city:
        if (matched_city["city"] != st.session_state.selected_city and not st.session_state.is_live_gps) or (matched_city["city"] != st.session_state.selected_city and st.session_state.get("_last_manual_city") != sel_city):
            st.session_state.selected_city = matched_city["city"]
            st.session_state.selected_state = matched_city["state"]
            st.session_state.selected_lat = matched_city["lat"]
            st.session_state.selected_lon = matched_city["lon"]
            st.session_state.detected_district = matched_city["city"]
            st.session_state.is_live_gps = False
            st.session_state._last_manual_city = sel_city
        
    st.markdown("---")
    
    # Manual Custom Coordinates
    with st.expander("🛠️ Custom GPS Coordinates"):
        c_lat = st.number_input("Latitude", value=float(st.session_state.selected_lat), format="%.6f")
        c_lon = st.number_input("Longitude", value=float(st.session_state.selected_lon), format="%.6f")
        if st.button("Set Custom Location", use_container_width=True):
            rev = reverse_geocode_coordinates(c_lat, c_lon)
            st.session_state.selected_lat = c_lat
            st.session_state.selected_lon = c_lon
            st.session_state.selected_city = rev.get("city") or "Custom Site"
            st.session_state.selected_state = rev.get("state") or "India"
            st.session_state.detected_district = rev.get("district") or st.session_state.selected_city
            st.session_state.is_live_gps = False
            st.toast(f"Updated location to: {st.session_state.selected_city}")
            st.rerun()

    # Quick Location Switch
    st.markdown("#### 🎯 Quick Metropolitan Switch")
    q_col1, q_col2 = st.columns(2)
    if q_col1.button("📍 Mumbai", use_container_width=True):
        st.session_state.selected_city = "Mumbai"
        st.session_state.selected_state = "Maharashtra"
        st.session_state.selected_lat = 19.0760
        st.session_state.selected_lon = 72.8777
        st.session_state.detected_district = "Mumbai City"
        st.session_state.is_live_gps = False
        st.rerun()
    if q_col2.button("📍 Bengaluru", use_container_width=True):
        st.session_state.selected_city = "Bengaluru"
        st.session_state.selected_state = "Karnataka"
        st.session_state.selected_lat = 12.9716
        st.session_state.selected_lon = 77.5946
        st.session_state.detected_district = "Bengaluru Urban"
        st.session_state.is_live_gps = False
        st.rerun()
        
    q_col3, q_col4 = st.columns(2)
    if q_col3.button("📍 Hyderabad", use_container_width=True):
        st.session_state.selected_city = "Hyderabad"
        st.session_state.selected_state = "Telangana"
        st.session_state.selected_lat = 17.3850
        st.session_state.selected_lon = 78.4867
        st.session_state.detected_district = "Hyderabad"
        st.session_state.is_live_gps = False
        st.rerun()
    if q_col4.button("📍 Vijayawada", use_container_width=True):
        st.session_state.selected_city = "Vijayawada"
        st.session_state.selected_state = "Andhra Pradesh"
        st.session_state.selected_lat = 16.5062
        st.session_state.selected_lon = 80.6480
        st.session_state.detected_district = "NTR"
        st.session_state.is_live_gps = False
        st.rerun()

# 1. Fetch Real-Time Data & Nearest Station for Active Coordinates
t_metrics = get_live_time_metrics("Asia/Kolkata")
season = get_current_season(t_metrics["datetime"])

nearest_station = find_nearest_monitoring_station(
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

# Multi-horizon forecast
forecast_data = generate_multi_horizon_forecast(aq_data["pollutants"], weather_context={
    "temperature": weather_data["temperature"],
    "humidity": weather_data["humidity"],
    "wind_speed": weather_data["wind_speed"],
    "pressure": weather_data["pressure"]
})

# India-wide aggregate stats
india_status = get_india_wide_monitoring_status()
df_all_india = india_status["dataset_df"]

# Early warnings
active_warnings = evaluate_early_warnings(
    current_aqi=aq_data["aqi"],
    current_pm25=aq_data["pollutants"].get("pm25"),
    current_pm10=aq_data["pollutants"].get("pm10"),
    sub_indices=aq_data.get("sub_indices", {}),
    recent_trend_delta=12.0,
    forecast_aqi_max=forecast_data[2]["predicted_aqi"] if len(forecast_data) > 2 else None,
    is_anomaly=False
)

# 2. Render Command Header
render_command_header(
    city=st.session_state.selected_city,
    state=st.session_state.selected_state,
    lat=st.session_state.selected_lat,
    lon=st.session_state.selected_lon,
    status=aq_data["status"]
)

# If permission was denied, display helpful non-blocking notification
if st.session_state.gps_denied:
    st.warning("📍 Location permission was not granted. Please allow location access in your browser or select a city manually from the sidebar.")

# 3. Live Location Action Bar & Status Cards (Requirements 30-34 & 52)
render_location_action_bar(
    detected_city=st.session_state.selected_city,
    detected_state=st.session_state.selected_state,
    detected_district=st.session_state.detected_district,
    detected_lat=st.session_state.selected_lat,
    detected_lon=st.session_state.selected_lon,
    is_live_gps=st.session_state.is_live_gps,
    nearest_station=nearest_station
)

# Sensor proximity accuracy banner (Requirements 34 & 50)
render_accuracy_warning_banner(
    distance_km=nearest_station["distance_km"],
    station_name=nearest_station["station"]
)

# 4. Active Warning Banners
if active_warnings:
    render_alert_banners(active_warnings)

# 5. Main Telemetry Dashboard Row: Large Gauge AQI + Live Weather + Health Advisory
col_gauge, col_weather, col_risk = st.columns([1.2, 1.1, 1.1])

with col_gauge:
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

with col_weather:
    st.markdown("#### 🌦️ Live Weather & Meteorology")
    render_metric_card("Surface Temperature", f"{weather_data['temperature']} °C", f"Feels like {weather_data['feels_like']} °C", weather_data["weather_condition"], "#f59e0b")
    render_metric_card("Relative Humidity", f"{weather_data['humidity']} %", "Atmospheric moisture saturation", "Hygro", "#38bdf8")
    render_metric_card("Surface Wind", f"{weather_data['wind_speed']} km/h", f"Direction: {weather_data['wind_direction']}° | Plume Dispersion", "Anemo", "#10b981")

with col_risk:
    st.markdown("#### 🛡️ Environmental Risk & Health")
    risk_info = aq_data.get("risk_details", {})
    st.markdown(f"""
    <div class="telemetry-card" style="border-left: 4px solid {risk_info.get('badge_color', '#f59e0b')};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 14px; font-weight: 700; color: #f8fafc;">Assessed Health Risk</span>
            <span style="background: {risk_info.get('badge_color', '#f59e0b')}33; color: {risk_info.get('badge_color', '#f59e0b')}; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 700;">{risk_info.get('risk_level', 'Moderate').upper()}</span>
        </div>
        <div style="font-size: 13px; color: #e2e8f0; margin-top: 8px; line-height: 1.5;">
            {risk_info.get('summary', 'Standard outdoor conditions.')}
        </div>
        <hr style="border-color: rgba(75, 85, 99, 0.4); margin: 8px 0;"/>
        <div style="font-size: 12px; color: #cbd5e1; line-height: 1.6;">
            • <strong>Outdoor Exercise:</strong> {risk_info.get('outdoor_exercise', 'Acceptable')}<br/>
            • <strong>N95 Respirator:</strong> {'Strongly Recommended' if risk_info.get('mask_recommended') else 'Not Required'}<br/>
            • <strong>Vulnerable Groups:</strong> {risk_info.get('sensitive_advisory', 'Limit heavy exertion.')}
        </div>
    </div>
    """, unsafe_allow_html=True)

# 6. Indian CPCB 6-Pollutant Ambient Concentrations Breakdown
st.markdown("---")
st.markdown("### 🧪 Indian CPCB 6-Pollutant Ambient Concentrations")
st.caption(f"Continuous sensor readings reported by **{nearest_station['station']}** ({nearest_station['distance_km']} km away).")
render_pollutant_breakdown_grid(aq_data["pollutants"], aq_data.get("sub_indices", {}))

# 7. Dynamic Location-Based Comprehensive AQI & Weather Table (Requirements 35 & 46)
st.markdown("---")
st.markdown("### 📋 Location-Based Comprehensive Environmental Telemetry Table")
st.caption("Synchronized atmospheric parameters, sensor metadata, and geographic metrics for your active location.")
render_location_aqi_table(
    aq_data=aq_data,
    weather_data=weather_data,
    nearest_station=nearest_station,
    user_city=st.session_state.selected_city,
    user_state=st.session_state.selected_state,
    time_metrics=t_metrics,
    season_name=season["name"]
)

# 9. Top 10 At-Risk Cities & Machine Learning Forecast Horizon
st.markdown("---")
col_hotspots, col_forecast = st.columns([1.3, 1.1])

with col_hotspots:
    st.markdown("#### 🚨 Top 10 Most At-Risk Indian Cities")
    st.caption("Active monitoring stations reporting highest continuous AQI levels.")
    
    top_risk_df = df_all_india.sort_values(by="aqi", ascending=False).head(10)
    display_top = top_risk_df[["city", "state", "aqi", "aqi_category", "dominant_pollutant", "pm25", "temperature", "risk_level"]].copy()
    display_top.columns = ["City", "State", "NAQI", "Category", "Driver", "PM2.5", "Temp (°C)", "Risk"]
    st.dataframe(display_top, hide_index=True, use_container_width=True)
    
    if st.button("👉 View Full Alert Cities Directory & Diagnostics", use_container_width=True):
        st.switch_page("pages/03_🚨_Alert_Cities.py")

with col_forecast:
    st.markdown("#### 🔮 Machine Learning Multi-Horizon Forecast")
    st.caption(f"Predicted AQI trajectory for **{st.session_state.selected_city}** (Gradient Boosted Trees).")
    st.plotly_chart(render_forecast_horizon_chart(forecast_data, aq_data["aqi"]), use_container_width=True)

# 10. National Air Quality Monitoring Summary
st.markdown("---")
st.markdown("### 🇮🇳 National Air Quality Monitoring Summary")
st.caption("Aggregated indicators calculated dynamically across all continuous monitoring locations in India.")

i_col1, i_col2, i_col3, i_col4 = st.columns(4)
with i_col1:
    render_metric_card("Total Cities Monitored", f"{india_status['total_monitored']}", "Continuous ambient monitoring network", "Coverage", "#38bdf8")
with i_col2:
    render_metric_card("Cities Currently At Risk", f"{india_status['cities_at_risk']}", "AQI > 200 (Poor, Very Poor, Severe)", "Critical", "#ef4444")
with i_col3:
    render_metric_card("Cities with Clean Air", f"{india_status['cities_good_satisfactory']}", "AQI <= 100 (Good & Satisfactory)", "Healthy", "#10b981")
with i_col4:
    render_metric_card("Cities Requiring Attention", f"{india_status['cities_requiring_attention']}", "AQI 101 - 200 (Moderate)", "Watchlist", "#f59e0b")
