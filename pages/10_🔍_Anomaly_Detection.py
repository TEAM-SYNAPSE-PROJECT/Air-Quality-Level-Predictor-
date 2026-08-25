"""
Page 10: Isolation Forest Atmospheric Anomaly & Spike Detection.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from ml.anomaly_detector import AirQualityAnomalyDetector
from components.navbar import render_command_header
from components.cards import render_metric_card

st.set_page_config(page_title="Anomaly Detection | Air Quality Predictor", page_icon="🔍", layout="wide")

with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

render_command_header(city="Anomaly Diagnostics", state="Machine Learning Pipeline", status="ANOMALY ENGINE")

st.markdown("### 🔍 ISOLATION FOREST ATMOSPHERIC ANOMALY DETECTOR")
st.caption("Unsupervised tree-based outlier isolation isolating extreme chemical spikes, sensor faults, and plume events.")

# Controls
ctrl_c1, ctrl_c2 = st.columns([1, 2])
with ctrl_c1:
    contamination = st.slider("Contamination Factor (Expected Outlier Ratio)", 0.01, 0.10, 0.04, 0.01)

# Run Anomaly Detector
df_raw = pd.read_csv("data/sample_air_quality.csv")
detector = AirQualityAnomalyDetector(contamination=contamination)
detector.fit(df_raw)
df_anomaly, anomaly_records = detector.detect_anomalies(df_raw)

anomalies_found = df_anomaly[df_anomaly["is_anomaly"]]

# Plotly marker size must be numeric, not True/False.
df_anomaly["anomaly_size"] = df_anomaly["is_anomaly"].astype(int).map({0: 6, 1: 10})

# Metric Tiles
m1, m2, m3 = st.columns(3)
with m1:
    render_metric_card("Total Samples Evaluated", f"{len(df_anomaly)}", "Continuous hourly telemetry points", "Dataset", "#38bdf8")
with m2:
    render_metric_card("Anomalies Detected", f"{len(anomalies_found)}", f"Contamination: {contamination*100:.1f}%", "Outliers", "#ef4444")
with m3:
    max_spike = anomalies_found["pm25"].max() if not anomalies_found.empty else 0
    render_metric_card("Max PM2.5 Spike", f"{max_spike:.1f} µg/m³", "Peak extreme outlier concentration", "Maximum", "#f97316")

st.markdown("---")

# Visualizer
st.markdown("#### 📉 Multivariate Anomaly Distribution Scatter")
fig_anom = px.scatter(
    df_anomaly,
    x="timestamp" if "timestamp" in df_anomaly.columns else df_anomaly.index,
    y="pm25",
    color="is_anomaly",
    color_discrete_map={True: "#EF4444", False: "#C5A368"},
    size="anomaly_size",
    size_max=10,
    title="PM2.5 Concentrations with Isolation Forest Anomalies (Red Points)",
    labels={"is_anomaly": "Anomaly Detected", "pm25": "PM2.5 (µg/m³)"}
)
fig_anom.update_layout(
    paper_bgcolor="#0A0A0A",
    plot_bgcolor="#111111",
    font={"color": "#888888", "family": "Plus Jakarta Sans"},
    xaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
    yaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
    height=400
)
st.plotly_chart(fig_anom, use_container_width=True)

# Outlier Log Table
st.markdown("#### 📋 Top Identified Atmospheric Outlier Events")
if not anomalies_found.empty:
    cols_show = ["timestamp", "pm25", "pm10", "no2", "so2", "temperature", "humidity", "wind_speed", "anomaly_score"]
    avail_cols = [c for c in cols_show if c in anomalies_found.columns]
    st.dataframe(anomalies_found[avail_cols].sort_values(by="anomaly_score").head(25), hide_index=True, use_container_width=True)
else:
    st.info("No anomalies detected at the selected contamination threshold.")