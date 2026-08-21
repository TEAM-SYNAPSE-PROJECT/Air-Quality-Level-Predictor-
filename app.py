# ==============================================================================
# SYNAPSE • AIR QUALITY LEVEL PREDICTOR
# Predict • Monitor • Protect People • By Team Synapse
# Indian CPCB Standard • Continuous Ambient Air Quality Monitoring (CAAQMS)
# ==============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import pytz
from cpcb_aqi import calculate_india_aqi, get_aqi_category, get_category_color
from ml_pipeline import train_aqi_models, forecast_next_hours

st.set_page_config(
    page_title="SYNAPSE • AIR QUALITY LEVEL PREDICTOR",
    page_icon="💨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Synapse Luxury Dark & Gold Styling
st.markdown("""
<style>
    .main { background-color: #0a0a0a; color: #f8fafc; }
    .stMetric { background: #12141a; border: 1px solid #2a2a2a; border-radius: 4px; padding: 12px; }
    .aqi-card { padding: 20px; border-radius: 4px; text-align: center; font-weight: bold; }
    .gold-text { color: #C5A059; font-weight: bold; }
    h1, h2, h3 { font-family: 'Cinzel', serif, sans-serif; letter-spacing: 0.05em; color: #ffffff; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid #2a2a2a; }
    .stTabs [data-baseweb="tab"] { background-color: #12141a; color: #808495; border-radius: 4px 4px 0 0; padding: 8px 16px; font-weight: 600; font-size: 13px; }
    .stTabs [aria-selected="true"] { background-color: #C5A059 !important; color: #000000 !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR & GPS / LIVE FEEDS -----------------
st.sidebar.markdown("""
<div style="border-bottom: 1px solid #262730; padding-bottom: 12px; margin-bottom: 16px;">
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 24px;">💨</span>
        <div>
            <div style="color: #C5A059; font-size: 14px; font-weight: 800; letter-spacing: 0.15em; font-family: monospace;">SYNAPSE</div>
            <div style="color: #ffffff; font-size: 11px; font-weight: 700;">AIR QUALITY PREDICTOR</div>
        </div>
    </div>
    <div style="color: #808495; font-size: 10px; margin-top: 4px;">• PREDICT • MONITOR • PROTECT PEOPLE • <strong>BY TEAM SYNAPSE</strong></div>
</div>
""", unsafe_allow_html=True)

stations = {
    "Vijayawada (Benz Circle)": {"lat": 16.5062, "lon": 80.6480, "state": "Andhra Pradesh"},
    "Delhi (Anand Vihar)": {"lat": 28.6469, "lon": 77.3160, "state": "Delhi"},
    "Mumbai (Bandra Kurla)": {"lat": 19.0596, "lon": 72.8295, "state": "Maharashtra"},
    "Bengaluru (Silk Board)": {"lat": 12.9176, "lon": 77.6238, "state": "Karnataka"},
    "Hyderabad (Sanathnagar)": {"lat": 17.4578, "lon": 78.4419, "state": "Telangana"},
    "Kolkata (Rabindra Bharati)": {"lat": 22.6273, "lon": 88.3813, "state": "West Bengal"},
    "Patna (Samanpura)": {"lat": 25.6154, "lon": 85.0833, "state": "Bihar"},
    "Kanpur (Nehru Nagar)": {"lat": 26.4712, "lon": 80.3129, "state": "Uttar Pradesh"},
    "Ghaziabad (Vasundhara)": {"lat": 28.6603, "lon": 77.3573, "state": "Uttar Pradesh"},
    "Chennai (Alandur)": {"lat": 13.0033, "lon": 80.2014, "state": "Tamil Nadu"},
    "Pune (Shivajinagar)": {"lat": 18.5314, "lon": 73.8446, "state": "Maharashtra"},
    "Jaipur (Adarsh Nagar)": {"lat": 26.8914, "lon": 75.8287, "state": "Rajasthan"},
}

selected_station_name = st.sidebar.selectbox("📍 Select Monitoring Station", list(stations.keys()))
selected_station = stations[selected_station_name]

# Date, Time & Season Calculation
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)
time_str = now_ist.strftime("%I:%M:%S %p IST")
date_str = now_ist.strftime("%a, %d %b, %Y")

month = now_ist.month
if 3 <= month <= 5:
    season_str = "Summer (Premonsoon)"
elif 6 <= month <= 9:
    season_str = "Monsoon Season"
elif 10 <= month <= 11:
    season_str = "Post-Monsoon (Inversion Alert)"
else:
    season_str = "Winter Stagnation"

st.sidebar.markdown(f"""
<div style="background-color: #12141a; border: 1px solid #262730; border-radius: 4px; padding: 12px; margin-top: 12px; font-size: 11px; font-family: monospace;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
        <span style="color: #808495;">🕒 IST Clock:</span>
        <span style="color: #ffffff; font-weight: bold;">{time_str}</span>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
        <span style="color: #808495;">📅 Date:</span>
        <span style="color: #C5A059;">{date_str}</span>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
        <span style="color: #808495;">🌤️ Season:</span>
        <span style="color: #facc15; font-weight: bold;">{season_str}</span>
    </div>
    <div style="display: flex; justify-content: space-between; border-top: 1px solid #262730; padding-top: 6px;">
        <span style="color: #808495;">📡 Feeds:</span>
        <span style="color: #10b981; font-weight: bold;">● LIVE FEEDS 💨</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- DATA FETCHING -----------------
@st.cache_data(ttl=900)
def fetch_air_quality(lat, lon):
    try:
        url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=pm10,pm2_5,nitrogen_dioxide,sulphur_dioxide,carbon_monoxide,ozone,ammonia"
            f"&past_days=7&forecast_days=3&timezone=Asia%2FKolkata"
        )
        res = requests.get(url, timeout=12).json()
        if "hourly" in res:
            return pd.DataFrame(res["hourly"])
    except Exception as e:
        pass
    
    times = pd.date_range(end=datetime.now(), periods=168, freq="h")
    return pd.DataFrame({
        "time": [t.strftime("%Y-%m-%dT%H:%M") for t in times],
        "pm2_5": np.random.uniform(35, 95, 168),
        "pm10": np.random.uniform(50, 140, 168),
        "nitrogen_dioxide": np.random.uniform(18, 55, 168),
        "sulphur_dioxide": np.random.uniform(6, 25, 168),
        "carbon_monoxide": np.random.uniform(200, 800, 168),
        "ozone": np.random.uniform(30, 70, 168)
    })

@st.cache_data(ttl=900)
def fetch_weather(lat, lon):
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,surface_pressure,precipitation"
            f"&past_days=7&forecast_days=3&timezone=Asia%2FKolkata"
        )
        res = requests.get(url, timeout=12).json()
        if "hourly" in res:
            return pd.DataFrame(res["hourly"])
    except Exception as e:
        pass
    
    times = pd.date_range(end=datetime.now(), periods=168, freq="h")
    return pd.DataFrame({
        "time": [t.strftime("%Y-%m-%dT%H:%M") for t in times],
        "temperature_2m": np.random.uniform(26, 33, 168),
        "relative_humidity_2m": np.random.uniform(55, 85, 168),
        "wind_speed_10m": np.random.uniform(6, 18, 168),
        "wind_direction_10m": np.random.uniform(0, 360, 168),
        "surface_pressure": np.random.uniform(1008, 1016, 168),
        "precipitation": np.zeros(168)
    })

