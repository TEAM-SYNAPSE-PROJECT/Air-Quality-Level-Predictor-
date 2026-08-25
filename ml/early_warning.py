"""
Early Warning & Real-Time Alert Dispatcher.
Evaluates 7 distinct environmental trigger cases and generates actionable alerts.
"""
from typing import Dict, Any, List

def evaluate_early_warnings(
    current_aqi: float,
    current_pm25: float = None,
    current_pm10: float = None,
    sub_indices: Dict[str, float] = None,
    recent_trend_delta: float = 0.0,
    forecast_aqi_max: float = None,
    is_anomaly: bool = False
) -> List[Dict[str, Any]]:
    """
    Evaluates 7 early warning scenarios and returns active alerts with severity levels.
    """
    alerts = []
    sub_indices = sub_indices or {}
    
    # CASE 1: AQI reaches high-risk category
    if current_aqi >= 301:
        alerts.append({
            "case_id": "CASE_1_HIGH_AQI",
            "severity": "CRITICAL" if current_aqi > 400 else "HIGH",
            "icon": "🚨",
            "title": f"Critical AQI Threshold Exceeded ({int(current_aqi)})",
            "message": f"Air quality has reached { 'Severe' if current_aqi > 400 else 'Very Poor' } category. Immediate protective measures required.",
            "action": "Avoid outdoor activities, keep indoor air filtered, wear certified N95 respirators if stepping out."
        })
    elif current_aqi >= 201:
        alerts.append({
            "case_id": "CASE_1_POOR_AQI",
            "severity": "MEDIUM",
            "icon": "⚠️",
            "title": f"Poor Air Quality Alert (AQI {int(current_aqi)})",
            "message": "Air quality is in the Poor category. Prolonged outdoor exposure may trigger respiratory discomfort.",
            "action": "Limit intense outdoor cardiovascular exercises; sensitive groups should stay indoors."
        })
        
    # CASE 2: Rapid AQI escalation
    if recent_trend_delta >= 30.0:
        alerts.append({
            "case_id": "CASE_2_RAPID_RISE",
            "severity": "HIGH",
            "icon": "📈",
            "title": f"Rapid AQI Surge (+{recent_trend_delta:.0f} pts in recent hours)",
            "message": "Air pollution levels are climbing rapidly due to deteriorating atmospheric dispersion.",
            "action": "Close exterior building ventilations and prepare indoor filtration units."
        })
        
    # CASE 3: Dangerous PM2.5 elevation
    if current_pm25 is not None and current_pm25 >= 120.0:
        alerts.append({
            "case_id": "CASE_3_DANGEROUS_PM25",
            "severity": "HIGH",
            "icon": "🌫️",
            "title": f"Dangerous Fine Particulate Concentration ({current_pm25:.1f} µg/m³)",
            "message": "PM2.5 exceeds safe national standards by multiple times, penetrating deep into lung alveoli.",
            "action": "Use high-efficiency particulate air (HEPA) purifiers indoors; avoid running combustion appliances."
        })
        
    # CASE 4: Coarse dust / PM10 elevation
    if current_pm10 is not None and current_pm10 >= 250.0:
        alerts.append({
            "case_id": "CASE_4_ELEVATED_PM10",
            "severity": "MEDIUM",
            "icon": "🏜️",
            "title": f"Elevated Coarse Dust PM10 ({current_pm10:.1f} µg/m³)",
            "message": "High coarse dust levels detected from windblown surface soil or construction dust.",
            "action": "Sprinkle water on surrounding paved areas, cover open soil, and wear dust-blocking eyewear."
        })
        
    # CASE 5: Multiple elevated pollutants simultaneously
    elevated_count = sum(1 for si in sub_indices.values() if si >= 150)
    if elevated_count >= 2:
        alerts.append({
            "case_id": "CASE_5_MULTI_POLLUTANT",
            "severity": "HIGH",
            "icon": "☣️",
            "title": f"Multi-Pollutant Co-Exposure Hazard ({elevated_count} Pollutants Elevated)",
            "message": "Simultaneous surge in multiple chemical species (particulates + gases) causing synergistic toxic impact.",
            "action": "Avoid all active exposure; vulnerable populations should consult healthcare providers if experiencing symptoms."
        })
        
    # CASE 6: Forecast predicts dangerous future AQI
    if forecast_aqi_max is not None and forecast_aqi_max >= 300.0:
        alerts.append({
            "case_id": "CASE_6_PREDICTED_SPIKE",
            "severity": "MEDIUM",
            "icon": "🔮",
            "title": f"Forecast Warning: Peak AQI {int(forecast_aqi_max)} Predicted Ahead",
            "message": "Machine learning forecast models indicate worsening air quality in upcoming horizons.",
            "action": "Plan outdoor commutes and sports activities ahead to avoid peak pollution windows."
        })
        
    # CASE 7: Statistical / Isolation Forest Anomaly
    if is_anomaly:
        alerts.append({
            "case_id": "CASE_7_ANOMALY_SPIKE",
            "severity": "MEDIUM",
            "icon": "⚡",
            "title": "Atmospheric Anomaly Detected by Isolation Forest",
            "message": "Machine learning anomaly detectors identified an atypical pollution/meteorological signature.",
            "action": "Verify local emission sources, nearby industrial activities, or agricultural biomass plumes."
        })
        
    return alerts
