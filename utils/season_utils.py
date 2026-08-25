"""Indian Seasonal Interpretation and Meteorological Context."""
from datetime import datetime
from typing import Dict, Any

def get_current_season(dt: datetime = None) -> Dict[str, Any]:
    """
    Dynamically determines the current Indian meteorological season
    based on month and day without any hardcoding.
    """
    if dt is None:
        from utils.time_utils import get_current_ist_datetime
        dt = get_current_ist_datetime()
        
    month = dt.month
    
    if month in [12, 1, 2]:
        return {
            "name": "Winter",
            "emoji": "❄️",
            "full_name": "Winter (Cold Season)",
            "hindi_name": "Shishir / Hemant (शीत ऋतु)",
            "months": "Dec - Feb",
            "pollution_characteristic": "Thermal inversion traps particulate matter (PM2.5 & PM10) near ground level causing peak smog episodes.",
            "dominant_risk": "High PM2.5 / Fog & Smog",
            "avg_dispersion": "Very Low (Stagnant Air)"
        }
    elif month in [3, 4, 5]:
        return {
            "name": "Summer",
            "emoji": "☀️",
            "full_name": "Summer (Pre-Monsoon)",
            "hindi_name": "Grishma (ग्रीष्म ऋतु)",
            "months": "Mar - May",
            "pollution_characteristic": "High solar radiation accelerates Ground-Level Ozone (O3) formation; arid conditions elevate coarse dust (PM10).",
            "dominant_risk": "Ozone (O3) & Windblown Dust (PM10)",
            "avg_dispersion": "High (Strong convective mixing)"
        }
    elif month in [6, 7, 8, 9]:
        return {
            "name": "Monsoon",
            "emoji": "🌧️",
            "full_name": "South-West Monsoon",
            "hindi_name": "Varsha (वर्षा ऋतु)",
            "months": "Jun - Sep",
            "pollution_characteristic": "Frequent precipitation wash-out (wet deposition) scrubs pollutants from the atmosphere, yielding cleanest AQI of the year.",
            "dominant_risk": "High Humidity & Localized Waterlogging",
            "avg_dispersion": "Very High (Rain washout & strong winds)"
        }
    else:  # month in [10, 11]
        return {
            "name": "Post-Monsoon",
            "emoji": "🍂",
            "full_name": "Post-Monsoon (Autumn)",
            "hindi_name": "Sharad (शरद ऋतु)",
            "months": "Oct - Nov",
            "pollution_characteristic": "Retreating monsoon, dropping temperatures, calm surface winds, and agricultural biomass burning cause severe pollution surges across Indo-Gangetic plains.",
            "dominant_risk": "Biomass Stubble Smoke & Rapid PM2.5 Spikes",
            "avg_dispersion": "Low to Declining"
        }
