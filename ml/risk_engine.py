"""
Environmental Risk Engine.
Assesses multi-tier health risks, vulnerable population impacts,
and outdoor activity safety thresholds.
"""
from typing import Dict, Any, List

def compute_environmental_risk(
    aqi: float,
    pm25: float = None,
    dominant_pollutant: str = "PM2.5",
    temperature: float = None,
    humidity: float = None
) -> Dict[str, Any]:
    """
    Evaluates health risk index, activity recommendations, and vulnerable group advisories.
    """
    aqi_val = round(aqi) if aqi is not None else 0
    
    if aqi_val <= 50:
        level = "Low"
        badge_color = "#10b981"
        summary = "Air quality is ideal for all outdoor activities."
        general_advisory = "Enjoy outdoor activities. Air pollution poses little to no health risk."
        sensitive_advisory = "No special precautions needed."
        mask_recommended = False
        outdoor_exercise = "Fully Recommended"
    elif aqi_val <= 100:
        level = "Moderate-Low"
        badge_color = "#84cc16"
        summary = "Air quality is acceptable for the vast majority of citizens."
        general_advisory = "Outdoor activities are generally safe."
        sensitive_advisory = "Unusually sensitive individuals with pre-existing respiratory conditions should observe symptoms."
        mask_recommended = False
        outdoor_exercise = "Recommended"
    elif aqi_val <= 200:
        level = "Moderate"
        badge_color = "#f59e0b"
        summary = "Air quality may cause breathing discomfort to sensitive individuals."
        general_advisory = "Healthy individuals can continue normal outdoor activities, but reduce prolonged strenuous exertion."
        sensitive_advisory = "People with asthma, COPD, elderly, and children should limit heavy outdoor exertion."
        mask_recommended = False
        outdoor_exercise = "Acceptable with moderation"
    elif aqi_val <= 300:
        level = "High"
        badge_color = "#f97316"
        summary = "Air quality is unhealthy; prolonged outdoor exposure causes discomfort."
        general_advisory = "Avoid prolonged outdoor workouts. Keep windows closed during peak traffic hours."
        sensitive_advisory = "Children, elderly, and individuals with lung/heart disease should remain indoors."
        mask_recommended = True
        outdoor_exercise = "Not Recommended"
    elif aqi_val <= 400:
        level = "Very High"
        badge_color = "#ef4444"
        summary = "Air quality is hazardous. Severe respiratory illness hazard."
        general_advisory = "Everyone should avoid outdoor physical activities. Wear N95 masks when stepping out."
        sensitive_advisory = "High-risk individuals must strictly stay indoors with air purification active."
        mask_recommended = True
        outdoor_exercise = "Strictly Prohibited"
    else:
        level = "Critical / Emergency"
        badge_color = "#991b1b"
        summary = "Public health emergency. Extreme toxicity levels across the area."
        general_advisory = "Emergency health alert. Strictly remain indoors. Use HEPA air purifiers."
        sensitive_advisory = "Severe risk of acute cardiac/respiratory events. Seek medical attention if experiencing chest tightness."
        mask_recommended = True
        outdoor_exercise = "Hazardous"
        
    return {
        "risk_level": level,
        "badge_color": badge_color,
        "summary": summary,
        "general_advisory": general_advisory,
        "sensitive_advisory": sensitive_advisory,
        "mask_recommended": mask_recommended,
        "outdoor_exercise": outdoor_exercise,
        "dominant_pollutant": dominant_pollutant
    }
