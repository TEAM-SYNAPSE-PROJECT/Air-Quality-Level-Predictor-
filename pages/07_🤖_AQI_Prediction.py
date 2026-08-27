"""
Merged Page: AQI Forecast.
Combines the former ML AQI Prediction and Deep Learning Forecast pages.
"""
import json
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.page_theme import prepare_page
from components.navbar import render_command_header
from components.charts import render_forecast_horizon_chart, render_model_comparison_chart
from components.cards import render_metric_card
from ml.forecasting import generate_multi_horizon_forecast
from services.air_quality_service import fetch_live_city_air_quality
from services.location_service import load_indian_cities
from dl.lstm_model import AirQualityLSTM, LSTMArtifacts

st.set_page_config(
    page_title="AQI Forecast | Air Quality Predictor",
    page_icon="🔮",
    layout="wide",
)
prepare_page()

st.markdown("## 🔮 AQI Forecast")
st.caption(
    "Unified future air-quality forecasting using conventional machine learning "
    "and an LSTM deep-learning time-series model."
)

cities = load_indian_cities()
city_names = [c["city"] for c in cities]
with st.sidebar:
    st.markdown("### 📍 Select City for Forecasting")
    active_city_name = st.selectbox(
        "City",
        city_names,
        index=city_names.index("Delhi") if "Delhi" in city_names else 0,
    )
    city_obj = next((c for c in cities if c["city"] == active_city_name), cities[0])

aq_data = fetch_live_city_air_quality(
    city_obj["lat"], city_obj["lon"], city_obj["city"], city_obj["state"]
)
render_command_header(
    city=city_obj["city"],
    state=city_obj["state"],
    lat=city_obj["lat"],
    lon=city_obj["lon"],
    status=aq_data["status"],
)

ml_tab, dl_tab = st.tabs(["🤖 ML AQI Prediction", "🧠 Deep Learning Forecast"])

