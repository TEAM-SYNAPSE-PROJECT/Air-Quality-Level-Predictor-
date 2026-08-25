"""
Page 11: Interactive CPCB NAQI Manual Calculator & Sub-Index Simulator.
"""
import streamlit as st
from ml.aqi_calculator import calculate_indian_aqi, calculate_sub_index
from components.navbar import render_command_header
from components.gauges import render_aqi_gauge
from components.cards import render_metric_card

st.set_page_config(page_title="AQI Calculator | Air Quality Predictor", page_icon="🧮", layout="wide")

with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

render_command_header(city="NAQI Calculator", state="CPCB Standard Formula", status="INTERACTIVE")

st.markdown("### 🧮 INDIAN CPCB NAQI MANUAL CALCULATOR")
st.caption("Direct implementation of the Central Pollution Control Board (CPCB) piecewise linear interpolation sub-index algorithm.")

# Input Grid
st.markdown("#### 1. Enter Ambient Pollutant Concentrations")

c1, c2, c3 = st.columns(3)
with c1:
    in_pm25 = st.number_input("PM2.5 Concentration (µg/m³)", min_value=0.0, max_value=800.0, value=85.0, step=1.0)
    in_pm10 = st.number_input("PM10 Concentration (µg/m³)", min_value=0.0, max_value=1200.0, value=145.0, step=1.0)
with c2:
    in_no2 = st.number_input("NO2 Concentration (µg/m³)", min_value=0.0, max_value=500.0, value=45.0, step=1.0)
    in_so2 = st.number_input("SO2 Concentration (µg/m³)", min_value=0.0, max_value=800.0, value=20.0, step=1.0)
with c3:
    in_co = st.number_input("CO Concentration (mg/m³)", min_value=0.0, max_value=50.0, value=1.5, step=0.1)
    in_o3 = st.number_input("O3 Ozone Concentration (µg/m³)", min_value=0.0, max_value=600.0, value=40.0, step=1.0)

# Calculate CPCB AQI
calc_pollutants = {
    "pm25": in_pm25,
    "pm10": in_pm10,
    "no2": in_no2,
    "so2": in_so2,
    "co": in_co,
    "o3": in_o3
}
result = calculate_indian_aqi(calc_pollutants)

st.markdown("---")
st.markdown("#### 2. Calculation Results & Sub-Index Breakdown")

res_left, res_right = st.columns([1.2, 1])

with res_left:
    st.plotly_chart(
        render_aqi_gauge(
            result["aqi"],
            result["category"],
            dominant_pollutant=result["dominant_pollutant"],
            risk_level=result["category"],
            city_name="Calculated NAQI"
        ),
        use_container_width=True
    )

with res_right:
    st.markdown(f"""
    <div class="telemetry-card">
        <div style="font-size: 16px; font-weight: 700; color: #38bdf8;">Calculated CPCB NAQI Summary</div>
        <div style="font-size: 32px; font-weight: 800; color: {result['color']}; margin: 8px 0;">
            {result['aqi']} <span style="font-size: 16px; color: #cbd5e1;">({result['category'].upper()})</span>
        </div>
        <div style="font-size: 13px; color: #e2e8f0; line-height: 1.6;">
            • <strong>Dominant Driving Pollutant:</strong> {result['dominant_pollutant_display']}<br/>
            • <strong>Max Sub-Index:</strong> {result['dominant_subindex']:.1f}<br/>
            • <strong>Health Advisory:</strong> {result['health_statement']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sub-indices table
    st.markdown("##### 📊 Computed Individual Sub-Indices")
    sub_df_data = []
    for p, si in result["sub_indices"].items():
        sub_df_data.append({
            "Pollutant": p.upper(),
            "Input Value": f"{calc_pollutants.get(p)} {'mg/m³' if p=='co' else 'µg/m³'}",
            "CPCB Sub-Index": round(si, 1),
            "Is Dominant": "🌟 Primary Driver" if p == result["dominant_pollutant"].lower() else ""
        })
    st.dataframe(sub_df_data, hide_index=True, use_container_width=True)
