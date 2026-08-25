"""
Interactive Environmental Analytics & Data Visualizer.
Generates Plotly interactive line charts, comparison plots, heatmaps, and forecasts.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Any, List

DARK_LAYOUT = {
    "paper_bgcolor": "#0A0A0A",
    "plot_bgcolor": "#111111",
    "font": {"color": "#888888", "family": "Plus Jakarta Sans, sans-serif"},
    "xaxis": {"gridcolor": "#1A1A1A", "zerolinecolor": "#2A2A2A"},
    "yaxis": {"gridcolor": "#1A1A1A", "zerolinecolor": "#2A2A2A"},
    "margin": dict(l=40, r=20, t=40, b=40)
}

def render_pollutant_trends_chart(df: pd.DataFrame, title: str = "Atmospheric Pollutant Trends") -> go.Figure:
    """Renders multi-line trend chart for PM2.5, PM10, NO2, O3 over time."""
    fig = go.Figure()
    
    time_col = "timestamp" if "timestamp" in df.columns else df.index
    
    if "pm25" in df.columns:
        fig.add_trace(go.Scatter(x=time_col, y=df["pm25"], mode="lines", name="PM2.5", line=dict(color="#C5A368", width=2.5)))
    if "pm10" in df.columns:
        fig.add_trace(go.Scatter(x=time_col, y=df["pm10"], mode="lines", name="PM10", line=dict(color="#D4B87C", width=1.8, dash="dot")))
    if "no2" in df.columns:
        fig.add_trace(go.Scatter(x=time_col, y=df["no2"], mode="lines", name="NO2", line=dict(color="#10B981", width=1.8)))
    if "o3" in df.columns:
        fig.add_trace(go.Scatter(x=time_col, y=df["o3"], mode="lines", name="Ozone (O3)", line=dict(color="#A3A3A3", width=1.6)))
        
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text=f"<b style='font-family:Playfair Display, serif; color:#F5F5F5;'>{title}</b>", font=dict(size=14)),
        height=340,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#888888"))
    )
    return fig

def render_driver_breakdown_chart(drivers: List[Dict[str, Any]]) -> go.Figure:
    """Renders donut chart showing percentage contribution to current AQI."""
    labels = [d["display_name"] for d in drivers]
    values = [d["percentage_contribution"] for d in drivers]
    colors = ["#C5A368", "#D4B87C", "#A3834C", "#10B981", "#888888", "#555555"]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(colors=colors, line=dict(color="#0A0A0A", width=2)),
        textinfo="label+percent",
        textfont=dict(color="#F5F5F5", size=10, family="Plus Jakarta Sans")
    )])
    
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text="<b style='font-family:Playfair Display, serif; color:#F5F5F5;'>Pollutant Contribution Breakdown (%)</b>", font=dict(size=14)),
        height=320,
        showlegend=False
    )
    return fig

def render_forecast_horizon_chart(forecasts: List[Dict[str, Any]], current_aqi: float) -> go.Figure:
    """Renders forecast bar/line chart showing AQI progression into future hours."""
    horizons = ["Current"] + [f["label"] for f in forecasts]
    aqi_values = [current_aqi] + [f["predicted_aqi"] for f in forecasts]
    colors = ["#C5A368"] + [f.get("color", "#D4B87C") for f in forecasts]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=horizons,
        y=aqi_values,
        marker_color=colors,
        text=[f"{round(v)}" for v in aqi_values],
        textposition="auto",
        textfont=dict(color="#FFFFFF", family="JetBrains Mono", size=11),
        name="Predicted AQI"
    ))
    
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text="<b style='font-family:Playfair Display, serif; color:#F5F5F5;'>Machine Learning Multi-Horizon AQI Forecast</b>", font=dict(size=14)),
        height=320,
        yaxis_title="CPCB Air Quality Index",
        xaxis_title="Forecast Horizon"
    )
    return fig

def render_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """Generates correlation heatmap between pollutants and meteorological factors."""
    numerical_cols = ["pm25", "pm10", "no2", "so2", "co", "o3", "temperature", "humidity", "wind_speed", "pressure"]
    avail_cols = [c for c in numerical_cols if c in df.columns]
    
    corr = df[avail_cols].corr()
    
    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale=[[0, "#0A0A0A"], [0.5, "#2A2A2A"], [1.0, "#C5A368"]],
        aspect="auto",
        labels=dict(color="Correlation")
    )
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text="<b style='font-family:Playfair Display, serif; color:#F5F5F5;'>Cross-Feature Environmental Correlation Matrix</b>", font=dict(size=14)),
        height=420
    )
    return fig

def render_model_comparison_chart(models_metrics: Dict[str, Dict[str, Any]]) -> go.Figure:
    """Renders multi-metric comparison between ML models."""
    names = list(models_metrics.keys())
    rmse_vals = [models_metrics[m]["rmse"] for m in names]
    mae_vals = [models_metrics[m]["mae"] for m in names]
    r2_vals = [models_metrics[m]["r2"] * 100 for m in names] # scaled for visibility
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=names, y=rmse_vals, name="RMSE (Lower is Better)", marker_color="#EF4444"))
    fig.add_trace(go.Bar(x=names, y=mae_vals, name="MAE (Lower is Better)", marker_color="#C5A368"))
    fig.add_trace(go.Bar(x=names, y=r2_vals, name="R² Score % (Higher is Better)", marker_color="#10B981"))
    
    fig.update_layout(
        **DARK_LAYOUT,
        barmode="group",
        title=dict(text="<b style='font-family:Playfair Display, serif; color:#F5F5F5;'>Machine Learning Model Benchmark Evaluation</b>", font=dict(size=14)),
        height=340,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#888888"))
    )
    return fig