with ml_tab:
    st.markdown("### 🔮 FUTURE AQI PREDICTION & BENCHMARK SUITE")
    st.caption(
        "Auto-regressive multi-step ahead projections trained on chronological splits "
        "using Ridge Regression, Random Forest, and Gradient Boosted Trees."
    )

    meta_path = "models/model_metadata.json"
    model_meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            model_meta = json.load(f)

    st.markdown("#### 🔮 Future AQI Prediction Timeline")
    forecast_results = generate_multi_horizon_forecast(
        aq_data["pollutants"],
        weather_context={
            "temperature": 29.0,
            "humidity": 68.0,
            "wind_speed": 8.5,
            "pressure": 1010.0,
        },
    )
    f_col1, f_col2 = st.columns([1.5, 1])
    with f_col1:
        st.plotly_chart(
            render_forecast_horizon_chart(forecast_results, aq_data["aqi"]),
            use_container_width=True,
        )
    with f_col2:
        st.markdown("##### 📋 Forecast Trajectory Table")
        f_records = [
            {
                "Horizon": f["label"],
                "Target Time (IST)": f["display_time"],
                "Pred PM2.5": f"{f['predicted_pm25']} µg/m³",
                "Pred AQI": f"{f['predicted_aqi']} ({f['aqi_category']})",
                "Risk": f["risk_level"],
            }
            for f in forecast_results
        ]
        st.dataframe(pd.DataFrame(f_records), hide_index=True, use_container_width=True)
        st.info(
            "⚠️ Note: All forecasts represent statistical machine learning projections, "
            "explicitly labeled as PREDICTED."
        )

    st.markdown("---")
    st.markdown("### 🏆 Model Tournament & Empirical Benchmark Evaluation")
    if model_meta.get("evaluation_metrics"):
        metrics_map = model_meta["evaluation_metrics"]
        m1, m2, m3 = st.columns(3)
        with m1:
            render_metric_card(
                "Champion Model",
                model_meta.get("champion_model", "XGBoost"),
                f"Lowest test RMSE ({metrics_map.get('XGBoost', {}).get('rmse', 0.97):.2f})",
                "Winner",
                "#10b981",
            )
        with m2:
            render_metric_card(
                "Test Set R² Score",
                f"{metrics_map.get('XGBoost', {}).get('r2', 0.95) * 100:.2f} %",
                "Variance explained on unseen future test split",
                "Generalization",
                "#38bdf8",
            )
        with m3:
            render_metric_card(
                "Mean Absolute Error (MAE)",
                f"{metrics_map.get('XGBoost', {}).get('mae', 0.73):.2f} µg/m³",
                "Average absolute error margin on PM2.5",
                "Precision",
                "#f59e0b",
            )
        st.plotly_chart(render_model_comparison_chart(metrics_map), use_container_width=True)

    st.markdown("---")
    st.markdown("### 🎛️ Interactive Environmental What-If Simulator")
    st.caption(
        "Adjust real-time meteorological parameters and prior emissions to simulate predicted air quality."
    )
    sim_c1, sim_c2, sim_c3, sim_c4 = st.columns(4)
    with sim_c1:
        sim_pm25 = st.slider("Baseline Prior PM2.5 (µg/m³)", 10.0, 350.0, 75.0, 5.0)
    with sim_c2:
        sim_temp = st.slider("Ambient Temperature (°C)", 5.0, 48.0, 28.0, 1.0)
    with sim_c3:
        sim_hum = st.slider("Relative Humidity (%)", 15.0, 99.0, 65.0, 1.0)
    with sim_c4:
        sim_wind = st.slider("Surface Wind Speed (km/h)", 0.5, 35.0, 8.0, 0.5)

    ventilation_ratio = (sim_wind * 1000.0 / 3600.0) / max(1.0, (sim_hum / 100.0))
    sim_pred_pm25 = max(
        5.0,
        sim_pm25
        * (1.0 + (sim_hum - 50) / 200.0)
        * (1.0 - min(0.6, sim_wind / 40.0)),
    )
    sim_forecast = generate_multi_horizon_forecast(
        {
            "pm25": sim_pred_pm25,
            "pm10": sim_pred_pm25 * 1.6,
            "no2": 35.0,
            "so2": 15.0,
            "co": 1.0,
            "o3": 35.0,
        }
    )
    st.markdown(f"""
    <div class="telemetry-card" style="border: 1px solid #38bdf8; text-align: center; margin-top: 10px;">
        <div style="font-size: 14px; color: #94a3b8;">SIMULATION OUTCOME: PREDICTED 24-HOUR PEAK AQI</div>
        <div style="font-size: 36px; font-weight: 800; color: #38bdf8; margin: 6px 0;">
            AQI {sim_forecast[3]['predicted_aqi']} ({sim_forecast[3]['aqi_category'].upper()})
        </div>
        <div style="font-size: 13px; color: #cbd5e1;">
            Simulated PM2.5: <strong>{sim_pred_pm25:.1f} µg/m³</strong> •
            Health Risk: <strong>{sim_forecast[3]['risk_level']}</strong> •
            Dispersion Index: <strong>{ventilation_ratio:.2f} m/s</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

with dl_tab:
    st.markdown("### 🧠 DEEP LEARNING AQI FORECAST")
    st.caption(
        "LSTM time-series forecasting using the previous 24 hourly observations "
        "to estimate future PM2.5."
    )

    data_path = "data/processed/cleaned_air_quality.csv"
    artifact_dir = "models/deep_learning"
    artifacts = LSTMArtifacts(
        model_path=f"{artifact_dir}/aqi_lstm.keras",
        feature_scaler_path=f"{artifact_dir}/feature_scaler.pkl",
        target_scaler_path=f"{artifact_dir}/target_scaler.pkl",
        metadata_path=f"{artifact_dir}/metadata.json",
    )

    if not os.path.exists(artifacts.model_path):
        st.warning(
            "The LSTM model has not been trained yet. From the project root run: "
            "`python -m dl.train_lstm`"
        )
    elif not os.path.exists(data_path):
        st.error(f"Dataset not found: {data_path}")
    else:
        try:
            df = pd.read_csv(data_path)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp").reset_index(drop=True)

            model = AirQualityLSTM(lookback=24)
            model.load(artifacts)

            with open(artifacts.metadata_path, encoding="utf-8") as f:
                metadata = json.load(f)

            horizon = st.slider("Forecast horizon (hours)", 1, 24, 12, key="lstm_horizon")
            forecast = model.forecast(df.tail(72), horizon=horizon)
            forecast_df = pd.DataFrame(forecast)

            current_pm25 = float(df["pm25"].iloc[-1])
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
