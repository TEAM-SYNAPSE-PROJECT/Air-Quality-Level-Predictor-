# ==============================================================================
# Indian Central Pollution Control Board (CPCB) NAQI Calculation Engine
# Exact Piecewise Linear Interpolation Formula:
# Ip = ((IHi - ILo) / (BPHi - BPLo)) * (Cp - BPLo) + ILo
# ==============================================================================

CPCB_BREAKPOINTS = {
    "pm25": [
        (0, 30, 0, 50, "Good"),
        (30, 60, 51, 100, "Satisfactory"),
        (60, 90, 101, 200, "Moderate"),
        (90, 120, 201, 300, "Poor"),
        (120, 250, 301, 400, "Very Poor"),
        (250, 500, 401, 500, "Severe"),
    ],
    "pm10": [
        (0, 50, 0, 50, "Good"),
        (50, 100, 51, 100, "Satisfactory"),
        (100, 250, 101, 200, "Moderate"),
        (250, 350, 201, 300, "Poor"),
        (350, 430, 301, 400, "Very Poor"),
        (430, 600, 401, 500, "Severe"),
    ],
    "no2": [
        (0, 40, 0, 50, "Good"),
        (40, 80, 51, 100, "Satisfactory"),
        (80, 180, 101, 200, "Moderate"),
        (180, 280, 201, 300, "Poor"),
        (280, 400, 301, 400, "Very Poor"),
        (400, 500, 401, 500, "Severe"),
    ],
    "so2": [
        (0, 40, 0, 50, "Good"),
        (40, 80, 51, 100, "Satisfactory"),
        (80, 380, 101, 200, "Moderate"),
        (380, 800, 201, 300, "Poor"),
        (800, 1600, 301, 400, "Very Poor"),
        (1600, 2000, 401, 500, "Severe"),
    ],
    "co": [
        (0, 1.0, 0, 50, "Good"),
        (1.0, 2.0, 51, 100, "Satisfactory"),
        (2.0, 10.0, 101, 200, "Moderate"),
        (10.0, 17.0, 201, 300, "Poor"),
        (17.0, 34.0, 301, 400, "Very Poor"),
        (34.0, 50.0, 401, 500, "Severe"),
    ],
    "o3": [
        (0, 50, 0, 50, "Good"),
        (50, 100, 51, 100, "Satisfactory"),
        (100, 168, 101, 200, "Moderate"),
        (168, 208, 201, 300, "Poor"),
        (208, 748, 301, 400, "Very Poor"),
        (748, 1000, 401, 500, "Severe"),
    ]
}

def calculate_sub_index(pollutant, conc):
    if conc is None or conc < 0:
        return 0, "Good"
    brackets = CPCB_BREAKPOINTS.get(pollutant, [])
    for (bp_low, bp_high, i_low, i_high, category) in brackets:
        if bp_low <= conc <= bp_high:
            sub = ((i_high - i_low) / (bp_high - bp_low)) * (conc - bp_low) + i_low
            return round(sub), category
    # If above max bracket
    if brackets and conc > brackets[-1][1]:
        return 500, "Severe"
    return 0, "Good"

def calculate_india_aqi(pollutant_dict):
    sub_indices = {}
    for p, val in pollutant_dict.items():
        if p in CPCB_BREAKPOINTS:
            idx, cat = calculate_sub_index(p, val)
            sub_indices[p] = {"sub_index": idx, "category": cat}

    if not sub_indices:
        return {"aqi": 0, "category": "Good", "dominant_pollutant": "None", "sub_indices": {}}

    dominant_pollutant = max(sub_indices.keys(), key=lambda k: sub_indices[k]["sub_index"])
    overall_aqi = sub_indices[dominant_pollutant]["sub_index"]
    overall_category = get_aqi_category(overall_aqi)

    return {
        "aqi": overall_aqi,
        "category": overall_category,
        "dominant_pollutant": dominant_pollutant.upper(),
        "sub_indices": sub_indices
    }

def get_aqi_category(aqi):
    if aqi <= 50: return "Good"
    if aqi <= 100: return "Satisfactory"
    if aqi <= 200: return "Moderate"
    if aqi <= 300: return "Poor"
    if aqi <= 400: return "Very Poor"
    return "Severe"

def get_category_color(category):
    colors = {
        "Good": "#10b981",
        "Satisfactory": "#84cc16",
        "Moderate": "#f59e0b",
        "Poor": "#f97316",
        "Very Poor": "#ef4444",
        "Severe": "#7f1d1d"
    }
    return colors.get(category, "#10b981")
