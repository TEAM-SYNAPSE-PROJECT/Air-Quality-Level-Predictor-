"""
Page 5: Detailed 6-Pollutant Chemical & Environmental Breakdown.
"""
import streamlit as st
from components.page_theme import prepare_page
import plotly.express as px
from chatbot.knowledge_base import POLLUTANT_KNOWLEDGE
from services.air_quality_service import fetch_live_city_air_quality
from services.location_service import load_indian_cities
from components.navbar import render_command_header
from components.cards import render_metric_card

st.set_page_config(page_title="Pollutant Analysis | Air Quality Predictor", page_icon="🌫️", layout="wide")

prepare_page()


cities = load_indian_cities()
city_names = [c["city"] for c in cities]

# City Selector
with st.sidebar:
    st.markdown("### 📍 Select City for Diagnostics")
    active_city_name = st.selectbox("City", city_names, index=city_names.index("Delhi") if "Delhi" in city_names else 0)
    city_obj = next((c for c in cities if c["city"] == active_city_name), cities[0])

aq_data = fetch_live_city_air_quality(city_obj["lat"], city_obj["lon"], city_obj["city"], city_obj["state"])

render_command_header(city=city_obj["city"], state=city_obj["state"], lat=city_obj["lat"], lon=city_obj["lon"], status=aq_data["status"])

st.markdown("### 🧪 CHEMICAL POLLUTANT SPECIES & AMBIENT STANDARDS")
st.caption("Deep-dive environmental toxicology, aerodynamic particle sizes, sources, and Indian CPCB NAQI threshold standards.")

# Pollutant Tabs
tab_pm25, tab_pm10, tab_no2, tab_so2, tab_co, tab_o3 = st.tabs([
    "🌫️ PM2.5 (Fine Particulate)",
    "🏜️ PM10 (Coarse Dust)",
    "🚗 NO2 (Nitrogen Dioxide)",
    "🏭 SO2 (Sulfur Dioxide)",
    "🔥 CO (Carbon Monoxide)",
    "☀️ O3 (Ground Ozone)"
])

def render_pollutant_tab(p_key: str, tab_container):
    info = POLLUTANT_KNOWLEDGE[p_key]
    val = aq_data["pollutants"].get(p_key, "N/A")
    unit = "mg/m³" if p_key == "co" else "µg/m³"
    sub_idx = aq_data.get("sub_indices", {}).get(p_key, "N/A")
    
    with tab_container:
        col_t1, col_t2 = st.columns([1.2, 1])
        
        with col_t1:
            st.markdown(f"""
            <div class="telemetry-card">
                <div style="font-size: 20px; font-weight: 800; color: #38bdf8;">{info['title']}</div>
                <div style="margin-top: 10px; font-size: 14px; color: #e2e8f0; line-height: 1.6;">
                    <strong>Description & Mechanics:</strong><br/>
                    {info['explanation']}
                </div>
                <hr style="border-color: rgba(75, 85, 99, 0.4); margin: 12px 0;"/>
                <div style="font-size: 13px; color: #cbd5e1; line-height: 1.6;">
                    <strong>🏭 Major Emission Sources:</strong><br/>
                    {info['sources']}<br/><br/>
                    <strong>🫁 Pathological Health Impact:</strong><br/>
                    {info['health_impact']}<br/><br/>
                    <strong>📏 Indian CPCB Permissible Standard:</strong><br/>
                    <span style="color: #38bdf8; font-family: monospace;">{info['cpcb_standard']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_t2:
            render_metric_card(f"Current {p_key.upper()} in {city_obj['city']}", f"{val} {unit}", f"CPCB Sub-Index: {sub_idx}", "Live Sensor", "#06b6d4")
            
            # Comparative scale
            st.markdown("##### 📊 National CPCB Breakpoint Scale")
            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 8px; font-size: 12px; color: #94a3b8;">
                • <strong>Good (0-50):</strong> Clean background air<br/>
                • <strong>Satisfactory (51-100):</strong> Minor respiratory irritation in highly sensitive people<br/>
                • <strong>Moderate (101-200):</strong> Discomfort to people with asthma/lung disease<br/>
                • <strong>Poor (201-300):</strong> Breathing discomfort to most people on prolonged exposure<br/>
                • <strong>Very Poor (301-400):</strong> Respiratory illness on prolonged exposure<br/>
                • <strong>Severe (401-500):</strong> Affects healthy people; seriously impacts those with existing diseases
            </div>
            """, unsafe_allow_html=True)

render_pollutant_tab("pm25", tab_pm25)
render_pollutant_tab("pm10", tab_pm10)
render_pollutant_tab("no2", tab_no2)
render_pollutant_tab("so2", tab_so2)
render_pollutant_tab("co", tab_co)
render_pollutant_tab("o3", tab_o3)
