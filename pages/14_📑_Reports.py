"""
Page 14: Comprehensive Environmental Audit Reports (PDF / CSV Exports).
"""
import streamlit as st
from datetime import datetime
from services.air_quality_service import fetch_live_city_air_quality
from services.weather_service import get_live_weather
from services.location_service import load_indian_cities
from services.report_service import generate_pdf_report, generate_csv_report
from ml.forecasting import generate_multi_horizon_forecast
from ml.early_warning import evaluate_early_warnings
from utils.time_utils import get_live_time_metrics
from utils.season_utils import get_current_season
from components.navbar import render_command_header

st.set_page_config(page_title="Audit Reports | Air Quality Predictor", page_icon="📑", layout="wide")

with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

cities = load_indian_cities()
city_names = [c["city"] for c in cities]

with st.sidebar:
    st.markdown("### 📍 Select Report Target City")
    active_city_name = st.selectbox("City", city_names, index=city_names.index("Delhi") if "Delhi" in city_names else 0)
    city_obj = next((c for c in cities if c["city"] == active_city_name), cities[0])

# Prepare Telemetry
t_metrics = get_live_time_metrics("Asia/Kolkata")
season = get_current_season(t_metrics["datetime"])
aq_data = fetch_live_city_air_quality(city_obj["lat"], city_obj["lon"], city_obj["city"], city_obj["state"])
weather = get_live_weather(city_obj["lat"], city_obj["lon"], city_obj["city"])
forecasts = generate_multi_horizon_forecast(aq_data["pollutants"])
warnings = evaluate_early_warnings(
    current_aqi=aq_data["aqi"],
    current_pm25=aq_data["pollutants"].get("pm25"),
    current_pm10=aq_data["pollutants"].get("pm10"),
    sub_indices=aq_data.get("sub_indices", {})
)

report_payload = {
    "location": {
        "city": city_obj["city"],
        "state": city_obj["state"],
        "latitude": city_obj["lat"],
        "longitude": city_obj["lon"]
    },
    "timestamp_str": f"{t_metrics['date_str']} {t_metrics['time_str']} IST",
    "season": f"{season['name']} ({season['emoji']})",
    "data_status": aq_data["status"],
    "aqi": aq_data["aqi"],
    "category": aq_data["aqi_category"],
    "dominant_pollutant": aq_data["dominant_pollutant"],
    "risk_level": aq_data["risk_level"],
    "pollutants": aq_data["pollutants"],
    "sub_indices": aq_data.get("sub_indices", {}),
    "weather": weather,
    "forecasts": forecasts,
    "warnings": warnings
}

render_command_header(city=city_obj["city"], state=city_obj["state"], lat=city_obj["lat"], lon=city_obj["lon"], status=aq_data["status"])

st.markdown("### 📑 ENVIRONMENTAL INTELLIGENCE AUDIT REPORT GENERATOR")
st.caption("Generate official audit dossiers with strict structural demarcation between Observed Real-Time Telemetry and Machine Learning Projections.")

# Export Buttons
btn_c1, btn_c2, btn_c3 = st.columns([1, 1, 2])

with btn_c1:
    pdf_bytes = generate_pdf_report(report_payload)
    st.download_button(
        label="📄 Download Official PDF Report",
        data=pdf_bytes,
        file_name=f"AQI_Audit_Report_{city_obj['city']}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with btn_c2:
    csv_text = generate_csv_report(report_payload)
    st.download_button(
        label="📊 Download CSV Telemetry Dataset",
        data=csv_text,
        file_name=f"AQI_Telemetry_{city_obj['city']}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.markdown("---")

# Report Live Preview
st.markdown("#### 🔍 Live Audit Document Preview")

with st.expander("📄 View Formatted Document Hierarchy (Observed vs Predicted Separation)", expanded=True):
    st.markdown(f"""
    ### 1. Telemetry Metadata & Provenance
    - **Station / City:** `{city_obj['city']}, {city_obj['state']}`
    - **Geographic Coordinates:** `{city_obj['lat']}° N, {city_obj['lon']}° E`
    - **Audit Generation Timestamp:** `{t_metrics['date_str']} {t_metrics['time_str']} IST`
    - **Current Indian Season:** `{season['name'].upper()}`
    - **Data Pipeline Provenance:** `{aq_data['status']}`
    
    ---
    ### 2. Observed Air Quality Metrics (ACTUAL MEASUREMENTS)
    - **Indian CPCB NAQI:** **{aq_data['aqi']}** ({aq_data['aqi_category'].upper()})
    - **Primary Dominant Factor:** **{aq_data['dominant_pollutant']}**
    - **Fine Particulates (PM2.5):** `{aq_data['pollutants']['pm25']} µg/m³` (Sub-Index: {aq_data.get('sub_indices', {}).get('pm25', 'N/A')})
    - **Coarse Particulates (PM10):** `{aq_data['pollutants']['pm10']} µg/m³` (Sub-Index: {aq_data.get('sub_indices', {}).get('pm10', 'N/A')})
    - **Nitrogen Dioxide (NO2):** `{aq_data['pollutants']['no2']} µg/m³` (Sub-Index: {aq_data.get('sub_indices', {}).get('no2', 'N/A')})
    - **Sulfur Dioxide (SO2):** `{aq_data['pollutants']['so2']} µg/m³` (Sub-Index: {aq_data.get('sub_indices', {}).get('so2', 'N/A')})
    - **Carbon Monoxide (CO):** `{aq_data['pollutants']['co']} mg/m³` (Sub-Index: {aq_data.get('sub_indices', {}).get('co', 'N/A')})
    - **Ground-Level Ozone (O3):** `{aq_data['pollutants']['o3']} µg/m³` (Sub-Index: {aq_data.get('sub_indices', {}).get('o3', 'N/A')})
    
    ---
    ### 3. Meteorological Dispersion Conditions
    - **Surface Ambient Temperature:** `{weather['temperature']} °C` (Feels: `{weather['feels_like']} °C`)
    - **Relative Humidity:** `{weather['humidity']} %`
    - **Surface Wind Speed:** `{weather['wind_speed']} km/h` (Direction: `{weather['wind_direction']}°`)
    - **Atmospheric Pressure:** `{weather['pressure']} hPa`
    
    ---
    ### 4. Machine Learning AQI Forecast (PREDICTED - NOT OBSERVED)
    - **+1 Hour Ahead:** Predicted AQI `{forecasts[0]['predicted_aqi']}` ({forecasts[0]['aqi_category']}) | Risk: {forecasts[0]['risk_level']}
    - **+3 Hours Ahead:** Predicted AQI `{forecasts[1]['predicted_aqi']}` ({forecasts[1]['aqi_category']}) | Risk: {forecasts[1]['risk_level']}
    - **+6 Hours Ahead:** Predicted AQI `{forecasts[2]['predicted_aqi']}` ({forecasts[2]['aqi_category']}) | Risk: {forecasts[2]['risk_level']}
    - **+24 Hours Ahead:** Predicted AQI `{forecasts[4]['predicted_aqi']}` ({forecasts[4]['aqi_category']}) | Risk: {forecasts[4]['risk_level']}
    """)
