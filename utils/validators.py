"""Data validation, range checks, and integrity audits."""
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

# Valid meteorological and environmental bounds
POLLUTANT_BOUNDS = {
    "pm25": (0.0, 1000.0, "µg/m³"),
    "pm10": (0.0, 1500.0, "µg/m³"),
    "no2": (0.0, 1000.0, "µg/m³"),
    "so2": (0.0, 1000.0, "µg/m³"),
    "co": (0.0, 100.0, "mg/m³"),
    "o3": (0.0, 800.0, "µg/m³"),
    "temperature": (-20.0, 60.0, "°C"),
    "humidity": (0.0, 100.0, "%"),
    "wind_speed": (0.0, 150.0, "km/h"),
    "pressure": (800.0, 1100.0, "hPa"),
    "rainfall": (0.0, 500.0, "mm")
}

def validate_pollutant_record(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates a single telemetry measurement dict."""
    issues = []
    
    for key, (min_v, max_v, unit) in POLLUTANT_BOUNDS.items():
        if key in record and record[key] is not None:
            val = float(record[key])
            if val < min_v:
                issues.append(f"{key.upper()} value {val} is negative or below physiological minimum ({min_v} {unit})")
            elif val > max_v:
                issues.append(f"{key.upper()} value {val} exceeds theoretical ceiling ({max_v} {unit})")
                
    # Coordinate validation
    if "latitude" in record and record["latitude"] is not None:
        lat = float(record["latitude"])
        if not (6.0 <= lat <= 38.0):
            issues.append(f"Latitude {lat} is outside Indian geographic boundaries (6°N to 38°N)")
            
    if "longitude" in record and record["longitude"] is not None:
        lon = float(record["longitude"])
        if not (68.0 <= lon <= 98.0):
            issues.append(f"Longitude {lon} is outside Indian geographic boundaries (68°E to 98°E)")
            
    return len(issues) == 0, issues

def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Generates an extensive data validation summary for CSV or ingested dataset."""
    summary = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "missing_counts": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "invalid_ranges": {},
        "outlier_counts": {},
        "status": "PASS"
    }
    
    # Check standard columns
    for col in df.columns:
        col_lower = col.lower()
        matched_key = None
        for k in POLLUTANT_BOUNDS:
            if k in col_lower:
                matched_key = k
                break
        if matched_key:
            min_v, max_v, _ = POLLUTANT_BOUNDS[matched_key]
            numeric_col = pd.to_numeric(df[col], errors='coerce')
            below_min = (numeric_col < min_v).sum()
            above_max = (numeric_col > max_v).sum()
            if below_min > 0 or above_max > 0:
                summary["invalid_ranges"][col] = {
                    "below_min": int(below_min),
                    "above_max": int(above_max)
                }
                
    if summary["duplicate_rows"] > 0 or len(summary["invalid_ranges"]) > 0:
        summary["status"] = "WARNINGS DETECTED"
        
    return summary
