"""
Page 10: Isolation Forest Atmospheric Anomaly & Spike Detection.
"""
import streamlit as st
from components.page_theme import prepare_page
import pandas as pd
import plotly.graph_objects as go
from ml.anomaly_detector import AirQualityAnomalyDetector
from components.navbar import render_command_header
from components.cards import render_metric_card

st.set_page_config(page_title="Anomaly Detection | Air Quality Predictor", page_icon="🔍", layout="wide")

prepare_page()


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
st.markdown("#### 📈 Atmospheric Anomaly Timeline")
fig_anom=go.Figure()
normal=df_anomaly[~df_anomaly["is_anomaly"]]
outliers=df_anomaly[df_anomaly["is_anomaly"]]
xcol="timestamp" if "timestamp" in df_anomaly.columns else df_anomaly.index
fig_anom.add_trace(go.Scatter(x=normal[xcol],y=normal["pm25"],mode="lines",name="Normal telemetry",line=dict(color="#38bdf8",width=2)))
fig_anom.add_trace(go.Scatter(x=outliers[xcol],y=outliers["pm25"],mode="markers",name="Detected anomaly",marker=dict(color="#f43f5e",size=11,line=dict(color="#fff",width=1))))
fig_anom.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(7,12,24,.55)",font={"color":"#cbd5e1","family":"Plus Jakarta Sans"},xaxis=dict(gridcolor="rgba(148,163,184,.12)"),yaxis=dict(gridcolor="rgba(148,163,184,.12)"),height=420,hoverlabel=dict(bgcolor="#0b1220"),legend=dict(orientation="h",y=1.02,yanchor="bottom"),title="PM2.5 telemetry with Isolation Forest outliers")
st.plotly_chart(fig_anom,use_container_width=True)

# Outlier Log Table
st.markdown("#### 📋 Top Identified Atmospheric Outlier Events")
if not anomalies_found.empty:
    cols_show = ["timestamp", "pm25", "pm10", "no2", "so2", "temperature", "humidity", "wind_speed", "anomaly_score"]
    avail_cols = [c for c in cols_show if c in anomalies_found.columns]
    st.dataframe(anomalies_found[avail_cols].sort_values(by="anomaly_score").head(25), hide_index=True, use_container_width=True)
else:
    st.info("No anomalies detected at the selected contamination threshold.")