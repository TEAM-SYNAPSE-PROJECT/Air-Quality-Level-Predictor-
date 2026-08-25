"""
Page 12: Targeted Air Pollution Reduction & Action Frameworks.
"""
import streamlit as st
from services.air_quality_service import fetch_live_city_air_quality
from services.location_service import load_indian_cities
from components.navbar import render_command_header

st.set_page_config(page_title="Reduce Air Pollution | Air Quality Predictor", page_icon="🌱", layout="wide")

with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

cities = load_indian_cities()
city_names = [c["city"] for c in cities]

with st.sidebar:
    st.markdown("### 📍 Select Context City")
    active_city_name = st.selectbox("City", city_names, index=city_names.index("Delhi") if "Delhi" in city_names else 0)
    city_obj = next((c for c in cities if c["city"] == active_city_name), cities[0])

aq_data = fetch_live_city_air_quality(city_obj["lat"], city_obj["lon"], city_obj["city"], city_obj["state"])

render_command_header(city=city_obj["city"], state=city_obj["state"], lat=city_obj["lat"], lon=city_obj["lon"], status=aq_data["status"])

st.markdown("### 🌱 ACTIONABLE AIR POLLUTION MITIGATION STRATEGIES")
st.caption("Science-backed intervention pathways tailored to real-time pollutant profiles and atmospheric conditions.")

# Live Dynamic City Context Banner
dom_pol = aq_data["dominant_pollutant"]
aqi_val = aq_data["aqi"]
aqi_cat = aq_data["aqi_category"]

st.markdown(f"""
<div class="telemetry-card" style="border-left: 4px solid #10b981; margin-bottom: 20px;">
    <div style="font-size: 16px; font-weight: 700; color: #34d399;">
        🎯 Targeted Action Recommendation for {city_obj['city']}
    </div>
    <div style="font-size: 13px; color: #e2e8f0; margin-top: 6px; line-height: 1.6;">
        Current AQI is <strong>{aqi_val} ({aqi_cat.upper()})</strong> with <strong>{dom_pol}</strong> as the primary driver. 
        {'High particulate loading requires immediate road dust water sprinkling and strict enforcement on biomass/waste burning.' if dom_pol in ['PM2.5', 'PM10'] else 'Combustion gas levels necessitate traffic diversion and strict boiler scrubber audits.'}
    </div>
</div>
""", unsafe_allow_html=True)

# 4 Action Tiers
tab_ind, tab_com, tab_indus, tab_gov = st.tabs([
    "👤 Individual & Household Actions",
    "🏘️ Community & Society Actions",
    "🏭 Industrial & Commercial Controls",
    "🏛️ Government & Policy (GRAP / NCAP)"
])

with tab_ind:
    st.markdown("""
    #### 🚶 Individual & Household Mitigation Checklist
    - **Transit Shift:** Replace single-occupant motor trips with metro, electric buses, or non-motorized cycling for short distances (<2 km).
    - **No Idling:** Switch off vehicle engine at red lights exceeding 15 seconds.
    - **Zero Waste Burning:** Never burn garden waste, dry leaves, plastic wrappers, or cardboard; compost organic matter instead.
    - **Clean Cooking Fuels:** Ensure cooking with piped natural gas (PNG) or LPG instead of solid biomass, wood, or cow dung cakes.
    - **Energy Efficiency:** Transition to 5-star BEE rated inverter air conditioners and LED lighting, lowering base thermal power generation demand.
    """)

with tab_com:
    st.markdown("""
    #### 🏘️ Community & Neighborhood Initiatives
    - **Urban Green Belts (Miyawaki Method):** Plant dense native micro-forests with high particulate-absorption foliage (Peepal, Neem, Banyan, Ashoka).
    - **Paved Road Maintenance & Wet Cleaning:** Deploy water misting and mechanical sweeping to prevent resuspension of silt and road dust.
    - **Carpooling & Shift Staggering:** Establish synchronized carpooling networks and stagger office arrival hours to alleviate peak vehicular choke points.
    - **Hyperlocal Air Quality Mesh:** Install community particulate monitoring sensors to detect unauthorized nighttime waste incinerations.
    """)

with tab_indus:
    st.markdown("""
    #### 🏭 Industrial & Commercial Controls
    - **Continuous Emission Monitoring (CEMS):** Enforce real-time telemetry from industrial stacks connected directly to state pollution control boards.
    - **High-Efficiency Particulate Capture:** Install Electrostatic Precipitators (ESPs) and fabric baghouse filters achieving >99.5% particulate collection efficiency.
    - **Flue Gas Desulfurization (FGD):** Deploy wet limestone or dry sorbent FGD scrubbers on all coal-fired boilers to eliminate SO2 emissions.
    - **Low-NOx Burners:** Retrofit industrial furnaces and boilers with staged combustion and Selective Catalytic Reduction (SCR) catalysts.
    """)

with tab_gov:
    st.markdown("""
    #### 🏛️ Statutory Frameworks (CPCB GRAP & NCAP)
    - **National Clean Air Programme (NCAP):** India's targeted framework to reduce PM2.5 and PM10 by 40% across 131 non-attainment cities.
    - **Graded Response Action Plan (GRAP Stages):**
        - *Stage I (Poor - AQI 201-300):* Mechanized sweeping, strict anti-dust measures at construction sites.
        - *Stage II (Very Poor - AQI 301-400):* Ban on diesel generator sets, enhanced parking fees to discourage private vehicles, increase bus/metro frequency.
        - *Stage III (Severe - AQI 401-450):* Strict ban on non-essential construction, demolition, stone crushers, and BS-III Petrol / BS-IV Diesel 4-wheelers.
        - *Stage IV (Severe+ - AQI > 450):* Ban entry of non-essential trucks, transition schools to online mode, 50% work-from-home mandate.
    """)
