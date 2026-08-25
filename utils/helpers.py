"""Helpers for formatting, styling, and color mapping."""
from typing import Dict, Any, Tuple

# Indian CPCB AQI Category Breakpoints & Colors
AQI_CATEGORIES = [
    {"min": 0, "max": 50, "category": "Good", "color": "#10b981", "bg_color": "rgba(16, 185, 129, 0.15)", "text_color": "#34d399", "risk": "Minimal Risk", "desc": "Air quality is considered satisfactory, and air pollution poses little or no risk."},
    {"min": 51, "max": 100, "category": "Satisfactory", "color": "#84cc16", "bg_color": "rgba(132, 204, 22, 0.15)", "text_color": "#a3e635", "risk": "Minor Risk", "desc": "Minor breathing discomfort to sensitive people."},
    {"min": 101, "max": 200, "category": "Moderate", "color": "#f59e0b", "bg_color": "rgba(245, 158, 11, 0.15)", "text_color": "#fbbf24", "risk": "Moderate Risk", "desc": "Breathing discomfort to the people with lungs, asthma and heart diseases."},
    {"min": 201, "max": 300, "category": "Poor", "color": "#f97316", "bg_color": "rgba(249, 115, 22, 0.15)", "text_color": "#fb923c", "risk": "High Risk", "desc": "Breathing discomfort to most people on prolonged exposure."},
    {"min": 301, "max": 400, "category": "Very Poor", "color": "#ef4444", "bg_color": "rgba(239, 68, 68, 0.15)", "text_color": "#f87171", "risk": "Very High Risk", "desc": "Respiratory illness on prolonged exposure."},
    {"min": 401, "max": 1000, "category": "Severe", "color": "#991b1b", "bg_color": "rgba(153, 27, 27, 0.25)", "text_color": "#fca5a5", "risk": "Critical / Emergency", "desc": "Affects healthy people and seriously impacts those with existing diseases."}
]

def get_aqi_category_info(aqi_val: float) -> Dict[str, Any]:
    """Returns color, risk description, and badge styling for any numerical AQI value."""
    aqi_round = round(aqi_val)
    for item in AQI_CATEGORIES:
        if item["min"] <= aqi_round <= item["max"]:
            return item
    if aqi_round > 500:
        return AQI_CATEGORIES[-1]
    return AQI_CATEGORIES[0]

def get_risk_level_from_aqi(aqi_val: float) -> str:
    """Classifies risk into Low, Moderate, High, Very High, Critical."""
    if aqi_val <= 50:
        return "Low"
    elif aqi_val <= 100:
        return "Low-Moderate"
    elif aqi_val <= 200:
        return "Moderate"
    elif aqi_val <= 300:
        return "High"
    elif aqi_val <= 400:
        return "Very High"
    else:
        return "Critical"

def format_pollutant_display(pollutant_key: str, value: float) -> Tuple[str, str, str]:
    """Returns formatted name, formatted value with unit, and formula."""
    key = pollutant_key.lower().replace(".", "").replace("_", "")
    mapping = {
        "pm25": ("Fine Particulate Matter", f"{value:.1f} µg/m³", "PM₂.₅"),
        "pm10": ("Coarse Particulate Matter", f"{value:.1f} µg/m³", "PM₁₀"),
        "no2": ("Nitrogen Dioxide", f"{value:.1f} µg/m³", "NO₂"),
        "so2": ("Sulfur Dioxide", f"{value:.1f} µg/m³", "SO₂"),
        "co": ("Carbon Monoxide", f"{value:.2f} mg/m³", "CO"),
        "o3": ("Ozone", f"{value:.1f} µg/m³", "O₃")
    }
    return mapping.get(key, (pollutant_key.upper(), f"{value:.1f}", pollutant_key.upper()))
