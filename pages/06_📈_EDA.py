"""
Page 6: Exploratory Data Analysis & Statistical Environmental Patterns.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from components.navbar import render_command_header
from components.charts import render_correlation_heatmap

st.set_page_config(page_title="EDA & Statistical Analysis | Air Quality Predictor", page_icon="📈", layout="wide")

with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

render_command_header(city="Statistical Analytics", state="Dataset Audit", status="DATA EXPLORER")

st.markdown("### 📈 EXPLORATORY DATA ANALYSIS (EDA)")
st.caption("Statistical distributions, seasonal dispersion variances, diurnal patterns, and cross-pollutant correlations.")

# Load Cleaned Time-Series Dataset
df = pd.read_csv("data/sample_air_quality.csv")
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.day_name()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Pollutant Distributions",
    "🍂 Seasonal & Diurnal Cycles",
    "🌡️ Weather vs Pollution Interactions",
    "🔥 Correlation Matrix"
])

with tab1:
    st.markdown("#### Frequency Distribution of Atmospheric Particulates & Gases")
    p_sel = st.selectbox("Select Target Variable for Histogram & KDE", ["pm25", "pm10", "no2", "so2", "co", "o3"], index=0)
    
    fig_hist = px.histogram(
        df,
        x=p_sel,
        nbins=50,
        marginal="box",
        color_discrete_sequence=["#C5A368"],
        title=f"Empirical Probability Distribution of {p_sel.upper()}"
    )
    fig_hist.update_layout(
        paper_bgcolor="#0A0A0A",
        plot_bgcolor="#111111",
        font={"color": "#888888", "family": "Plus Jakarta Sans"},
        xaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
        yaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
        height=380
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with tab2:
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.markdown("#### 🍂 Seasonal Distribution (Boxplot)")
        fig_season = px.box(
            df,
            x="season",
            y="pm25",
            color="season",
            title="PM2.5 Distribution Across Indian Seasons",
            color_discrete_sequence=["#C5A368", "#D4B87C", "#10B981", "#EF4444"]
        )
        fig_season.update_layout(
            paper_bgcolor="#0A0A0A",
            plot_bgcolor="#111111",
            font={"color": "#888888", "family": "Plus Jakarta Sans"},
            xaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
            yaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
            height=360,
            showlegend=False
        )
        st.plotly_chart(fig_season, use_container_width=True)
        
    with col_c2:
        st.markdown("#### ⏰ 24-Hour Diurnal Cycle (Inversion Peak)")
        hourly_avg = df.groupby("hour")[["pm25", "pm10", "no2"]].mean().reset_index()
        fig_diurnal = px.line(
            hourly_avg,
            x="hour",
            y=["pm25", "pm10", "no2"],
            title="Diurnal Inversion Peak (Morning 8-10 AM & Evening 8-11 PM)",
            markers=True,
            color_discrete_sequence=["#C5A368", "#D4B87C", "#10B981"]
        )
        fig_diurnal.update_layout(
            paper_bgcolor="#0A0A0A",
            plot_bgcolor="#111111",
            font={"color": "#888888", "family": "Plus Jakarta Sans"},
            xaxis=dict(tickmode="linear", tick0=0, dtick=2, gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
            yaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
            height=360,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#888888"))
        )
        st.plotly_chart(fig_diurnal, use_container_width=True)

with tab3:
    col_w1, col_w2 = st.columns(2)
    
    with col_w1:
        st.markdown("#### Wind Speed vs PM2.5 (Ventilation Dispersion)")
        fig_wind = px.scatter(
            df.sample(min(500, len(df))),
            x="wind_speed",
            y="pm25",
            trendline="ols",
            color="temperature",
            color_continuous_scale=[[0, "#1A1A1A"], [0.5, "#2A2A2A"], [1.0, "#C5A368"]],
            title="Dispersion: High Wind Velocity Clears Particulates",
            labels={"wind_speed": "Wind Speed (km/h)", "pm25": "PM2.5 (µg/m³)"}
        )
        fig_wind.update_layout(
            paper_bgcolor="#0A0A0A",
            plot_bgcolor="#111111",
            font={"color": "#888888", "family": "Plus Jakarta Sans"},
            xaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
            yaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
            height=360
        )
        st.plotly_chart(fig_wind, use_container_width=True)
        
    with col_w2:
        st.markdown("#### Temperature vs Ground Ozone (O3 Photochemistry)")
        fig_temp = px.scatter(
            df.sample(min(500, len(df))),
            x="temperature",
            y="o3",
            trendline="ols",
            color="humidity",
            color_continuous_scale=[[0, "#1A1A1A"], [0.5, "#2A2A2A"], [1.0, "#C5A368"]],
            title="Photochemistry: Solar Radiation Drives Ozone Formation",
            labels={"temperature": "Temperature (°C)", "o3": "Ozone (µg/m³)"}
        )
        fig_temp.update_layout(
            paper_bgcolor="#0A0A0A",
            plot_bgcolor="#111111",
            font={"color": "#888888", "family": "Plus Jakarta Sans"},
            xaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
            yaxis=dict(gridcolor="#1A1A1A", zerolinecolor="#2A2A2A"),
            height=360
        )
        st.plotly_chart(fig_temp, use_container_width=True)

with tab4:
    st.plotly_chart(render_correlation_heatmap(df), use_container_width=True)
