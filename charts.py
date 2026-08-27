"""Beautiful Plotly charts with deliberately varied palettes per visualization."""
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any, List

DARK_LAYOUT={"paper_bgcolor":"rgba(0,0,0,0)","plot_bgcolor":"rgba(7,12,24,.55)","font":{"color":"#cbd5e1","family":"Plus Jakarta Sans, sans-serif"},"xaxis":{"gridcolor":"rgba(148,163,184,.12)","zerolinecolor":"rgba(148,163,184,.18)"},"yaxis":{"gridcolor":"rgba(148,163,184,.12)","zerolinecolor":"rgba(148,163,184,.18)"},"margin":dict(l=45,r=25,t=60,b=45)}
PALETTES={
 "pollutants":["#22d3ee","#f472b6","#a78bfa","#facc15","#34d399","#fb7185"],
 "forecast":["#60a5fa","#f97316","#c084fc","#2dd4bf","#f43f5e","#eab308"],
 "models":["#38bdf8","#f59e0b","#a78bfa","#34d399","#fb7185"],
 "drivers":["#06b6d4","#ec4899","#8b5cf6","#84cc16","#f97316","#14b8a6"],
 "weather":["#38bdf8","#fbbf24","#f472b6","#34d399","#c084fc"],
 "anomaly":["#e879f9","#22d3ee","#fb7185","#a3e635"],
}

def _layout(fig,title,height=350):
    fig.update_layout(**DARK_LAYOUT,title=dict(text=f"<b>{title}</b>",font=dict(size=15,color="#f8fafc")),height=height,legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=10,color="#cbd5e1")),hoverlabel=dict(bgcolor="#0b1220",font_color="#f8fafc"))
    return fig

def render_pollutant_trends_chart(df,title="Atmospheric Pollutant Trends"):
    fig=go.Figure(); x=df["timestamp"] if "timestamp" in df.columns else df.index
    cols=[("pm25","PM2.5"),("pm10","PM10"),("no2","NO₂"),("o3","O₃")]
    for i,(col,name) in enumerate(cols):
        if col in df.columns: fig.add_trace(go.Scatter(x=x,y=df[col],mode="lines",name=name,line=dict(color=PALETTES["pollutants"][i],width=3),hovertemplate=f"{name}: %{{y:.2f}}<extra></extra>"))
    return _layout(fig,title,360)

def render_driver_breakdown_chart(drivers):
    labels=[d["display_name"] for d in drivers]; values=[d["percentage_contribution"] for d in drivers]
    fig=go.Figure(go.Pie(labels=labels,values=values,hole=.64,marker=dict(colors=PALETTES["drivers"][:len(labels)],line=dict(color="#07101d",width=2)),textinfo="label+percent",textfont=dict(color="#f8fafc",size=10)))
    return _layout(fig,"Pollutant Contribution Breakdown",330).update_layout(showlegend=False)

def render_forecast_horizon_chart(forecasts,current_aqi):
    horizons=["Now"]+[f["label"] for f in forecasts]; vals=[current_aqi]+[f["predicted_aqi"] for f in forecasts]
    fig=go.Figure(go.Bar(x=horizons,y=vals,marker_color=PALETTES["forecast"][:len(vals)],text=[round(v) for v in vals],textposition="outside",textfont=dict(color="#f8fafc"),name="Future AQI"))
    return _layout(fig,"Future AQI Prediction Timeline",410)

def render_model_comparison_chart(models_metrics):
    names=list(models_metrics); fig=go.Figure()
    series=[("RMSE","rmse"),("MAE","mae"),("R² Score %","r2")]
    for i,(name,key) in enumerate(series):
        vals=[models_metrics[m].get(key,0)*(100 if key=="r2" else 1) for m in names]
        fig.add_trace(go.Bar(x=names,y=vals,name=name,marker_color=PALETTES["models"][i]))
    return _layout(fig,"Model Benchmark Comparison",360).update_layout(barmode="group")

def render_weather_hourly_chart(df):
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df["time"],y=df["temperature"],mode="lines+markers",name="Temperature °C",line=dict(color=PALETTES["weather"][0],width=3)))
    fig.add_trace(go.Scatter(x=df["time"],y=df["humidity"],mode="lines+markers",name="Humidity %",line=dict(color=PALETTES["weather"][1],width=2.5,dash="dot")))
    fig.add_trace(go.Bar(x=df["time"],y=df["rain_probability"],name="Rain Probability %",marker_color=PALETTES["weather"][2],opacity=.35))
    return _layout(fig,"Next 24-Hour Weather Dynamics",370)

def render_correlation_heatmap(df, title="Feature Correlation Heatmap"):
    """Render a Plotly correlation heatmap for numeric dataframe columns."""
    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Not enough numeric columns to calculate correlations.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=14, color="#cbd5e1"),
        )
        return _layout(fig, title, 420)

    corr = numeric_df.corr(numeric_only=True)

    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.columns.tolist(),
            zmin=-1,
            zmax=1,
            colorscale="RdBu",
            reversescale=True,
            text=[[f"{v:.2f}" for v in row] for row in corr.values],
            texttemplate="%{text}",
            textfont=dict(size=10),
            hovertemplate="%{x} vs %{y}: %{z:.3f}<extra></extra>",
            colorbar=dict(title="Correlation"),
        )
    )

    return _layout(fig, title, max(420, 34 * len(corr.columns) + 120))

