"""
Data Cleaning & Preprocessing Pipeline.
Implements robust missing value imputation, negative value clipping,
duplicate deduplication, and datetime standardisation.
"""
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np
from ml.data_validation import normalize_column_names

def clean_air_quality_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans raw air quality data:
    1. Normalizes column headers
    2. Parses and sorts timestamps
    3. Removes duplicates
    4. Clips invalid negative pollutant readings to zero
    5. Imputes missing values using forward-fill / linear interpolation
    """
    df_clean = normalize_column_names(df)
    initial_rows = len(df_clean)
    
    # Drop full duplicates
    df_clean = df_clean.drop_duplicates()
    dups_removed = initial_rows - len(df_clean)
    
    # Standardize datetime
    if "timestamp" in df_clean.columns:
        df_clean["timestamp"] = pd.to_datetime(df_clean["timestamp"], errors="coerce")
        df_clean = df_clean.sort_values(by="timestamp").reset_index(drop=True)
        
    # Pollutant columns clipping
    pollutant_cols = ["pm25", "pm10", "no2", "so2", "co", "o3"]
    for col in pollutant_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
            df_clean[col] = df_clean[col].clip(lower=0.0)
            
    # Meteorological columns cleaning
    met_cols = ["temperature", "humidity", "wind_speed", "wind_direction", "pressure", "rainfall"]
    for col in met_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
            
    # Intelligent time-series interpolation for numerical columns
    numerical_cols = df_clean.select_dtypes(include=[np.number]).columns
    for col in numerical_cols:
        # Interpolate linearly for small gaps, then forward fill, backward fill
        df_clean[col] = df_clean[col].interpolate(method="linear", limit=6)
        df_clean[col] = df_clean[col].ffill().bfill()
        
    # Calculate AQI if missing or if raw pollutants are present
    from ml.aqi_calculator import calculate_indian_aqi
    
    if "aqi" not in df_clean.columns or df_clean["aqi"].isnull().any():
        aqi_list = []
        cat_list = []
        dom_list = []
        risk_list = []
        
        for idx, row in df_clean.iterrows():
            pollutants = {
                p: row[p] for p in pollutant_cols if p in df_clean.columns and not pd.isna(row[p])
            }
            res = calculate_indian_aqi(pollutants)
            aqi_list.append(res["aqi"])
            cat_list.append(res["category"])
            dom_list.append(res["dominant_pollutant"])
            risk_list.append(res["risk_level"])
            
        df_clean["aqi"] = aqi_list
        df_clean["aqi_category"] = cat_list
        df_clean["dominant_pollutant"] = dom_list
        df_clean["risk_level"] = risk_list
        
    cleaning_metadata = {
        "initial_rows": initial_rows,
        "final_rows": len(df_clean),
        "duplicates_removed": dups_removed,
        "imputed_columns": list(numerical_cols),
        "processed_at": pd.Timestamp.now().isoformat()
    }
    
    return df_clean, cleaning_metadata