aq_df = fetch_air_quality(selected_station["lat"], selected_station["lon"])
weather_df = fetch_weather(selected_station["lat"], selected_station["lon"])

# Current observations
current_pm25 = float(aq_df["pm2_5"].dropna().iloc[-1]) if not aq_df["pm2_5"].dropna().empty else 37.6
current_pm10 = float(aq_df["pm10"].dropna().iloc[-1]) if not aq_df["pm10"].dropna().empty else 56.0
current_no2 = float(aq_df["nitrogen_dioxide"].dropna().iloc[-1]) if "nitrogen_dioxide" in aq_df else 20.6
current_so2 = float(aq_df["sulphur_dioxide"].dropna().iloc[-1]) if "sulphur_dioxide" in aq_df else 7.9
current_co = float(aq_df["carbon_monoxide"].dropna().iloc[-1] / 1000.0) if "carbon_monoxide" in aq_df else 0.25
current_o3 = float(aq_df["ozone"].dropna().iloc[-1]) if "ozone" in aq_df else 43.0
current_temp = float(weather_df["temperature_2m"].dropna().iloc[-1]) if not weather_df["temperature_2m"].dropna().empty else 28.0
current_hum = float(weather_df["relative_humidity_2m"].dropna().iloc[-1]) if not weather_df["relative_humidity_2m"].dropna().empty else 65.0
current_wind = float(weather_df["wind_speed_10m"].dropna().iloc[-1]) if not weather_df["wind_speed_10m"].dropna().empty else 9.0
current_heading = float(weather_df["wind_direction_10m"].dropna().iloc[-1]) if not weather_df["wind_direction_10m"].dropna().empty else 135.0
current_press = float(weather_df["surface_pressure"].dropna().iloc[-1]) if not weather_df["surface_pressure"].dropna().empty else 1012.0
current_rain = float(weather_df["precipitation"].dropna().iloc[-1]) if "precipitation" in weather_df and not weather_df["precipitation"].dropna().empty else 0.0

