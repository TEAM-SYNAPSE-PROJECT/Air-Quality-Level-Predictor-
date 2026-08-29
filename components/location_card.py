"""
Interactive Location Module & Dynamic Telemetry Tables.
Provides browser HTML5 Geolocation triggering, manual location selector,
detected location banner, nearest station analysis, and comprehensive parameter tables.
"""
import streamlit as st
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
    # Streamlit 1.51+ Components v2 runs JavaScript in the app page (not an
    # isolated v1 iframe), which allows browser geolocation to work reliably.
    gps_component = st.components.v2.component(
        name="live_browser_gps",
        html="""
        <div class="gps-wrap">
            <button id="gps-btn" type="button">📍 MY LOCATION</button>
            <button id="refresh-gps-btn" type="button">🔄 REFRESH LOCATION</button>
            <span id="gps-status"></span>
        </div>
        """,
        css="""
        .gps-wrap {
            margin: 0;
            padding: 0;
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        button {
            border-radius: 6px;
            padding: 10px 16px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.10em;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        #gps-btn {
            background: #C5A368;
            color: #0A0A0A;
            border: none;
        }
        #gps-btn:hover { background: #D4B87C; }
        #refresh-gps-btn {
            background: #151515;
            color: #F5F5F5;
            border: 1px solid #2A2A2A;
        }
        #refresh-gps-btn:hover {
            border-color: #C5A368;
            color: #C5A368;
        }
        #gps-status {
            font-size: 11px;
            color: #888888;
            margin-left: 8px;
        }
        """,
        js="""
        export default function({ parentElement, setStateValue }) {
            const btn = parentElement.querySelector('#gps-btn');
            const refreshBtn = parentElement.querySelector('#refresh-gps-btn');
            const status = parentElement.querySelector('#gps-status');

            // Keep the browser watch outside the component function so a
            // Streamlit rerun does not accidentally create multiple watches.
            if (!window.__airQualityGPS) {
                window.__airQualityGPS = {
                    watchId: null,
                    lastSent: null
                };
            }
            const gps = window.__airQualityGPS;

            function setStatus(text) {
                if (status) status.textContent = text;
            }

            function locationSuccess(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const accuracy = position.coords.accuracy || 0;
                const now = Date.now();

                // Avoid excessive Streamlit reruns while still tracking live.
                // Send immediately on the first fix, then only after 15 seconds
                // or when the device has moved roughly 25 metres or more.
                let shouldSend = !gps.lastSent;
                if (gps.lastSent) {
                    const dLat = (lat - gps.lastSent.lat) * 111320;
                    const dLon = (lon - gps.lastSent.lon) * 111320 * Math.cos(lat * Math.PI / 180);
                    const movedMeters = Math.sqrt(dLat * dLat + dLon * dLon);
                    shouldSend = movedMeters >= 25 || (now - gps.lastSent.time) >= 15000;
                }

                setStatus('📡 Live GPS active • ' + lat.toFixed(5) + '°, ' + lon.toFixed(5) + '° • ±' + Math.round(accuracy) + 'm');
                if (btn) btn.innerHTML = '🟢 LIVE LOCATION';

                if (shouldSend) {
                    gps.lastSent = { lat: lat, lon: lon, time: now };
                    setStateValue('location', {
                        latitude: lat,
                        longitude: lon,
                        accuracy: accuracy,
                        timestamp: now
                    });
                    setStateValue('error', null);
                }
            }

            function locationError(error) {
                let message = 'Location request failed.';
                if (error.code === 1) {
                    message = 'Permission denied. Allow Location for this site, then click MY LOCATION again.';
                } else if (error.code === 2) {
                    message = 'Position unavailable. Check GPS/Wi-Fi/network signal.';
                } else if (error.code === 3) {
                    message = 'Location request timed out. Please try again.';
                }
                setStatus('⚠️ ' + message);
                if (btn) btn.innerHTML = '📍 MY LOCATION';
                setStateValue('error', { code: error.code, message: message });
            }

            function startGPS() {
                if (!navigator.geolocation) {
                    locationError({ code: 2 });
                    return;
                }

                setStatus('⏳ Requesting device GPS permission...');
                if (btn) btn.innerHTML = '⏳ DETECTING LOCATION...';

                if (gps.watchId !== null) {
                    navigator.geolocation.clearWatch(gps.watchId);
                    gps.watchId = null;
                }

                gps.watchId = navigator.geolocation.watchPosition(
                    locationSuccess,
                    locationError,
                    {
                        enableHighAccuracy: true,
                        timeout: 15000,
                        maximumAge: 5000
                    }
                );
            }

            if (btn) btn.onclick = startGPS;
            if (refreshBtn) refreshBtn.onclick = startGPS;

            if (gps.watchId !== null) {
                setStatus('📡 Live GPS active');
                if (btn) btn.innerHTML = '🟢 LIVE LOCATION';
            }
        }
        """
    )

    gps_result = gps_component(
        default={"location": None, "error": None},
        on_location_change=lambda: None,
        on_error_change=lambda: None,
        key="air_quality_live_gps"
    )

    # Pass the browser GPS result back through the same query-parameter path
    # already used by app.py. No other project file needs to change.
    gps_location = getattr(gps_result, "location", None)
    gps_error = getattr(gps_result, "error", None)

    if isinstance(gps_location, dict):
        try:
            lat = float(gps_location.get("latitude"))
            lon = float(gps_location.get("longitude"))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                current_lat = str(st.query_params.get("user_lat", ""))
                current_lon = str(st.query_params.get("user_lon", ""))
                new_lat = f"{lat:.6f}"
                new_lon = f"{lon:.6f}"
                if current_lat != new_lat or current_lon != new_lon or st.query_params.get("loc_source") != "gps":
                    st.query_params["user_lat"] = new_lat
                    st.query_params["user_lon"] = new_lon
                    st.query_params["loc_source"] = "gps"
                    st.query_params["acc"] = str(round(float(gps_location.get("accuracy", 0))))
                    st.query_params["t"] = str(int(float(gps_location.get("timestamp", 0))))
                    st.query_params.pop("loc_error", None)
                    st.rerun()
        except (TypeError, ValueError):
            pass

    if isinstance(gps_error, dict) and gps_error.get("code"):
        st.query_params["loc_error"] = "denied"

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
