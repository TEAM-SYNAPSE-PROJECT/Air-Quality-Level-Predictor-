"""
Page 16: About the Platform, Scientific Methodology & Architecture.
"""
import streamlit as st
from components.navbar import render_command_header

st.set_page_config(page_title="About | Air Quality Predictor", page_icon="ℹ️", layout="wide")

with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

render_command_header(city="Documentation", state="Architecture & Standards", status="SYSTEM SPECS")

st.markdown("### ℹ️ ABOUT AIR QUALITY LEVEL PREDICTOR")
st.caption("National Air Quality Intelligence & Environmental Early Warning Platform.")

tab_arch, tab_cpcb, tab_ml, tab_data = st.tabs([
    "🏗️ Platform Architecture",
    "📐 Indian CPCB NAQI Formula",
    "🤖 Machine Learning Pipeline",
    "📡 Data Provenance & Sources"
])

with tab_arch:
    st.markdown("""
    #### 🌐 Comprehensive Full-Stack Architecture
    The **Air Quality Level Predictor** is an industrial-grade environmental monitoring and predictive intelligence system built with modern Python, Streamlit, Scikit-learn, XGBoost, Plotly, and Folium.
    
    ```
    ┌────────────────────────────────────────────────────────────────────────┐
    │                       PRESENTATION & DASHBOARD LAYER                   │
    │  • 16 Modular Specialized Analytics Screens • Plotly Radial Gauges     │
    │  • Interactive Folium / Mapbox Heatmaps    • Contextual AI Chatbot     │
    └───────────────────────────────────┬────────────────────────────────────┘
                                        │
    ┌───────────────────────────────────▼────────────────────────────────────┐
    │                      INTELLIGENCE & SERVICES LAYER                     │
    │  • Real-Time CPCB NAQI Engine             • 7-Scenario Risk Dispatcher │
    │  • Dynamic India Hotspot Monitor          • Multi-Horizon ML Forecaster│
    │  • Automated PDF/CSV Audit Generator      • Resilient API Client       │
    └───────────────────────────────────┬────────────────────────────────────┘
                                        │
    ┌───────────────────────────────────▼────────────────────────────────────┐
    │                  DATA PROCESSING & ML MODEL PIPELINE                   │
    │  • Data Validation & Outlier Scrubbing    • 60+ Engineered Features    │
    │  • Chronological Time-Based Split         • Model Tournament (XGB/RF)  │
    │  • Isolation Forest Anomaly Detection     • Model Registry & Artifacts │
    └────────────────────────────────────────────────────────────────────────┘
    ```
    """)

with tab_cpcb:
    st.markdown("""
    #### 📐 Indian CPCB Piecewise Linear Interpolation Formula
    The National Air Quality Index (NAQI) for any given pollutant sub-index $I_p$ is calculated using the standard CPCB mathematical formula:
    
    $$I_p = \\frac{I_{HI} - I_{LO}}{B_{HI} - B_{LO}} \\times (C_p - B_{LO}) + I_{LO}$$
    
    Where:
    - $C_p$ = Actual observed pollutant concentration
    - $B_{HI}$ = Breakpoint concentration greater than or equal to $C_p$
    - $B_{LO}$ = Breakpoint concentration less than or equal to $C_p$
    - $I_{HI}$ = NAQI value corresponding to $B_{HI}$
    - $I_{LO}$ = NAQI value corresponding to $B_{LO}$
    
    The composite **Overall National AQI** is defined as the maximum of all computed individual sub-indices:
    
    $$\\text{Overall NAQI} = \\max(I_{PM2.5}, I_{PM10}, I_{NO_2}, I_{SO_2}, I_{CO}, I_{O_3})$$
    
    *The pollutant yielding this maximum sub-index is designated as the **Dominant Driving Pollutant**.*
    """)

with tab_ml:
    st.markdown("""
    #### 🤖 Machine Learning Pipeline & Zero-Data-Leakage Protocol
    1. **Chronological Time-Based Partitioning:** Data is partitioned strictly along the time axis (70% Past $\\rightarrow$ Train, 15% Intermediate $\\rightarrow$ Validation, 15% Future $\\rightarrow$ Out-of-time Test) to guarantee zero lookahead bias.
    2. **Autoregressive Lag & Rolling Features:** Generates $t-1, t-2, t-3, t-6, t-12, t-24$ hour lags alongside rolling 3h, 6h, 12h, and 24h moving averages and exponential standard deviations.
    3. **Meteorological Interactions:** Ventilation indices ($v_{\\text{wind}} / \\text{humidity}$) and diurnal solar radiation ratios.
    4. **Model Tournament:** Rigorously evaluates Ridge Linear Regression, Random Forest Regressors, and XGBoost Gradient Boosted trees.
    5. **Unsupervised Anomaly Isolation:** Employs tree-partitioning Isolation Forest to detect atypical atmospheric events.
    """)

with tab_data:
    st.markdown("""
    #### 📡 Atmospheric Data Sources & Real-Time Provenance
    - **Open-Meteo Air Quality & Atmospheric Chemistry API:** High-resolution atmospheric dispersion modeling providing PM2.5, PM10, NO2, SO2, CO, and O3.
    - **Open-Meteo Numerical Weather Prediction:** ECMWF / GFS meteorological surface variables (Temperature, Humidity, Surface Wind, Atmospheric Pressure).
    - **Central Pollution Control Board (CPCB) Guidelines:** Breakpoints, category ranges, health statements, and standard permissible limits.
    - **India Monitoring Grid:** Pre-compiled catalog of 108+ continuous ambient air quality monitoring stations across all Indian States and Union Territories.
    """)
