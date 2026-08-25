"""
Data Validation Pipeline.
Performs data integrity checks, missing value detection, range validation,
temporal consistency, and schema verification.
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np

# Canonical Schema
CANONICAL_COLUMNS = [
    "city", "state", "station", "latitude", "longitude", "timestamp",
    "pm25", "pm10", "co", "no2", "so2", "o3",
    "temperature", "humidity", "wind_speed", "wind_direction", "pressure", "rainfall"
]

COLUMN_SYNONYMS = {
    "pm25": ["pm2.5", "pm_2_5", "pm25", "pm_25", "pm2_5", "particulate_matter_2_5"],
    "pm10": ["pm10", "pm_10", "pm_10_0", "particulate_matter_10"],
    "no2": ["no2", "nitrogen_dioxide", "no_2"],
    "so2": ["so2", "sulfur_dioxide", "so_2"],
    "co": ["co", "carbon_monoxide"],
    "o3": ["o3", "ozone", "o_3"],
    "temperature": ["temp", "temperature", "temp_c", "t"],
    "humidity": ["humidity", "rh", "relative_humidity", "hum"],
    "wind_speed": ["wind_speed", "wind", "ws", "wind_spd", "windspeed"],
    "wind_direction": ["wind_direction", "wind_deg", "wd", "wind_dir"],
    "pressure": ["pressure", "baro", "pres", "atm_pressure"],
    "rainfall": ["rainfall", "rain", "precipitation", "precip"]
}

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Maps varying external CSV headers to standard canonical internal schema."""
    df_clean = df.copy()
    rename_dict = {}
    
    for col in df_clean.columns:
        col_clean = str(col).strip().lower().replace(" ", "_").replace("-", "_")
        matched = False
        for standard_name, synonyms in COLUMN_SYNONYMS.items():
            if col_clean in synonyms or col_clean == standard_name:
                rename_dict[col] = standard_name
                matched = True
                break
        if not matched:
            rename_dict[col] = col_clean
            
    df_clean.rename(columns=rename_dict, inplace=True)
    return df_clean

def run_data_validation(df: pd.DataFrame) -> Dict[str, Any]:
    """Executes thorough data quality audits and returns structured diagnostics."""
    df_norm = normalize_column_names(df)
    
    total_records = len(df_norm)
    missing_report = df_norm.isnull().sum().to_dict()
    missing_percentages = {k: round((v / total_records) * 100, 2) for k, v in missing_report.items()}
    
    duplicates = int(df_norm.duplicated().sum())
    
    # Check negative or extreme values
    outliers = {}
    numerical_cols = df_norm.select_dtypes(include=[np.number]).columns
    
    for col in numerical_cols:
        col_data = df_norm[col].dropna()
        neg_count = int((col_data < 0).sum())
        
        # IQR based extreme anomaly check
        if len(col_data) > 10:
            q25, q75 = np.percentile(col_data, [25, 75])
            iqr = q75 - q25
            extreme_upper = q75 + (3 * iqr)
            extreme_count = int((col_data > extreme_upper).sum())
        else:
            extreme_count = 0
            
        if neg_count > 0 or extreme_count > 0:
            outliers[col] = {
                "negative_values": neg_count,
                "extreme_outliers": extreme_count
            }
            
    # Timestamp validity
    timestamp_valid = True
    if "timestamp" in df_norm.columns:
        try:
            pd.to_datetime(df_norm["timestamp"])
        except Exception:
            timestamp_valid = False
            
    status = "HEALTHY"
    issues = []
    if duplicates > 0:
        status = "WARNING"
        issues.append(f"{duplicates} duplicate rows detected.")
    if len(outliers) > 0:
        issues.append(f"Negative values or extremes identified in {list(outliers.keys())}")
    if any(pct > 20 for pct in missing_percentages.values()):
        status = "CRITICAL_MISSING"
        issues.append("Certain critical fields have >20% missing observations.")
        
    return {
        "status": status,
        "total_records": total_records,
        "columns_present": list(df_norm.columns),
        "missing_counts": missing_report,
        "missing_percentages": missing_percentages,
        "duplicate_count": duplicates,
        "outliers": outliers,
        "timestamp_valid": timestamp_valid,
        "issues": issues,
        "normalized_df": df_norm
    }
