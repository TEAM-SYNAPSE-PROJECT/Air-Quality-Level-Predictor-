"""
Deep Learning AQI Forecast page.

This page is intentionally separate from the existing ML prediction page.
Train the model once with:
    python -m dl.train_lstm

The UI automatically uses the saved LSTM artifacts when available.
"""

import json
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from components.page_theme import prepare_page

from dl.lstm_model import AirQualityLSTM, LSTMArtifacts


st.set_page_config(
    page_title="Deep Learning Forecast | Air Quality Predictor",
    page_icon="🧠",
    layout="wide",
)

prepare_page()


DATA_PATH = "data/processed/cleaned_air_quality.csv"
ARTIFACT_DIR = "models/deep_learning"

artifacts = LSTMArtifacts(
    model_path=f"{ARTIFACT_DIR}/aqi_lstm.keras",
    feature_scaler_path=f"{ARTIFACT_DIR}/feature_scaler.pkl",
    target_scaler_path=f"{ARTIFACT_DIR}/target_scaler.pkl",
    metadata_path=f"{ARTIFACT_DIR}/metadata.json",
)

st.markdown("## 🧠 Deep Learning AQI Forecast")
st.caption(
    "LSTM time-series forecasting using the previous 24 hourly observations "
    "to estimate future PM2.5."
)

if not os.path.exists(artifacts.model_path):
    st.warning(
        "The LSTM model has not been trained yet. From the project root run: "
        "`python -m dl.train_lstm`"
    )
    st.stop()

if not os.path.exists(DATA_PATH):
    st.error(f"Dataset not found: {DATA_PATH}")
    st.stop()

try:
    df = pd.read_csv(DATA_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    model = AirQualityLSTM(lookback=24)
    model.load(artifacts)

    with open(artifacts.metadata_path, encoding="utf-8") as f:
        metadata = json.load(f)

    horizon = st.slider("Forecast horizon (hours)", 1, 24, 12)
    forecast = model.forecast(df.tail(72), horizon=horizon)
    forecast_df = pd.DataFrame(forecast)

    current_pm25 = float(df["pm25"].iloc[-1])
    last_time = df["timestamp"].iloc[-1]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current PM2.5", f"{current_pm25:.1f} µg/m³")
    c2.metric("Forecast +1h", f"{forecast_df.iloc[0]['predicted_pm25']:.1f} µg/m³")
    c3.metric(
        f"Forecast +{horizon}h",
        f"{forecast_df.iloc[-1]['predicted_pm25']:.1f} µg/m³",
    )
    c4.metric("Lookback", "24 hours")

    fig = go.Figure()
    history = df.tail(48)
    fig.add_trace(go.Scatter(
        x=history["timestamp"],
        y=history["pm25"],
        mode="lines",
        name="Historical PM2.5",
    ))
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(forecast_df["forecast_time"]),
        y=forecast_df["predicted_pm25"],
        mode="lines+markers",
        name="LSTM Forecast",
    ))
    fig.update_layout(
        title="PM2.5: Historical + Deep Learning Forecast",
        xaxis_title="Time",
        yaxis_title="PM2.5 (µg/m³)",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 LSTM Forecast")
    st.dataframe(
        forecast_df.rename(columns={
            "step": "Step",
            "forecast_time": "Forecast Time",
            "predicted_pm25": "Predicted PM2.5 (µg/m³)",
        }),
        hide_index=True,
        use_container_width=True,
    )

    st.markdown("### 📊 Held-Out Test Performance")
    metrics = metadata.get("metrics", {})
    m1, m2, m3 = st.columns(3)
    m1.metric("RMSE", f"{metrics.get('rmse', 0):.2f}")
    m2.metric("MAE", f"{metrics.get('mae', 0):.2f}")
    m3.metric("R²", f"{metrics.get('r2', 0):.3f}")

    st.info(
        "This is a genuine LSTM forecast trained with chronological data. "
        "The displayed metrics come from the held-out test split and should "
        "not be presented as a guaranteed future accuracy."
    )

except Exception as exc:
    st.error(f"Deep Learning module error: {exc}")
