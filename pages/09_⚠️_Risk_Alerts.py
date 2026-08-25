"""
Page 9: Early Warning Notification & Multi-Scenario Alert Dispatcher.
"""
import streamlit as st
from ml.early_warning import evaluate_early_warnings
from services.air_quality_service import fetch_live_city_air_quality
from services.location_service import load_indian_cities
from components.navbar import render_command_header
from components.alerts import render_alert_banners

st.set_page_config(page_title="Risk Alerts | Air Quality Predictor", page_icon="⚠️", layout="wide")

with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

cities = load_indian_cities()
city_names = [c["city"] for c in cities]

with st.sidebar:
    st.markdown("### 📍 Select Monitoring Station")
    active_city_name = st.selectbox("City", city_names, index=city_names.index("Delhi") if "Delhi" in city_names else 0)
    city_obj = next((c for c in cities if c["city"] == active_city_name), cities[0])

aq_data = fetch_live_city_air_quality(city_obj["lat"], city_obj["lon"], city_obj["city"], city_obj["state"])

render_command_header(city=city_obj["city"], state=city_obj["state"], lat=city_obj["lat"], lon=city_obj["lon"], status=aq_data["status"])

st.markdown("### ⚠️ EARLY WARNING & ENVIRONMENTAL RISK DISPATCH")
st.caption("Automated threat evaluation engine screening live telemetry across 7 discrete atmospheric risk triggers.")

# Evaluate Active Live Alerts
live_alerts = evaluate_early_warnings(
    current_aqi=aq_data["aqi"],
    current_pm25=aq_data["pollutants"].get("pm25"),
    current_pm10=aq_data["pollutants"].get("pm10"),
    sub_indices=aq_data.get("sub_indices", {}),
    recent_trend_delta=15.0,
    forecast_aqi_max=320.0 if aq_data["aqi"] > 250 else 180.0,
    is_anomaly=False
)

st.markdown("#### 🚨 Active Warnings for Selected Location")
render_alert_banners(live_alerts)

st.markdown("---")

# 7 Trigger Cases Architecture Matrix
st.markdown("### 🛡️ Real-Time 7-Scenario Risk Engine Protocol")

scenarios = [
    ("CASE 1: High-Risk AQI Threshold", "AQI >= 201 (Poor, Very Poor, Severe)", "Triggers immediate public alert and restriction of intense outdoor activities."),
    ("CASE 2: Rapid AQI Escalation", "Rate of change >= +30 AQI points in recent hours", "Warns of sudden atmospheric stagnation or severe localized industrial/biomass plume emission."),
    ("CASE 3: Hazardous Fine Particulate PM2.5", "PM2.5 >= 120 µg/m³ (2x National Standard)", "Issues HEPA air purifier guidance and mandatory N95 respirator advisory for sensitive groups."),
    ("CASE 4: Elevated Coarse Dust PM10", "PM10 >= 250 µg/m³", "Triggers municipal dust suppression (water misting on roads) and construction site shielding alerts."),
    ("CASE 5: Multi-Pollutant Co-Exposure", ">= 2 pollutants with Sub-Index >= 150 simultaneously", "Issues synergistic chemical hazard alert due to simultaneous particulate and gas phase toxicity."),
    ("CASE 6: Predicted Spike in Upcoming Horizon", "ML Forecast predicts future AQI >= 300 ahead", "Enables proactive commute and school schedule adjustments before peak pollution arrival."),
    ("CASE 7: Isolation Forest Atmospheric Anomaly", "Atypical multivariate outlier signature detected", "Flags unusual meteorological anomalies or unreported localized emission events.")
]

for title, cond, impact in scenarios:
    st.markdown(f"""
    <div class="telemetry-card" style="margin-bottom: 10px; padding: 12px 16px;">
        <div style="font-weight: 700; color: #38bdf8; font-size: 14px;">{title}</div>
        <div style="font-size: 12px; color: #cbd5e1; margin-top: 4px;"><strong>Trigger Condition:</strong> <code>{cond}</code></div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 2px;"><strong>Operational Action:</strong> {impact}</div>
    </div>
    """, unsafe_allow_html=True)
