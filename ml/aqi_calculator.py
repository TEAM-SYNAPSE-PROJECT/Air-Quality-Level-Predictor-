"""
Indian Central Pollution Control Board (CPCB) National Air Quality Index (NAQI) Calculator.
Implements official mathematical piecewise linear sub-index interpolation.
"""
from typing import Dict, Any, Optional, Tuple

# Official CPCB Breakpoints for AQI (Category index boundaries: [0-50, 51-100, 101-200, 201-300, 301-400, 401-500])
AQI_I_LO = [0, 51, 101, 201, 301, 401]
AQI_I_HI = [50, 100, 200, 300, 400, 500]

# Pollutant Concentration Breakpoints (B_LO, B_HI) in µg/m³ (CO in mg/m³)
BREAKPOINTS = {
    "pm25": [(0, 30), (31, 60), (61, 90), (91, 120), (121, 250), (251, 350)],
    "pm10": [(0, 50), (51, 100), (101, 250), (251, 350), (351, 430), (431, 500)],
    "no2":  [(0, 40), (41, 80), (81, 180), (181, 280), (281, 400), (401, 500)],
    "so2":  [(0, 40), (41, 80), (81, 380), (381, 800), (801, 1600), (1601, 2000)],
    "co":   [(0, 1.0), (1.1, 2.0), (2.1, 10.0), (10.1, 17.0), (17.1, 34.0), (34.1, 50.0)],
    "o3":   [(0, 50), (51, 100), (101, 168), (169, 208), (209, 748), (749, 1000)]
}

def calculate_sub_index(pollutant: str, concentration: float) -> Optional[float]:
    """
    Calculates sub-index Ip for a given pollutant concentration Cp using CPCB formula:
    Ip = [(I_HI - I_LO) / (B_HI - B_LO)] * (Cp - B_LO) + I_LO
    """
    if concentration is None or concentration < 0:
        return None
        
    p_key = pollutant.lower().replace(".", "").replace("_", "")
    if p_key not in BREAKPOINTS:
        return None
        
    bp_list = BREAKPOINTS[p_key]
    
    for i, (b_lo, b_hi) in enumerate(bp_list):
        if b_lo <= concentration <= b_hi:
            i_lo = AQI_I_LO[i]
            i_hi = AQI_I_HI[i]
            sub_idx = ((i_hi - i_lo) / (b_hi - b_lo)) * (concentration - b_lo) + i_lo
            return round(sub_idx, 1)
            
    # If concentration exceeds highest defined bracket, extrapolate linearly from top bracket
    last_idx = len(bp_list) - 1
    b_lo, b_hi = bp_list[last_idx]
    i_lo, i_hi = AQI_I_LO[last_idx], AQI_I_HI[last_idx]
    sub_idx = ((i_hi - i_lo) / (b_hi - b_lo)) * (concentration - b_lo) + i_lo
    return round(sub_idx, 1)

def get_aqi_category(aqi_val: float) -> Tuple[str, str, str]:
    """Returns (Category, Color, Health Impact Description)."""
    val = round(aqi_val)
    if val <= 50:
        return "Good", "#10b981", "Minimal impact. Clean and safe air."
    elif val <= 100:
        return "Satisfactory", "#84cc16", "Minor breathing discomfort to sensitive individuals."
    elif val <= 200:
        return "Moderate", "#f59e0b", "Breathing discomfort to people with asthma, lungs and heart diseases."
    elif val <= 300:
        return "Poor", "#f97316", "Breathing discomfort to most people on prolonged exposure."
    elif val <= 400:
        return "Very Poor", "#ef4444", "Respiratory illness on prolonged exposure. Pronounced effect on vulnerable groups."
    else:
        return "Severe", "#991b1b", "Emergency health warning. Affects healthy individuals and severely impacts vulnerable populations."

def calculate_indian_aqi(pollutants: Dict[str, float]) -> Dict[str, Any]:
    """
    Computes overall CPCB AQI, sub-indices for all available pollutants,
    dominant pollutant, category, and health advisory.
    """
    sub_indices = {}
    
    for p, val in pollutants.items():
        if val is not None:
            si = calculate_sub_index(p, float(val))
            if si is not None:
                norm_p = p.lower().replace(".", "").replace("_", "")
                sub_indices[norm_p] = si
                
    if not sub_indices:
        return {
            "aqi": None,
            "category": "Unavailable",
            "color": "#6b7280",
            "dominant_pollutant": "None",
            "dominant_subindex": 0.0,
            "dominant_pollutant_display": "None",
            "sub_indices": {},
            "health_statement": "Insufficient pollutant data to compute CPCB AQI.",
            "risk_level": "Unknown"
        }
        
    # Dominant pollutant is the one with highest sub-index
    dominant_key = max(sub_indices, key=sub_indices.get)
    dominant_subindex = float(sub_indices[dominant_key])
    max_aqi = round(dominant_subindex)
    
    category, color, health_stmt = get_aqi_category(max_aqi)
    
    # Map dominant key to display format
    display_names = {
        "pm25": "PM2.5 (Fine Particulate)",
        "pm10": "PM10 (Coarse Dust)",
        "no2": "NO2 (Nitrogen Dioxide)",
        "so2": "SO2 (Sulfur Dioxide)",
        "co": "CO (Carbon Monoxide)",
        "o3": "O3 (Ozone)"
    }
    
    from utils.helpers import get_risk_level_from_aqi
    risk = get_risk_level_from_aqi(max_aqi)
    
    return {
        "aqi": max_aqi,
        "category": category,
        "color": color,
        "dominant_pollutant": dominant_key.upper(),
        "dominant_subindex": dominant_subindex,
        "dominant_pollutant_display": display_names.get(dominant_key, dominant_key.upper()),
        "sub_indices": sub_indices,
        "health_statement": health_stmt,
        "risk_level": risk
    }
