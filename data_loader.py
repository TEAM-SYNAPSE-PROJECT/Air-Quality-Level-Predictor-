"""
Flexible data loader.

Priority:
1. Uploaded CSV from Streamlit.
2. A local CSV supplied by the user.
3. Built-in demo data when real data is unavailable.

This makes the project runnable even without an API.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from data import CITIES

FEATURES = ["humidity","no","no2","co","so2","pm25","pm10","o3","temperature"]

ALIASES = {
    "relativehumidity": "humidity",
    "relative_humidity": "humidity",
    "rh": "humidity",
    "pm2.5": "pm25",
    "pm_2_5": "pm25",
    "pm10": "pm10",
    "nitrogen_dioxide": "no2",
    "nitrogen dioxide": "no2",
    "sulfur_dioxide": "so2",
    "sulphur_dioxide": "so2",
    "carbon_monoxide": "co",
    "ozone": "o3",
}

def _normalise_columns(df):
    df = df.copy()
    rename = {}
    for col in df.columns:
        key = str(col).strip().lower()
        key = ALIASES.get(key, key)
        rename[col] = key
    return df.rename(columns=rename)

def demo_dataframe(city=None, periods=720):
    city = city or CITIES[0]
    rng = np.random.default_rng(42)
    trend = city.get("trend24h", [city["pollutants"]["pm25"]])
    base = city["pollutants"]
    weather = city["weather"]
    dates = pd.date_range(end=pd.Timestamp.now(tz="Asia/Kolkata"), periods=periods, freq="h")
    aqi_pattern = np.resize(np.asarray(trend, dtype=float), periods)
    aqi_pattern = aqi_pattern + rng.normal(0, 5, periods)
    scale = np.maximum(aqi_pattern / max(city["pollutants"]["pm25"], 1), 0.35)
    df = pd.DataFrame({
        "datetime": dates,
        "humidity": np.clip(weather["humidity"] + rng.normal(0, 7, periods), 20, 95),
        "no": np.clip(8 + rng.normal(0, 3, periods), 0, None),
        "no2": np.clip(base["no2"] * scale + rng.normal(0, 5, periods), 0, None),
        "co": np.clip(base["co"] * scale + rng.normal(0, .15, periods), .05, None),
        "so2": np.clip(base["so2"] * scale + rng.normal(0, 3, periods), 0, None),
        "pm25": np.clip(base["pm25"] * scale + rng.normal(0, 8, periods), 1, None),
        "pm10": np.clip(base["pm10"] * scale + rng.normal(0, 12, periods), 1, None),
        "o3": np.clip(base["o3"] * scale + rng.normal(0, 5, periods), 1, None),
        "temperature": weather["temperature"] + rng.normal(0, 2, periods),
    })
    return df

def prepare_dataframe(df):
    df = _normalise_columns(df)
    if "datetime" not in df.columns:
        for candidate in ["datetimelocal","datetimeLocal","date","timestamp","time"]:
            if candidate in df.columns:
                df["datetime"] = df[candidate]
                break
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    for col in FEATURES:
        if col not in df.columns:
            df[col] = np.nan
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def load_csv(path_or_buffer):
    return prepare_dataframe(pd.read_csv(path_or_buffer))

def fill_missing_with_demo(df, city=None):
    demo = demo_dataframe(city, max(len(df), 100))
    df = df.copy()
    for col in FEATURES:
        if df[col].isna().all():
            df[col] = demo[col].values[:len(df)]
        else:
            df[col] = df[col].interpolate().ffill().bfill()
    return df
