"""
Page 4: Interactive Geospatial Air Quality Map of India.
"""
import streamlit as st
from components.page_theme import prepare_page
import pandas as pd
from streamlit_folium import st_folium
from services.air_quality_service import get_india_wide_monitoring_status
from services.location_service import find_nearest_monitoring_station
from components.navbar import render_command_header
from components.maps import create_folium_air_quality_map, create_plotly_india_risk_map

st.set_page_config(page_title="Live Map | Air Quality Predictor", page_icon="🗺️", layout="wide")

prepare_page()


if "selected_lat" not in st.session_state:
    st.session_state.selected_lat = 28.6139
if "selected_lon" not in st.session_state:
    st.session_state.selected_lon = 77.2090
if "selected_city" not in st.session_state:
    st.session_state.selected_city = "Delhi"
if "selected_state" not in st.session_state:
    st.session_state.selected_state = "Delhi"
if "is_live_gps" not in st.session_state:
    st.session_state.is_live_gps = False

status_summary = get_india_wide_monitoring_status()
df_india = status_summary["dataset_df"]

nearest_stn = find_nearest_monitoring_station(
    st.session_state.selected_lat,
    st.session_state.selected_lon
)

render_command_header(
    city=st.session_state.selected_city,
    state=st.session_state.selected_state,
    lat=st.session_state.selected_lat,
    lon=st.session_state.selected_lon,
    status="GEOSPATIAL"
)

st.markdown("### 🗺️ INTERACTIVE INDIA AIR QUALITY HEATMAP & STATIONS")
st.caption("Geospatial distribution of continuous air monitoring stations color-coded by Indian CPCB severity levels.")

# Map Controls
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 1.5, 1])

with ctrl_col1:
    map_engine = st.radio("Map Rendering Engine", ["Interactive Folium Canvas", "Plotly Vector Mapbox"], horizontal=True)

with ctrl_col2:
    category_filter = st.multiselect(
        "Filter by AQI Category",
        ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"],
        default=["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
    )

with ctrl_col3:
    focus_city = st.selectbox("Focus City Coordinates", ["Active User Location", "All India View"] + sorted(list(df_india["city"].unique())))

filtered_df = df_india[df_india["aqi_category"].isin(category_filter)] if category_filter else df_india

# Coordinates for center
center_lat = st.session_state.selected_lat
center_lon = st.session_state.selected_lon
zoom_level = 8 if st.session_state.is_live_gps else 6

if focus_city == "All India View":
    center_lat, center_lon, zoom_level = 22.5937, 78.9629, 5
elif focus_city != "Active User Location":
    match = df_india[df_india["city"] == focus_city]
    if not match.empty:
        center_lat = float(match.iloc[0]["latitude"])
        center_lon = float(match.iloc[0]["longitude"])
        zoom_level = 9

if map_engine == "Interactive Folium Canvas":
    folium_map = create_folium_air_quality_map(
        filtered_df,
        user_lat=center_lat,
        user_lon=center_lon,
        user_city=st.session_state.selected_city,
        user_state=st.session_state.selected_state,
        is_live_gps=st.session_state.is_live_gps,
        nearest_station=nearest_stn,
        zoom_start=zoom_level
    )
    st_folium(folium_map, width="100%", height=560)
else:
    plotly_fig = create_plotly_india_risk_map(filtered_df, selected_city=focus_city if focus_city not in ["All India View", "Active User Location"] else st.session_state.selected_city)
    st.plotly_chart(plotly_fig, use_container_width=True)

# Legend Bar
st.markdown("""
<div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 8px; margin-top: 14px; background: #111111; border: 1px solid #222222; padding: 12px; border-radius: 6px;">
    <div style="display: flex; align-items: center; gap: 6px;"><span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #10b981;"></span><span style="font-size: 11px; color: #888888; font-weight: 600;">Good (0-50)</span></div>
    <div style="display: flex; align-items: center; gap: 6px;"><span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #34d399;"></span><span style="font-size: 11px; color: #888888; font-weight: 600;">Satisfactory (51-100)</span></div>
    <div style="display: flex; align-items: center; gap: 6px;"><span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #c5a368;"></span><span style="font-size: 11px; color: #888888; font-weight: 600;">Moderate (101-200)</span></div>
    <div style="display: flex; align-items: center; gap: 6px;"><span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #eab308;"></span><span style="font-size: 11px; color: #888888; font-weight: 600;">Poor (201-300)</span></div>
    <div style="display: flex; align-items: center; gap: 6px;"><span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #f97316;"></span><span style="font-size: 11px; color: #888888; font-weight: 600;">Very Poor (301-400)</span></div>
    <div style="display: flex; align-items: center; gap: 6px;"><span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #ef4444;"></span><span style="font-size: 11px; color: #888888; font-weight: 600;">Severe (401-500+)</span></div>
</div>
""", unsafe_allow_html=True)
