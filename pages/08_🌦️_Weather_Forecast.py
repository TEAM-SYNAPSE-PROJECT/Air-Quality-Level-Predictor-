import streamlit as st
import pandas as pd
from services.weather_service import get_live_weather
from services.location_service import load_indian_cities
from components.navbar import render_command_header
from components.cards import render_metric_card
from components.charts import render_weather_hourly_chart
from components.page_theme import prepare_page

st.set_page_config(page_title="7-Day Weather Forecast | Air Quality Predictor", page_icon="🌦️", layout="wide")
prepare_page()

cities=load_indian_cities(); city_names=[c["city"] for c in cities]
with st.sidebar:
    st.markdown("### 📍 Weather Location")
    active=st.selectbox("City",city_names,index=city_names.index("Delhi") if "Delhi" in city_names else 0)
    city=next((c for c in cities if c["city"]==active),cities[0])
weather=get_live_weather(city["lat"],city["lon"],city["city"])
render_command_header(city=city["city"],state=city["state"],lat=city["lat"],lon=city["lon"],status=weather["status"])

st.markdown('<div class="page-chip">LIVE METEOROLOGY • 7 DAYS</div>',unsafe_allow_html=True)
st.title("🌦️ 7-Day Weather Forecast")
st.caption("The extended forecast is the first view, followed by today's hourly atmospheric dynamics.")

w1,w2,w3,w4=st.columns(4)
with w1: render_metric_card("Temperature",f"{weather['temperature']} °C",f"Feels like {weather['feels_like']} °C",weather['weather_condition'],"#fbbf24")
with w2: render_metric_card("Humidity",f"{weather['humidity']} %","Relative humidity","MOISTURE","#38bdf8")
with w3: render_metric_card("Wind",f"{weather['wind_speed']} km/h",f"Direction {weather['wind_direction']}°","DISPERSION","#34d399")
with w4: render_metric_card("Pressure",f"{weather['pressure']} hPa","Surface pressure","BAROMETER","#c084fc")

st.markdown("### 📅 7-Day Extended Forecast")
daily=weather.get("daily_forecast",[])
if daily:
    cols=st.columns(7)
    day_colors=["#38bdf8","#f472b6","#a78bfa","#34d399","#fbbf24","#fb7185","#2dd4bf"]
    for i,d in enumerate(daily[:7]):
        with cols[i]:
            st.markdown(f'''<div class="telemetry-card" style="padding:16px 9px;text-align:center;min-height:155px;border-top:3px solid {day_colors[i]}">
            <div style="font-size:11px;color:{day_colors[i]};font-weight:800;letter-spacing:.08em">{d['day_name']}</div>
            <div style="font-size:22px;font-weight:800;color:#fff;margin:12px 0">{d['max_temp']}°</div>
            <div style="font-size:12px;color:#94a3b8">Low {d['min_temp']}°</div>
            <div style="font-size:12px;color:#e2e8f0;margin-top:9px">{d['condition']}</div>
            <div style="font-size:11px;color:#f472b6;margin-top:8px">🌧️ {d['rain_probability']}%</div></div>''',unsafe_allow_html=True)
else: st.warning("The weather provider did not return the 7-day series right now.")

st.markdown("### ⏱️ Today's Hourly Weather Dynamics")
hourly=weather.get("hourly_forecast",[])
if hourly: st.plotly_chart(render_weather_hourly_chart(pd.DataFrame(hourly)),use_container_width=True)