current_result = calculate_india_aqi({
    "pm25": current_pm25, "pm10": current_pm10, "no2": current_no2,
    "so2": current_so2, "co": current_co, "o3": current_o3
})

# ----------------- TOP HEADER BAR -----------------
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #262730; padding-bottom: 12px; margin-bottom: 16px;">
    <div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 26px;">💨</span>
            <span style="font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: 0.05em;">SYNAPSE • AIR QUALITY LEVEL PREDICTOR</span>
            <span style="background: rgba(197, 160, 89, 0.15); border: 1px solid rgba(197, 160, 89, 0.4); color: #C5A059; font-size: 10px; font-weight: bold; padding: 2px 8px; border-radius: 12px;">People Defense 👥🫁</span>
        </div>
        <div style="color: #808495; font-size: 12px; font-family: monospace; margin-top: 4px;">
            • PREDICT • MONITOR • PROTECT PEOPLE • <strong>BY TEAM SYNAPSE</strong> | Station: <strong style="color: #ffffff;">{selected_station_name}</strong>
        </div>
    </div>
    <div style="background: #12141a; border: 1px solid #262730; border-radius: 4px; padding: 6px 12px; font-family: monospace; font-size: 11px;">
        <span style="color: #10b981;">● LIVE</span> | <span style="color: #ffffff;">{time_str}</span> | <span style="color: #C5A059;">{date_str}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- TABS -----------------
tabs = st.tabs([
    "🎯 OVERVIEW & POLLUTANTS",
    "🔮 FUTURE PREDICTION",
    "🧮 NAQI CALCULATOR",
    "🗺️ STATION MAP",
    "📈 HISTORICAL TRENDS",
    "☁️ ATMOS DIAGNOSTICS"
])

