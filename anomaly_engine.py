"""Human-readable anomaly/spike analysis built on Isolation Forest output."""

import numpy as np

def pollutant_spikes(city):
    p = city["pollutants"]
    baselines = {
        "pm25": (55, 18), "pm10": (110, 35), "no2": (38, 12),
        "so2": (14, 5), "co": (1.5, .5), "o3": (45, 12)
    }
    rows = []
    for key, (mean, std) in baselines.items():
        value = float(p.get(key, 0))
        z = (value - mean) / max(std, .01)
        if z >= 3: severity = "CRITICAL_SPIKE"
        elif z >= 2: severity = "HIGH_SPIKE"
        elif z >= 1.2: severity = "ELEVATED"
        else: severity = "NORMAL"
        rows.append({
            "pollutant": key.upper(),
            "current": round(value, 2),
            "baseline_mean": mean,
            "z_score": round(z, 2),
            "severity": severity
        })
    return sorted(rows, key=lambda x: x["z_score"], reverse=True)
