"""
Page 3: Alert Cities & Critical Hotspot Diagnostics.
"""
import streamlit as st
from components.page_theme import prepare_page
import pandas as pd
from services.air_quality_service import get_india_wide_monitoring_status
from ml.driver_analysis import analyze_pollutant_drivers
from ml.risk_engine import compute_environmental_risk
from components.navbar import render_command_header
from components.cards import render_metric_card
from components.charts import render_driver_breakdown_chart

st.set_page_config(page_title="Alert Cities | Air Quality Predictor", page_icon="🚨", layout="wide")

prepare_page()


status_summary = get_india_wide_monitoring_status()
df_india = status_summary["dataset_df"]

# Filter strictly at-risk cities (AQI > 200)
df_alert = df_india[df_india["aqi"] > 200].sort_values(by="aqi", ascending=False).reset_index(drop=True)
severe_count = len(df_india[df_india["aqi"] > 400])

render_command_header(city="Hotspot Zones", state="National Watchlist", status="ACTIVE HOTSPOTS")

st.markdown("### 🚨 HIGH-RISK AIR QUALITY HOTSPOTS")
st.caption("Real-time automated registry of Indian cities exceeding safety thresholds (AQI > 200: Poor, Very Poor, Severe).")

# Mandatory Top Metrics
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card("Total Cities Monitored", f"{status_summary['total_monitored']}", "Active sensor network", "Coverage", "#38bdf8")
with c2:
    render_metric_card("Cities Currently At Risk", f"{len(df_alert)}", f"{(len(df_alert)/status_summary['total_monitored'])*100:.1f}% of national network", "Priority Action", "#ef4444")
with c3:
    render_metric_card("Severe Category (AQI > 400)", f"{severe_count}", "Public health emergency level", "Critical Alert", "#991b1b")
with c4:
    highest_city = status_summary["highest_aqi_city"]
    render_metric_card("Highest AQI Detected", f"{status_summary['highest_aqi_val']}", f"{highest_city} ({status_summary['highest_aqi_category']})", "Maximum Spike", "#f97316")

st.markdown("---")

# Alert Cities Table
st.markdown("### 📋 Active Air Quality Alert Table")
st.caption("Sort by clicking column headers or use search filter.")

filter_sev = st.radio("Filter by Severity Tier", ["All At-Risk (AQI > 200)", "Severe Only (AQI > 400)", "Very Poor (301 - 400)", "Poor (201 - 300)"], horizontal=True)

df_table_filtered = df_alert.copy()
if filter_sev == "Severe Only (AQI > 400)":
    df_table_filtered = df_table_filtered[df_table_filtered["aqi"] > 400]
elif filter_sev == "Very Poor (301 - 400)":
    df_table_filtered = df_table_filtered[(df_table_filtered["aqi"] > 300) & (df_table_filtered["aqi"] <= 400)]
elif filter_sev == "Poor (201 - 300)":
    df_table_filtered = df_table_filtered[(df_table_filtered["aqi"] > 200) & (df_table_filtered["aqi"] <= 300)]

cols_to_show = ["city", "state", "aqi", "aqi_category", "dominant_pollutant", "pm25", "pm10", "temperature", "humidity", "risk_level", "timestamp"]
rename_map = {
    "city": "City",
    "state": "State",
    "aqi": "NAQI",
    "aqi_category": "Category",
    "dominant_pollutant": "Dominant Pollutant",
    "pm25": "PM2.5 (µg/m³)",
    "pm10": "PM10 (µg/m³)",
    "temperature": "Temp (°C)",
    "humidity": "Hum (%)",
    "risk_level": "Risk Level",
    "timestamp": "Last Synced"
}

st.dataframe(
    df_table_filtered[cols_to_show].rename(columns=rename_map),
    use_container_width=True,
    hide_index=True
)

# Detailed Causality Analysis Drilldown
st.markdown("---")
st.markdown("### 🔍 Drilldown Diagnostic: Why is this City at Risk?")

if not df_alert.empty:
    alert_city_list = df_alert["city"].tolist()
    selected_drilldown = st.selectbox("Select a City to Diagnose Causality & Source Breakdown", alert_city_list)
    
    city_record = df_alert[df_alert["city"] == selected_drilldown].iloc[0]
    
    pollutants = {
        "pm25": float(city_record.get("pm25", 120.0)),
        "pm10": float(city_record.get("pm10", 220.0)),
        "no2": float(city_record.get("no2", 60.0)),
        "so2": float(city_record.get("so2", 25.0)),
        "co": float(city_record.get("co", 2.2)),
        "o3": float(city_record.get("o3", 55.0))
    }
    
    driver_res = analyze_pollutant_drivers(pollutants)
    risk_res = compute_environmental_risk(
        city_record["aqi"],
        pollutants["pm25"],
        city_record["dominant_pollutant"],
        city_record["temperature"],
        city_record["humidity"]
    )
    
    diag_col1, diag_col2 = st.columns([1.2, 1])
    
    with diag_col1:
        st.markdown(f"""
        <div class="telemetry-card" style="border-left: 4px solid #ef4444;">
            <div style="font-size: 18px; font-weight: 800; color: #ffffff;">
                Diagnostic Audit: {selected_drilldown}, {city_record['state']}
            </div>
            <div style="font-size: 13px; color: #f87171; margin: 4px 0;">
                Calculated NAQI: <strong>{city_record['aqi']}</strong> ({city_record['aqi_category'].upper()}) • Primary Driver: <strong>{city_record['dominant_pollutant']}</strong>
            </div>
            <hr style="border-color: rgba(75, 85, 99, 0.4); margin: 8px 0;"/>
            <div style="font-size: 13px; color: #e2e8f0; line-height: 1.6;">
                <strong>Primary Environmental Causes:</strong><br/>
                {'<br/>'.join(['• ' + r for r in driver_res['reasons']])}<br/>
                • <em>Atmospheric Boundary Trapping:</em> High humidity ({city_record['humidity']}%) and low surface wind restrict vertical plume dispersion, trapping emissions near breathing zones.
            </div>
            <div style="margin-top: 12px; font-size: 12px; color: #cbd5e1; background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: 6px;">
                <strong>🛡️ Immediate Health Action:</strong> {risk_res['general_advisory']}<br/>
                <strong>👥 Sensitive Populations:</strong> {risk_res['sensitive_advisory']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with diag_col2:
        st.plotly_chart(render_driver_breakdown_chart(driver_res["drivers"]), use_container_width=True)
else:
    st.success("No cities currently exceed the critical AQI 200 threshold!")
