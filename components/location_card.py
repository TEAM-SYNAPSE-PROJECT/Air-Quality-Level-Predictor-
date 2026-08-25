"""
Interactive Location Module & Dynamic Telemetry Tables.
Provides browser HTML5 Geolocation triggering, manual location selector,
detected location banner, nearest station analysis, and comprehensive parameter tables.
"""
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from typing import Dict, Any, Optional
from services.location_service import reverse_geocode_coordinates, find_nearest_monitoring_station
from utils.helpers import get_aqi_category_info

def render_location_action_bar(
    detected_city: str,
    detected_state: str,
    detected_district: str,
    detected_lat: float,
    detected_lon: float,
    is_live_gps: bool,
    nearest_station: Dict[str, Any]
):
    """
    Renders the prominent Location Header Card, Browser GPS trigger script,
    and manual switch controls as specified in Requirements 30-34 & 52.
    """
    # 1. HTML5 Geolocation Trigger Component
    # When user clicks the primary HTML button or standard button, browser prompts for GPS permission.
    gps_trigger_html = """
    <div style="margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif;">
        <script>
        function requestBrowserGPS() {
            const btn = document.getElementById('gps-btn');
            const statusText = document.getElementById('gps-status');
            if (btn) btn.innerHTML = "⏳ Detecting Satellite Location...";
            if (statusText) statusText.innerHTML = "Requesting device GPS coordinates...";
            
            if (!navigator.geolocation) {
                if (statusText) statusText.innerHTML = "❌ Geolocation is not supported by your browser.";
                if (btn) btn.innerHTML = "📍 MY LOCATION";
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const acc = position.coords.accuracy;
                    if (btn) btn.innerHTML = "✅ Location Acquired!";
                    if (statusText) statusText.innerHTML = "Coordinates: " + lat.toFixed(4) + "°N, " + lon.toFixed(4) + "°E (Accuracy: " + Math.round(acc) + "m)";
                    
                    try {
                        const targetUrl = new URL(window.parent.location.href);
                        targetUrl.searchParams.set('user_lat', lat.toFixed(6));
                        targetUrl.searchParams.set('user_lon', lon.toFixed(6));
                        targetUrl.searchParams.set('loc_source', 'gps');
                        targetUrl.searchParams.set('acc', acc.toFixed(0));
                        targetUrl.searchParams.set('t', Date.now().toString());
                        window.parent.location.href = targetUrl.toString();
                    } catch (e) {
                        window.location.search = "?user_lat=" + lat.toFixed(6) + "&user_lon=" + lon.toFixed(6) + "&loc_source=gps&t=" + Date.now();
                    }
                },
                function(error) {
                    let errMsg = "Location permission was not granted.";
                    if (error.code === 1) {
                        errMsg = "Permission Denied. Please allow location access in your browser or select a city manually.";
                    } else if (error.code === 2) {
                        errMsg = "Position Unavailable. Please check your network or GPS signal.";
                    } else if (error.code === 3) {
                        errMsg = "Location request timed out. Please try again.";
                    }
                    if (btn) btn.innerHTML = "📍 MY LOCATION";
                    if (statusText) statusText.innerHTML = "⚠️ " + errMsg;
                    
                    try {
                        const targetUrl = new URL(window.parent.location.href);
                        targetUrl.searchParams.set('loc_error', 'denied');
                        targetUrl.searchParams.set('t', Date.now().toString());
                        window.parent.location.href = targetUrl.toString();
                    } catch (e) {}
                },
                {
                    enableHighAccuracy: true,
                    timeout: 12000,
                    maximumAge: 0
                }
            );
        }
        </script>
        
        <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
            <button id="gps-btn" onclick="requestBrowserGPS()" style="
                background-color: #C5A368;
                color: #0A0A0A;
                border: none;
                border-radius: 6px;
                padding: 10px 18px;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                transition: background 0.2s ease;
            " onmouseover="this.style.backgroundColor='#D4B87C'" onmouseout="this.style.backgroundColor='#C5A368'">
                📍 MY LOCATION
            </button>
            <button onclick="requestBrowserGPS()" style="
                background-color: #151515;
                color: #F5F5F5;
                border: 1px solid #2A2A2A;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                cursor: pointer;
            " onmouseover="this.style.borderColor='#C5A368'; this.style.color='#C5A368'" onmouseout="this.style.borderColor='#2A2A2A'; this.style.color='#F5F5F5'">
                🔄 REFRESH LOCATION
            </button>
            <span id="gps-status" style="font-size: 11px; color: #888888; margin-left: 8px;"></span>
        </div>
    </div>
    """
    
    st.components.v1.html(gps_trigger_html, height=48)
    
    # 2. Render Location Status Cards
    status_badge = '<span class="status-pill status-live">🟢 LOCATION DETECTED</span>' if is_live_gps else '<span class="status-pill status-local">📍 MANUAL LOCATION</span>'
    
    loc_col, stn_col = st.columns([1.2, 1.1])
    
    with loc_col:
        st.markdown(f"""
        <div class="telemetry-card" style="border-left: 3px solid {'#10B981' if is_live_gps else '#C5A368'};">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
                <div>
                    <div class="eyebrow-label">DETECTED GPS POSITION</div>
                    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 20px; font-weight: 700; color: #FFFFFF;">
                        📍 {detected_city}, {detected_state}
                    </div>
                </div>
                {status_badge}
            </div>
            <div style="margin-top: 10px; display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; font-size: 11px; color: #888888;">
                <div>• District: <strong style="color: #F5F5F5;">{detected_district or detected_city}</strong></div>
                <div>• Country: <strong style="color: #F5F5F5;">India</strong></div>
                <div>• Latitude: <strong style="color: #C5A368; font-family: monospace;">{detected_lat:.6f}°N</strong></div>
                <div>• Longitude: <strong style="color: #C5A368; font-family: monospace;">{detected_lon:.6f}°E</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with stn_col:
        dist_val = nearest_station.get("distance_km", 0.0)
        stn_name = nearest_station.get("station", f"{detected_city} Monitoring Station")
        stn_city = nearest_station.get("city", detected_city)
        stn_state = nearest_station.get("state", detected_state)
        bearing = nearest_station.get("bearing", "N")
        
        st.markdown(f"""
        <div class="telemetry-card" style="border-left: 3px solid #C5A368;">
            <div class="eyebrow-label">AIR-QUALITY SENSING SOURCE</div>
            <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 17px; font-weight: 700; color: #F5F5F5;">
                🌫️ {stn_name}
            </div>
            <div style="margin-top: 8px; font-size: 11px; color: #888888; line-height: 1.6;">
                <div>• Spatial Separation: <strong style="color: #C5A368; font-family: monospace;">{dist_val} km</strong> ({bearing} heading from your position)</div>
                <div>• Station Location: <strong style="color: #F5F5F5;">{stn_city}, {stn_state}</strong></div>
                <div style="font-size: 10px; color: #666666; margin-top: 2px;">
                    <em>Continuous Ambient Air Quality Monitoring Station (CAAQMS)</em>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_accuracy_warning_banner(distance_km: float, station_name: str):
    """
    Renders standard honesty / accuracy disclaimer as required by Specification 34 & 50.
    """
    st.markdown(f"""
    <div style="background: #111111; border: 1px solid #222222; border-left: 3px solid #C5A368; border-radius: 6px; padding: 10px 16px; margin: 14px 0 18px 0; font-size: 11px; color: #888888; display: flex; align-items: center; justify-content: space-between; gap: 12px;">
        <div>
            <strong style="color: #F5F5F5;">ℹ️ Sensor Accuracy & Proximity Notice:</strong> 
            GPS coordinates identify your physical device position. Air quality telemetry reflects ambient measurements from the certified 
            <strong style="color: #C5A368;">{station_name}</strong> located <strong style="color: #C5A368;">{distance_km} km</strong> away.
        </div>
        <span style="font-size: 9px; text-transform: uppercase; letter-spacing: 0.1em; color: #555555; font-weight: 700; white-space: nowrap;">
            PROXIMITY-GROUNDED ESTIMATE
        </span>
    </div>
    """, unsafe_allow_html=True)

def render_location_aqi_table(
    aq_data: Dict[str, Any],
    weather_data: Dict[str, Any],
    nearest_station: Dict[str, Any],
    user_city: str,
    user_state: str,
    time_metrics: Dict[str, Any],
    season_name: str
):
    """
    Generates dynamic comprehensive Location-Based AQI & Environmental Table (Specification 35 & 46).
    """
    pollutants = aq_data.get("pollutants", {})
    aqi_val = aq_data.get("aqi", 100)
    aqi_cat = aq_data.get("aqi_category", "Moderate")
    risk_level = aq_data.get("risk_level", "Moderate")
    dom_pol = aq_data.get("dominant_pollutant", "PM2.5")
    dist_km = nearest_station.get("distance_km", 0.0)
    stn_name = nearest_station.get("station", f"{user_city} CAAQMS")
    
    # Status helper for parameters
    def get_pol_status(val, threshold_good, threshold_mod):
        if val is None:
            return "N/A"
        if val <= threshold_good:
            return "Normal"
        elif val <= threshold_mod:
            return "Moderate"
        return "Elevated"

    table_data = [
        {"Parameter": "Air Quality Index (AQI)", "Value": f"{aqi_val}", "Unit": "NAQI", "Status": aqi_cat},
        {"Parameter": "AQI Category", "Value": aqi_cat.upper(), "Unit": "CPCB Standard", "Status": "Active Level"},
        {"Parameter": "Assessed Risk Level", "Value": risk_level, "Unit": "EPA/CPCB", "Status": "Risk Profile"},
        {"Parameter": "Dominant Pollutant", "Value": dom_pol, "Unit": "Primary Driver", "Status": "Governing"},
        {"Parameter": "Particulate Matter (PM2.5)", "Value": f"{pollutants.get('pm25', 'N/A')}", "Unit": "µg/m³", "Status": get_pol_status(pollutants.get('pm25', 0), 30, 60)},
        {"Parameter": "Particulate Matter (PM10)", "Value": f"{pollutants.get('pm10', 'N/A')}", "Unit": "µg/m³", "Status": get_pol_status(pollutants.get('pm10', 0), 50, 100)},
        {"Parameter": "Carbon Monoxide (CO)", "Value": f"{pollutants.get('co', 'N/A')}", "Unit": "mg/m³", "Status": get_pol_status(pollutants.get('co', 0), 1.0, 2.0)},
        {"Parameter": "Nitrogen Dioxide (NO2)", "Value": f"{pollutants.get('no2', 'N/A')}", "Unit": "µg/m³", "Status": get_pol_status(pollutants.get('no2', 0), 40, 80)},
        {"Parameter": "Sulphur Dioxide (SO2)", "Value": f"{pollutants.get('so2', 'N/A')}", "Unit": "µg/m³", "Status": get_pol_status(pollutants.get('so2', 0), 40, 80)},
        {"Parameter": "Ozone (O3)", "Value": f"{pollutants.get('o3', 'N/A')}", "Unit": "µg/m³", "Status": get_pol_status(pollutants.get('o3', 0), 50, 100)},
        {"Parameter": "Ambient Temperature", "Value": f"{weather_data.get('temperature', 'N/A')}", "Unit": "°C", "Status": "Current"},
        {"Parameter": "Relative Humidity", "Value": f"{weather_data.get('humidity', 'N/A')}", "Unit": "%", "Status": "Current"},
        {"Parameter": "Wind Velocity", "Value": f"{weather_data.get('wind_speed', 'N/A')}", "Unit": "km/h", "Status": "Dispersion"},
        {"Parameter": "Wind Direction", "Value": f"{weather_data.get('wind_direction', 'N/A')}", "Unit": "° (Azimuth)", "Status": "Current"},
        {"Parameter": "Atmospheric Pressure", "Value": f"{weather_data.get('pressure', 'N/A')}", "Unit": "hPa", "Status": "Current"},
        {"Parameter": "Precipitation", "Value": f"{weather_data.get('rainfall', 0.0)}", "Unit": "mm", "Status": "Current"},
        {"Parameter": "Weather Condition", "Value": weather_data.get('weather_condition', 'N/A'), "Unit": "Meteorology", "Status": "Observed"},
        {"Parameter": "Current Date", "Value": time_metrics.get("date_str", "Today"), "Unit": "Calendar", "Status": time_metrics.get("day_name", "")},
        {"Parameter": "Measurement Time", "Value": f"{aq_data.get('last_updated', time_metrics.get('time_str', ''))}", "Unit": "IST (Asia/Kolkata)", "Status": "Recorded"},
        {"Parameter": "Device Time", "Value": f"{time_metrics.get('time_str', '')} IST", "Unit": "Local Time", "Status": "Synchronized"},
        {"Parameter": "Indian Season", "Value": season_name.upper(), "Unit": "Climatology", "Status": "Seasonal Cycle"},
        {"Parameter": "User Detected Location", "Value": f"{user_city}, {user_state}", "Unit": "Geographic", "Status": "User Position"},
        {"Parameter": "Monitoring Station", "Value": stn_name, "Unit": "Sensor Site", "Status": "Active CAAQMS"},
        {"Parameter": "Distance from User", "Value": f"{dist_km}", "Unit": "km", "Status": "Haversine Distance"}
    ]
    
    df_table = pd.DataFrame(table_data)
    st.dataframe(df_table, hide_index=True, use_container_width=True)
