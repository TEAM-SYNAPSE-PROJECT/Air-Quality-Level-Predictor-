"""
Interactive Circular AQI Gauges & Metric Visualizers.
Uses Plotly to render high-contrast radial indicator gauges according to Indian CPCB standards.
"""
import plotly.graph_objects as go
from utils.helpers import get_aqi_category_info

def render_aqi_gauge(
    aqi_value: float,
    category: str,
    dominant_pollutant: str = "PM2.5",
    risk_level: str = "Moderate",
    city_name: str = "Delhi",
    updated_time: str = ""
) -> go.Figure:
    """
    Renders custom circular AQI gauge with CPCB breakpoint color bands.
    """
    aqi_val = round(aqi_value) if aqi_value is not None else 0
    cat_info = get_aqi_category_info(aqi_val)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=aqi_val,
        number={
            "font": {"size": 52, "color": "#FFFFFF", "family": "Playfair Display, Georgia, serif"},
            "suffix": f"\n<span style='font-size:13px; color:#C5A368; font-family:Plus Jakarta Sans; text-transform:uppercase; letter-spacing:0.15em;'>AQI • {cat_info['category'].upper()}</span>"
        },
        title={
            "text": f"<b style='font-family:Playfair Display, serif; font-size:16px; color:#F5F5F5;'>{city_name.upper()} AIR QUALITY INDEX</b><br><span style='font-size:10px; color:#888888; text-transform:uppercase; letter-spacing:0.12em;'>DRIVER: {dominant_pollutant} &nbsp;|&nbsp; RISK: {risk_level}</span>",
            "font": {"size": 14, "color": "#F5F5F5"}
        },
        gauge={
            "axis": {
                "range": [0, 500],
                "tickwidth": 1,
                "tickcolor": "#2A2A2A",
                "tickvals": [0, 50, 100, 200, 300, 400, 500],
                "ticktext": ["0", "50", "100", "200", "300", "400", "500"],
                "tickfont": {"size": 9, "color": "#666666", "family": "JetBrains Mono"}
            },
            "bar": {"color": "#C5A368", "thickness": 0.22},
            "bgcolor": "#111111",
            "borderwidth": 1,
            "bordercolor": "#222222",
            "steps": [
                {"range": [0, 50], "color": "rgba(16, 185, 129, 0.18)"},
                {"range": [50, 100], "color": "rgba(52, 211, 153, 0.18)"},
                {"range": [100, 200], "color": "rgba(197, 163, 104, 0.22)"},
                {"range": [200, 300], "color": "rgba(234, 179, 8, 0.22)"},
                {"range": [300, 400], "color": "rgba(249, 115, 22, 0.22)"},
                {"range": [400, 500], "color": "rgba(239, 68, 68, 0.25)"}
            ]
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#F5F5F5", "family": "Plus Jakarta Sans"},
        height=290,
        margin=dict(l=25, r=25, t=50, b=20)
    )
    
    return fig
