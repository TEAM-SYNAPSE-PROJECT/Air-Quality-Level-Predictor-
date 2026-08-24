"""
CPCB National Air Quality Index calculation engine.

The AQI is calculated as the maximum pollutant sub-index.
Concentrations use the same units as the existing project:
PM2.5/PM10/NO2/SO2/O3/NH3/Pb in µg/m³ and CO in mg/m³.
"""

BREAKPOINTS = {
    "pm25": [(0,30,0,50),(31,60,51,100),(61,90,101,200),(91,120,201,300),(121,250,301,400),(251,380,401,500)],
    "pm10": [(0,50,0,50),(51,100,51,100),(101,250,101,200),(251,350,201,300),(351,430,301,400),(431,500,401,500)],
    "no2":  [(0,40,0,50),(41,80,51,100),(81,180,101,200),(181,280,201,300),(281,400,301,400),(401,800,401,500)],
    "so2":  [(0,40,0,50),(41,80,51,100),(81,380,101,200),(381,800,201,300),(801,1600,301,400),(1601,2000,401,500)],
    "co":   [(0,1.0,0,50),(1.1,2.0,51,100),(2.1,10.0,101,200),(10.1,17.0,201,300),(17.1,34.0,301,400),(34.1,50.0,401,500)],
    "o3":   [(0,50,0,50),(51,100,51,100),(101,168,101,200),(169,208,201,300),(209,748,301,400),(749,1000,401,500)],
    "nh3":  [(0,200,0,50),(201,400,51,100),(401,800,101,200),(801,1200,201,300),(1201,1800,301,400),(1801,2400,401,500)],
    "pb":   [(0,0.5,0,50),(0.51,1.0,51,100),(1.01,2.0,101,200),(2.01,3.0,201,300),(3.01,3.5,301,400),(3.51,4.0,401,500)],
}

METADATA = {
    "pm25": ("PM2.5", "µg/m³"),
    "pm10": ("PM10", "µg/m³"),
    "no2": ("NO₂", "µg/m³"),
    "so2": ("SO₂", "µg/m³"),
    "co": ("CO", "mg/m³"),
    "o3": ("O₃", "µg/m³"),
    "nh3": ("NH₃", "µg/m³"),
    "pb": ("Lead", "µg/m³"),
}

def category(aqi):
    aqi = float(aqi)
    if aqi <= 50: return "Good"
    if aqi <= 100: return "Satisfactory"
    if aqi <= 200: return "Moderately Polluted"
    if aqi <= 300: return "Poor"
    if aqi <= 400: return "Very Poor"
    return "Severe"

def health_advisory(cat):
    return {
        "Good": "Minimal impact on health. Ideal for normal outdoor activity.",
        "Satisfactory": "Minor breathing discomfort may occur in sensitive people.",
        "Moderately Polluted": "Sensitive people should limit prolonged strenuous outdoor activity.",
        "Poor": "Most people may experience discomfort on prolonged exposure.",
        "Very Poor": "Respiratory illness risk increases on prolonged exposure.",
        "Severe": "Health emergency conditions; avoid outdoor exertion.",
    }[cat]

def sub_index(pollutant, concentration):
    try:
        c = float(concentration)
    except (TypeError, ValueError):
        return 0
    if c < 0 or pollutant not in BREAKPOINTS:
        return 0
    for blo, bhi, ilo, ihi in BREAKPOINTS[pollutant]:
        if blo <= c <= bhi:
            return round(((ihi-ilo)/(bhi-blo))*(c-blo)+ilo)
    bp = BREAKPOINTS[pollutant][-1]
    if c > bp[1]:
        blo, bhi, ilo, ihi = bp
        return min(500, round(((ihi-ilo)/(bhi-blo))*(c-blo)+ilo))
    return 0

def calculate_aqi(pollutants):
    rows = []
    for key in METADATA:
        if key not in pollutants or pollutants[key] is None:
            continue
        si = sub_index(key, pollutants[key])
        rows.append({
            "pollutant": key,
            "name": METADATA[key][0],
            "unit": METADATA[key][1],
            "concentration": float(pollutants[key]),
            "sub_index": si,
            "category": category(si),
        })
    if not rows:
        return {"aqi": 0, "category": "Good", "dominant": "pm25", "subindices": []}
    dominant = max(rows, key=lambda x: x["sub_index"])
    aqi = int(dominant["sub_index"])
    return {
        "aqi": aqi,
        "category": category(aqi),
        "dominant": dominant["pollutant"],
        "subindices": rows,
        "health": health_advisory(category(aqi)),
    }