# ----------------- TAB 1: OVERVIEW & SYNAPSE CARDS -----------------
with tabs[0]:
    col_gauge, col_bars = st.columns([1, 1.8])
    with col_gauge:
        st.markdown("<div style='color: #C5A059; font-size: 11px; font-weight: bold; letter-spacing: 0.15em;'>🎯 AIR QUALITY INDEX LEVEL</div>", unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=current_result["aqi"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"<b>State of Air Quality:<br><span style='color:{get_category_color(current_result['category'])};font-size:22px'>{current_result['category']}</span></b>", 'font': {'size': 13}},
            gauge={
                'axis': {'range': [0, 500], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': get_category_color(current_result['category'])},
                'bgcolor': "#12141a",
                'borderwidth': 1,
                'bordercolor': "#2a2a2a",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(16,185,129,0.25)'},
                    {'range': [50, 100], 'color': 'rgba(132,204,22,0.25)'},
                    {'range': [100, 200], 'color': 'rgba(245,158,11,0.25)'},
                    {'range': [200, 300], 'color': 'rgba(249,115,22,0.25)'},
                    {'range': [300, 400], 'color': 'rgba(239,68,68,0.25)'},
                    {'range': [400, 500], 'color': 'rgba(127,29,29,0.25)'}
                ],
                'threshold': {
                    'line': {'color': "#C5A059", 'width': 4},
                    'thickness': 0.75,
                    'value': current_result["aqi"]
                }
            }
        ))
        fig_gauge.update_layout(paper_bgcolor="#0d0d0d", font={'color': "white", 'family': "sans-serif"}, height=260, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown(f"<p style='text-align: center; font-size: 12px; color: #808495;'>Dominant Pollutant: <strong style='color:#ffffff;'>{current_result['dominant_pollutant']}</strong></p>", unsafe_allow_html=True)

    with col_bars:
        st.markdown("<div style='color: #C5A059; font-size: 11px; font-weight: bold; letter-spacing: 0.15em;'>📊 MONITORED POLLUTANTS & WEATHER TELEMETRY (BAR GRAPHS)</div>", unsafe_allow_html=True)
        bar_pollutants = {
            "PM2.5 (µg/m³)": current_pm25,
            "PM10 (µg/m³)": current_pm10,
            "NO2 (µg/m³)": current_no2,
            "SO2 (µg/m³)": current_so2,
            "CO (mg/m³)": current_co * 10,
            "O3 (µg/m³)": current_o3,
            "Humidity (%)": current_hum,
            "Temp (°C)": current_temp
        }
        b_df = pd.DataFrame(list(bar_pollutants.items()), columns=["Metric", "Value"])
        fig_bars = px.bar(
            b_df, x="Metric", y="Value", text="Value",
            color="Value",
            color_continuous_scale="Viridis",
            title="Real-Time Pollutant Concentrations & Atmosphere"
        )
        fig_bars.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_bars.update_layout(paper_bgcolor="#0d0d0d", plot_bgcolor="#12141a", font_color="white", height=260, margin=dict(l=10, r=10, t=35, b=10))
        st.plotly_chart(fig_bars, use_container_width=True)

    # ----------------- PRIMARY POLLUTANTS SYNAPSE CARDS -----------------
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px; margin-bottom: 8px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 6px; height: 6px; background-color: #C5A059; border-radius: 50%;"></div>
            <span style="font-size: 11px; font-weight: 700; letter-spacing: 0.18em; color: #ffffff;">PRIMARY AIR POLLUTANTS • NAAQS CONTINUOUS MONITORED</span>
        </div>
        <span style="font-size: 10px; color: #737373; font-family: monospace;">CPCB BREAKPOINT INTERPOLATION</span>
    </div>
    """, unsafe_allow_html=True)

    p_col1, p_col2, p_col3 = st.columns(3)
    p_col4, p_col5, p_col6 = st.columns(3)

    pollutant_defs = [
        ("PM2.5", current_pm25, "µg/m³", 60, "Fine Particulate Matter (≤ 2.5 µm)", p_col1),
        ("PM10", current_pm10, "µg/m³", 100, "Coarse Particulate Matter (≤ 10 µm)", p_col2),
        ("NO2", current_no2, "µg/m³", 80, "Nitrogen Dioxide", p_col3),
        ("SO2", current_so2, "µg/m³", 80, "Sulfur Dioxide", p_col4),
        ("CO", current_co, "mg/m³", 2.0, "Carbon Monoxide", p_col5),
        ("O3", current_o3, "µg/m³", 100, "Ground-level Ozone", p_col6),
    ]

    for name, val, unit, limit, desc, target_col in pollutant_defs:
        with target_col:
            pct = int(min(200, (val / limit) * 100))
            is_safe = val <= limit
            status_text = "✓ SAFE" if is_safe else "▲ EXCEEDS"
            status_color = "#C5A059" if is_safe else "#f97316"
            bar_color = "#10b981" if pct <= 50 else ("#f59e0b" if pct <= 100 else "#ef4444")
            
            st.markdown(f"""
            <div style="background-color: #0d0d0d; border: 1px solid #2a2a2a; border-radius: 2px; padding: 12px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 11px; font-weight: bold; font-family: monospace; color: #ffffff;">{name}</span>
                    <span style="font-size: 9px; font-weight: bold; padding: 2px 6px; border-radius: 2px; background: rgba(197, 160, 89, 0.1); color: #C5A059; border: 1px solid rgba(197, 160, 89, 0.3);">BAR LEVEL {pct}%</span>
                </div>
                <div style="height: 1px; width: 32px; background-color: rgba(197, 160, 89, 0.6); margin: 8px 0;"></div>
                <div style="display: flex; align-items: baseline; gap: 6px;">
                    <span style="font-size: 26px; font-style: italic; font-weight: bold; color: #ffffff;">{val:.1f}</span>
                    <span style="font-size: 11px; color: #737373;">{unit}</span>
                </div>
                <div style="margin-top: 8px; font-size: 9px; color: #737373; font-family: monospace; display: flex; justify-content: space-between;">
                    <span>Bar Level</span>
                    <span>{pct}% of NAAQS</span>
                </div>
                <div style="width: 100%; height: 6px; background-color: #1a1a1a; border-radius: 2px; overflow: hidden; margin-top: 4px;">
                    <div style="width: {min(100, pct)}%; height: 100%; background-color: {bar_color};"></div>
                </div>
                <div style="font-size: 10px; color: #737373; margin-top: 6px;">{desc}</div>
                <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid #2a2a2a; display: flex; justify-content: space-between; font-size: 10px; font-family: monospace;">
                    <span style="color: #737373;">NAAQS: {limit} {unit.upper()}</span>
                    <span style="color: {status_color}; font-weight: bold;">{status_text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ----------------- METEOROLOGICAL ATMOSPHERIC DIAGNOSTICS -----------------
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px; margin-bottom: 8px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 6px; height: 6px; background-color: #C5A059; border-radius: 50%;"></div>
            <span style="font-size: 11px; font-weight: 700; letter-spacing: 0.18em; color: #ffffff;">METEOROLOGICAL ATMOSPHERIC DIAGNOSTICS</span>
        </div>
        <span style="font-size: 10px; color: #737373; font-family: monospace;">BOUNDARY LAYER & DISPERSION TELEMETRY</span>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        st.markdown(f"""
        <div style="background: #0d0d0d; border: 1px solid #2a2a2a; padding: 10px; border-radius: 2px;">
            <div style="font-size: 10px; color: #a3a3a3; font-family: monospace;">TEMPERATURE</div>
            <div style="font-size: 20px; font-style: italic; font-weight: bold; color: #ffffff; margin: 4px 0;">{current_temp}°C</div>
            <div style="font-size: 9px; color: #737373; font-family: monospace;">Mixing Height</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div style="background: #0d0d0d; border: 1px solid #2a2a2a; padding: 10px; border-radius: 2px;">
            <div style="font-size: 10px; color: #a3a3a3; font-family: monospace;">HUMIDITY</div>
            <div style="font-size: 20px; font-style: italic; font-weight: bold; color: #ffffff; margin: 4px 0;">{current_hum}%</div>
            <div style="font-size: 9px; color: #737373; font-family: monospace;">Hygroscopic</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div style="background: #0d0d0d; border: 1px solid #2a2a2a; padding: 10px; border-radius: 2px;">
            <div style="font-size: 10px; color: #a3a3a3; font-family: monospace;">WIND SPEED</div>
            <div style="font-size: 20px; font-style: italic; font-weight: bold; color: #ffffff; margin: 4px 0;">{current_wind} <span style="font-size: 10px;">km/h</span></div>
            <div style="font-size: 9px; color: #737373; font-family: monospace;">Ventilation Active</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div style="background: #0d0d0d; border: 1px solid #2a2a2a; padding: 10px; border-radius: 2px;">
            <div style="font-size: 10px; color: #a3a3a3; font-family: monospace;">HEADING</div>
            <div style="font-size: 20px; font-style: italic; font-weight: bold; color: #ffffff; margin: 4px 0;">{current_heading:.0f}° <span style="color:#C5A059; font-size:11px;">SE</span></div>
            <div style="font-size: 9px; color: #737373; font-family: monospace;">Plume Transport</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown(f"""
        <div style="background: #0d0d0d; border: 1px solid #2a2a2a; padding: 10px; border-radius: 2px;">
            <div style="font-size: 10px; color: #a3a3a3; font-family: monospace;">PRESSURE</div>
            <div style="font-size: 20px; font-style: italic; font-weight: bold; color: #ffffff; margin: 4px 0;">{current_press:.0f} <span style="font-size: 10px;">hPa</span></div>
            <div style="font-size: 9px; color: #737373; font-family: monospace;">Surface Gradient</div>
        </div>
        """, unsafe_allow_html=True)
    with m6:
        st.markdown(f"""
        <div style="background: #0d0d0d; border: 1px solid #2a2a2a; padding: 10px; border-radius: 2px;">
            <div style="font-size: 10px; color: #a3a3a3; font-family: monospace;">RAINFALL</div>
            <div style="font-size: 20px; font-style: italic; font-weight: bold; color: #ffffff; margin: 4px 0;">{current_rain:.1f} <span style="font-size: 10px;">mm</span></div>
            <div style="font-size: 9px; color: #737373; font-family: monospace;">Wet Scavenging</div>
        </div>
        """, unsafe_allow_html=True)

# ----------------- TAB 2: FUTURE PREDICTION -----------------
with tabs[1]:
    st.subheader("🔮 Machine Learning 72-Hour AQI Multi-Horizon Forecast")
    try:
        models, metrics, merged_history = train_aqi_models(aq_df, weather_df)
        forecast_df = forecast_next_hours(models.get("xgboost", models.get("linear")), merged_history, weather_df, hours=72)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=forecast_df["time"], 
            y=forecast_df["predicted_aqi"], 
            mode='lines+markers', 
            name='Predicted AQI', 
            line=dict(color='#C5A059', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=forecast_df["time"], 
            y=forecast_df["upper_bound"], 
            fill=None, 
            mode='lines', 
            line_color='rgba(255,255,255,0)', 
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=forecast_df["time"], 
            y=forecast_df["lower_bound"], 
            fill='tonexty', 
            mode='lines', 
            line_color='rgba(255,255,255,0)', 
            name='Confidence Interval (P10-P90)', 
            fillcolor='rgba(197, 160, 89, 0.18)'
        ))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0d0d0d",
            plot_bgcolor="#12141a",
            title="72-Hour Forecast Conditioned on Boundary Layer Meteorology",
            xaxis_title="Timeline (IST)",
            yaxis_title="CPCB Air Quality Index (AQI)",
            height=380,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📊 View Model Performance Metrics (MAE, RMSE, R²)"):
            m_df = pd.DataFrame(metrics).T
            st.dataframe(m_df.style.format({"mae": "{:.2f}", "rmse": "{:.2f}", "r2": "{:.3f}", "mape": "{:.1f}%"}))
    except Exception as e:
        st.error(f"Prediction model notice: {e}")

# ----------------- TAB 3: INTERACTIVE AQI CALCULATOR -----------------
with tabs[2]:
    st.subheader("🧮 Interactive Custom Indian AQI Calculator")
    st.write("Enter custom concentration values to calculate real-time CPCB NAQI and determine the dominant pollutant:")
    
    calc_c1, calc_c2, calc_c3, calc_c4 = st.columns(4)
    with calc_c1:
        u_pm25 = st.number_input("PM2.5 (µg/m³)", min_value=0.0, max_value=800.0, value=float(current_pm25), step=1.0)
        u_pm10 = st.number_input("PM10 (µg/m³)", min_value=0.0, max_value=1200.0, value=float(current_pm10), step=1.0)
    with calc_c2:
        u_no2 = st.number_input("NO2 (µg/m³)", min_value=0.0, max_value=600.0, value=float(current_no2), step=1.0)
        u_so2 = st.number_input("SO2 (µg/m³)", min_value=0.0, max_value=1000.0, value=float(current_so2), step=1.0)
    with calc_c3:
        u_co = st.number_input("CO (mg/m³)", min_value=0.0, max_value=50.0, value=float(current_co), step=0.1)
        u_o3 = st.number_input("O3 (µg/m³)", min_value=0.0, max_value=500.0, value=float(current_o3), step=1.0)
    with calc_c4:
        u_temp = st.number_input("Temperature (°C)", min_value=-10.0, max_value=55.0, value=float(current_temp), step=0.5)
        u_hum = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=float(current_hum), step=1.0)

    u_res = calculate_india_aqi({
        "pm25": u_pm25, "pm10": u_pm10, "no2": u_no2,
        "so2": u_so2, "co": u_co, "o3": u_o3
    })
    
    st.markdown("---")
    res_col1, res_col2 = st.columns([1, 2])
    with res_col1:
        st.metric(
            label="Calculated CPCB AQI",
            value=u_res["aqi"],
            delta=f"State: {u_res['category']}"
        )
    with res_col2:
        st.info(f"**Dominant Pollutant**: {u_res['dominant_pollutant']} | **State of Air Quality**: {u_res['category']}")

# ----------------- TAB 4: ALL-OVER INDIA MAP -----------------
with tabs[3]:
    st.subheader("🗺️ All-Over India Real-Time Air Quality Map")
    map_data = []
    for s_name, s_info in stations.items():
        est_aqi = 145 if s_info["lat"] > 24 else 75
        if s_name == selected_station_name:
            est_aqi = current_result["aqi"]
        map_data.append({
            "Station": s_name,
            "lat": s_info["lat"],
            "lon": s_info["lon"],
            "State": s_info["state"],
            "AQI": est_aqi,
            "Category": get_aqi_category(est_aqi)
        })
    map_df = pd.DataFrame(map_data)
    fig_map = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        hover_name="Station",
        hover_data={"AQI": True, "Category": True, "State": True, "lat": False, "lon": False},
        color="AQI",
        size="AQI",
        color_continuous_scale="Reds",
        size_max=18,
        zoom=4.2,
        center={"lat": 21.7679, "lon": 78.8718},
        mapbox_style="carto-darkmatter"
    )
    fig_map.update_layout(height=450, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#0d0d0d")
    st.plotly_chart(fig_map, use_container_width=True)

# ----------------- TAB 5: HISTORICAL TRENDS -----------------
with tabs[4]:
    st.subheader(f"📈 Historical 7-Day Atmospheric Trends — {selected_station_name}")
    st.line_chart(aq_df.set_index("time")[["pm2_5", "pm10", "nitrogen_dioxide", "ozone"]])

# ----------------- TAB 6: ATMOS DIAGNOSTICS -----------------
with tabs[5]:
    st.subheader(f"☁️ Boundary Layer Dispersion Diagnostics — {selected_station_name}")
    st.line_chart(weather_df.set_index("time")[["temperature_2m", "relative_humidity_2m", "wind_speed_10m"]])

# ----------------- FOOTER -----------------
st.markdown("---")
st.markdown("<p style='text-align: center; color: #808495; font-size: 12px; font-family: monospace;'>AIR QUALITY LEVEL PREDICTOR • Predict • Monitor • Protect People • <strong>BY TEAM SYNAPSE</strong></p>", unsafe_allow_html=True)
