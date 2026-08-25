"""
Page 8: Meteorological Forecasting & Atmospheric Dispersion Dynamics.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.weather_service import get_live_weather
from services.location_service import load_indian_cities
from components.navbar import render_command_header
from components.cards import render_metric_card

st.set_page_config(page_title="Weather Forecast | Air Quality Predictor", page_icon="🌦️", layout="wide")

with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

cities = load_indian_cities()
city_names = [c["city"] for c in cities]

with st.sidebar:
    st.markdown("### 📍 Select Weather Station")
    active_city_name = st.selectbox("City", city_names, index=city_names.index("Delhi") if "Delhi" in city_names else 0)
    city_obj = next((c for c in cities if c["city"] == active_city_name), cities[0])

weather = get_live_weather(city_obj["lat"], city_obj["lon"], city_obj["city"])

render_command_header(city=city_obj["city"], state=city_obj["state"], lat=city_obj["lat"], lon=city_obj["lon"], status=weather["status"])

st.markdown("### 🌦️ METEOROLOGICAL CONDITIONS & SYNOPTIC FORECAST")
st.caption("Live atmospheric variables and multi-day meteorological projections from high-resolution global numerical models.")

# Weather Cards Row
w1, w2, w3, w4 = st.columns(4)
with w1:
    render_metric_card("Temperature", f"{weather['temperature']} °C", f"Feels like {weather['feels_like']} °C", weather["weather_condition"], "#f59e0b")
with w2:
    render_metric_card("Relative Humidity", f"{weather['humidity']} %", "Moisture vapor saturation", "Hygrometer", "#38bdf8")
with w3:
    render_metric_card("Wind Velocity", f"{weather['wind_speed']} km/h", f"Heading: {weather['wind_direction']}°", "Anemometer", "#10b981")
with w4:
    render_metric_card("Atmospheric Pressure", f"{weather['pressure']} hPa", "Sea-level corrected", "Barometer", "#a855f7")

st.markdown("---")

# Hourly progression
st.markdown("#### ⏱️ Next 24-Hour Meteorological Trajectory")
if weather.get("hourly_forecast"):
    df_h = pd.DataFrame(weather["hourly_forecast"])
    
    fig_h = go.Figure()
    fig_h.add_trace(go.Scatter(x=df_h["time"], y=df_h["temperature"], mode="lines+markers", name="Temperature (°C)", line=dict(color="#C5A368", width=2.5)))
    fig_h.add_trace(go.Scatter(x=df_h["time"], y=df_h["humidity"], mode="lines+markers", name="Relative Humidity (%)", line=dict(color="#D4B87C", width=2, dash="dot")))
    fig_h.add_trace(go.Bar(x=df_h["time"], y=df_h["rain_probability"], name="Rain Probability (%)", marker_color="rgba(197, 163, 104, 0.25)"))
    
    fig_h.update_layout(
        paper_bgcolor="#0A0A0A",
        plot_bgcolor="#111111",
        font={"color": "#888888", "family": "Plus Jakarta Sans"},
        xaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
        yaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#888888"))
    )
    st.plotly_chart(fig_h, use_container_width=True)

# 7-Day Synoptic Weather
st.markdown("#### 📅 7-Day Extended Weather Outlook")
if weather.get("daily_forecast"):
    day_cols = st.columns(len(weather["daily_forecast"]))
    for idx, d in enumerate(weather["daily_forecast"]):
        with day_cols[idx]:
            st.markdown(f"""
            <div class="telemetry-card" style="padding: 12px 8px; text-align: center;">
                <div style="font-size: 10px; font-weight: 700; color: #C5A368; text-transform: uppercase; letter-spacing: 0.1em;">{d['day_name']}</div>
                <div style="font-size: 16px; font-weight: 700; color: #FFFFFF; margin: 6px 0; font-family: 'JetBrains Mono', monospace;">{d['max_temp']}° / {d['min_temp']}°</div>
                <div style="font-size: 11px; color: #888888;">{d['condition']}</div>
                <div style="font-size: 10px; color: #C5A368; margin-top: 4px;">🌧️ {d['rain_probability']}%</div>
            </div>
            """, unsafe_allow_html=True)
