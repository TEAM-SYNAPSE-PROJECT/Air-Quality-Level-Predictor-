"""
Feature Engineering Pipeline.
Transforms cleaned time-series data into rich predictive matrices with:
- Cyclical and calendar time features
- Meteorological interaction terms
- Lagged pollutant observations (Lag 1, 2, 3, 6, 12, 24)
- Rolling statistical aggregates (3h, 6h, 12h, 24h mean, min, max, std)
- Strict no-leakage time-series structure.
"""
from typing import Tuple, List
import pandas as pd
import numpy as np
import math

def encode_season(month: int) -> int:
    """Returns numerical season code: 0: Winter, 1: Summer, 2: Monsoon, 3: Post-Monsoon."""
    if month in [12, 1, 2]:
        return 0 # Winter
    elif month in [3, 4, 5]:
        return 1 # Summer
    elif month in [6, 7, 8, 9]:
        return 2 # Monsoon
    else:
        return 3 # Post-Monsoon

def build_features(df: pd.DataFrame, target_col: str = "pm25") -> Tuple[pd.DataFrame, List[str]]:
    """
    Constructs all time, meteorological, lag, and rolling features for training or inference.
    """
    df_feat = df.copy()
    
    if "timestamp" in df_feat.columns:
        df_feat["timestamp"] = pd.to_datetime(df_feat["timestamp"])
        df_feat = df_feat.sort_values(by="timestamp").reset_index(drop=True)
    else:
        df_feat["timestamp"] = pd.date_range(end=pd.Timestamp.now(), periods=len(df_feat), freq="h")
        
    # 1. TIME FEATURES
    df_feat["hour"] = df_feat["timestamp"].dt.hour
    df_feat["day"] = df_feat["timestamp"].dt.day
    df_feat["dayofweek"] = df_feat["timestamp"].dt.dayofweek
    df_feat["month"] = df_feat["timestamp"].dt.month
    df_feat["year"] = df_feat["timestamp"].dt.year
    df_feat["is_weekend"] = (df_feat["dayofweek"] >= 5).astype(int)
    df_feat["season"] = df_feat["month"].apply(encode_season)
    
    # Cyclical hour & month encoding
    df_feat["hour_sin"] = np.sin(2 * np.pi * df_feat["hour"] / 24.0)
    df_feat["hour_cos"] = np.cos(2 * np.pi * df_feat["hour"] / 24.0)
    df_feat["month_sin"] = np.sin(2 * np.pi * df_feat["month"] / 12.0)
    df_feat["month_cos"] = np.cos(2 * np.pi * df_feat["month"] / 12.0)
    
    # 2. WEATHER & INTERACTION FEATURES
    if "temperature" not in df_feat.columns:
        df_feat["temperature"] = 28.0
    if "humidity" not in df_feat.columns:
        df_feat["humidity"] = 65.0
    if "wind_speed" not in df_feat.columns:
        df_feat["wind_speed"] = 8.0
    if "pressure" not in df_feat.columns:
        df_feat["pressure"] = 1010.0
        
    # Ventilation index proxy (temperature * wind_speed)
    df_feat["ventilation_index"] = df_feat["temperature"] * df_feat["wind_speed"]
    # Humidity-pollution trapping interaction
    df_feat["hum_temp_ratio"] = df_feat["humidity"] / (df_feat["temperature"] + 1.0)
    
    # 3. LAG FEATURES (Strictly past information - no future leakage)
    lag_targets = [target_col]
    if "pm10" in df_feat.columns and target_col != "pm10":
        lag_targets.append("pm10")
    if "no2" in df_feat.columns and target_col != "no2":
        lag_targets.append("no2")
        
    lags = [1, 2, 3, 6, 12, 24]
    for col in lag_targets:
        for lag in lags:
            df_feat[f"{col}_lag_{lag}"] = df_feat[col].shift(lag)
            
    # 4. ROLLING FEATURES (Computed using shifted window to prevent target leakage)
    windows = [3, 6, 12, 24]
    for w in windows:
        # Shift by 1 first so current row's value is excluded from historical rolling window
        shifted = df_feat[target_col].shift(1)
        df_feat[f"{target_col}_rolling_mean_{w}"] = shifted.rolling(window=w, min_periods=1).mean()
        df_feat[f"{target_col}_rolling_min_{w}"] = shifted.rolling(window=w, min_periods=1).min()
        df_feat[f"{target_col}_rolling_max_{w}"] = shifted.rolling(window=w, min_periods=1).max()
        df_feat[f"{target_col}_rolling_std_{w}"] = shifted.rolling(window=w, min_periods=1).std().fillna(0)
        
    # Drop rows that have NaN from earliest lags
    df_feat = df_feat.dropna().reset_index(drop=True)
    
    # Identify feature columns (exclude non-feature metadata)
    exclude_cols = ["timestamp", "city", "state", "station", "aqi_category", "dominant_pollutant", "risk_level", "weather", "status", target_col]
    feature_cols = [c for c in df_feat.columns if c not in exclude_cols]
    
    return df_feat, feature_cols
