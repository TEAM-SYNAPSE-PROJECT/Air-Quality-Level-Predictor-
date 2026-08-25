"""
Pollutant Driver Analysis & Causality Breakdown.
Determines exact contribution percentages of each pollutant to current AQI
and explains underlying environmental drivers.
"""
from typing import Dict, Any, List
from ml.aqi_calculator import calculate_sub_index

POLLUTANT_DISPLAY_CONFIG = {
    "pm25": {"name": "PM2.5 (Fine Particles)", "source": "Vehicular exhaust, biomass burning, coal combustion, industrial emissions", "unit": "µg/m³"},
    "pm10": {"name": "PM10 (Coarse Dust)", "source": "Road dust, construction activities, soil erosion, open quarrying", "unit": "µg/m³"},
    "no2": {"name": "NO2 (Nitrogen Dioxide)", "source": "High-temperature combustion in diesel vehicles and thermal power plants", "unit": "µg/m³"},
    "so2": {"name": "SO2 (Sulfur Dioxide)", "source": "Coal-fired thermal plants, heavy diesel engines, oil refineries", "unit": "µg/m³"},
    "co": {"name": "CO (Carbon Monoxide)", "source": "Incomplete combustion in engines, biomass stoves, solid waste burning", "unit": "mg/m³"},
    "o3": {"name": "O3 (Ground-level Ozone)", "source": "Photochemical reaction between NOx and VOCs under intense sunlight", "unit": "µg/m³"}
}

def analyze_pollutant_drivers(pollutant_data: Dict[str, float]) -> Dict[str, Any]:
    """
    Computes pollutant sub-indices, percentage driver contributions, and textual explanations.
    """
    sub_indices = {}
    
    for p in ["pm25", "pm10", "no2", "so2", "co", "o3"]:
        val = pollutant_data.get(p)
        if val is not None:
            si = calculate_sub_index(p, float(val))
            if si is not None:
                sub_indices[p] = si
                
    if not sub_indices:
        return {"drivers": [], "dominant": "None", "summary": "No pollutant telemetry available."}
        
    total_si_sum = sum(sub_indices.values())
    max_si = max(sub_indices.values())
    dominant_key = max(sub_indices, key=sub_indices.get)
    
    driver_breakdown = []
    for p, si in sorted(sub_indices.items(), key=lambda x: x[1], reverse=True):
        pct = (si / total_si_sum) * 100.0 if total_si_sum > 0 else 0.0
        cfg = POLLUTANT_DISPLAY_CONFIG.get(p, {"name": p.upper(), "source": "General emissions", "unit": ""})
        
        driver_breakdown.append({
            "pollutant": p,
            "display_name": cfg["name"],
            "raw_value": pollutant_data.get(p),
            "unit": cfg["unit"],
            "sub_index": round(si, 1),
            "percentage_contribution": round(pct, 1),
            "source_origin": cfg["source"],
            "is_dominant": (p == dominant_key)
        })
        
    # Reason analysis
    reasons = []
    dom_cfg = POLLUTANT_DISPLAY_CONFIG.get(dominant_key, {})
    reasons.append(f"{dom_cfg.get('name', dominant_key.upper())} is the primary driver with a calculated sub-index of {max_si:.0f}.")
    
    if dominant_key == "pm25":
        reasons.append("Fine particulates (PM2.5) are elevated, indicating heavy combustion/vehicular emissions trapped by atmospheric boundaries.")
    elif dominant_key == "pm10":
        reasons.append("Coarse particulates (PM10) are dominating, indicating significant dust resuspension, construction debris, or arid winds.")
    elif dominant_key == "no2":
        reasons.append("Nitrogen dioxide (NO2) is high, indicating heavy localized traffic congestion or industrial stack combustion.")
    elif dominant_key == "o3":
        reasons.append("Ground-level ozone (O3) is elevated, reflecting intense solar radiation interacting with vehicular precursor gases.")
        
    return {
        "dominant_pollutant": dominant_key.upper(),
        "dominant_pollutant_subindex": max_si,
        "drivers": driver_breakdown,
        "reasons": reasons,
        "primary_source": dom_cfg.get("source", "Industrial & vehicular combustion")
    }
