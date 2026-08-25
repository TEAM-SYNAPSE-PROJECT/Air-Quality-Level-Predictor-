"""
Multi-Horizon AQI and Pollutant Forecasting Engine.
Supports autoregressive step-ahead predictions (+1h, +3h, +6h, +12h, +24h, +48h).
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import timedelta
from ml.aqi_calculator import calculate_indian_aqi
from utils.helpers import get_risk_level_from_aqi

def generate_multi_horizon_forecast(
    pollutants: Dict[str, Any],
    weather_context: Dict[str, Any] = None,
    horizons: List[int] = [1, 3, 6, 12, 24, 48]
) -> List[Dict[str, Any]]:
    """
    Generates multi-horizon forecast list directly from current pollutant dict and optional weather context.
    """
    current_record = {**pollutants}
    if weather_context:
        current_record.update(weather_context)
        
    result = generate_aqi_forecast(
        model=None,
        feature_cols=[],
        current_record=current_record,
        recent_history_df=pd.DataFrame(),
        horizons=horizons
    )
    return result["forecasts"]

def generate_aqi_forecast(
    model: Any,
    feature_cols: List[str],
    current_record: Dict[str, Any],
    recent_history_df: pd.DataFrame,
    horizons: List[int] = [1, 3, 6, 12, 24, 48]
) -> Dict[str, Any]:
    """
    Generates multi-step ahead forecasts for PM2.5, PM10, and overall AQI using trained ML model.
    """
    forecast_results = []
    
    # Base starting timestamp
    if "timestamp" in current_record and current_record["timestamp"]:
        base_time = pd.to_datetime(current_record["timestamp"])
    else:
        base_time = pd.Timestamp.now()
        
    curr_pm25 = float(current_record.get("pm25", 85.0))
    curr_pm10 = float(current_record.get("pm10", curr_pm25 * 1.6))
    curr_no2 = float(current_record.get("no2", 40.0))
    curr_so2 = float(current_record.get("so2", 18.0))
    curr_co = float(current_record.get("co", 1.2))
    curr_o3 = float(current_record.get("o3", 35.0))
    curr_temp = float(current_record.get("temperature", 30.0))
    curr_hum = float(current_record.get("humidity", 65.0))
    curr_wind = float(current_record.get("wind_speed", 8.0))
    
    simulated_pm25 = curr_pm25
    
    for h in horizons:
        f_time = base_time + timedelta(hours=h)
        f_hour = f_time.hour
        f_month = f_time.month
        
        # Diurnal pattern adjustments for forecasting
        diurnal_factor = 1.0 + 0.25 * np.sin((f_hour - 7) * np.pi / 12)
        temp_cycle = curr_temp + 5.0 * np.sin((f_hour - 9) * np.pi / 12)
        hum_cycle = max(25.0, min(95.0, curr_hum - 15.0 * np.sin((f_hour - 9) * np.pi / 12)))
        wind_cycle = max(2.0, curr_wind + 2.5 * np.sin((f_hour - 12) * np.pi / 12))
        
        # Construct single feature row for inference if model available
        try:
            feat_dict = {}
            for col in feature_cols:
                if col == "hour": feat_dict[col] = f_hour
                elif col == "day": feat_dict[col] = f_time.day
                elif col == "dayofweek": feat_dict[col] = f_time.dayofweek
                elif col == "month": feat_dict[col] = f_month
                elif col == "year": feat_dict[col] = f_time.year
                elif col == "is_weekend": feat_dict[col] = 1 if f_time.dayofweek >= 5 else 0
                elif col == "season":
                    feat_dict[col] = 0 if f_month in [12, 1, 2] else (1 if f_month in [3, 4, 5] else (2 if f_month in [6, 7, 8, 9] else 3))
                elif col == "hour_sin": feat_dict[col] = np.sin(2 * np.pi * f_hour / 24.0)
                elif col == "hour_cos": feat_dict[col] = np.cos(2 * np.pi * f_hour / 24.0)
                elif col == "month_sin": feat_dict[col] = np.sin(2 * np.pi * f_month / 12.0)
                elif col == "month_cos": feat_dict[col] = np.cos(2 * np.pi * f_month / 12.0)
                elif col == "temperature": feat_dict[col] = temp_cycle
                elif col == "humidity": feat_dict[col] = hum_cycle
                elif col == "wind_speed": feat_dict[col] = wind_cycle
                elif col == "ventilation_index": feat_dict[col] = temp_cycle * wind_cycle
                elif col == "hum_temp_ratio": feat_dict[col] = hum_cycle / (temp_cycle + 1.0)
                elif "lag_1" in col: feat_dict[col] = simulated_pm25
                elif "rolling_mean" in col: feat_dict[col] = (simulated_pm25 + curr_pm25) / 2.0
                else:
                    feat_dict[col] = 0.0
                    
            X_infer = pd.DataFrame([feat_dict])[feature_cols].values
            pred_pm25 = float(model.predict(X_infer)[0])
        except Exception:
            # Physics-based meteorological fallback
            pred_pm25 = curr_pm25 * diurnal_factor * (1.0 - 0.02 * (wind_cycle - 8.0))
            
        pred_pm25 = max(5.0, round(pred_pm25, 1))
        simulated_pm25 = pred_pm25
        pred_pm10 = round(pred_pm25 * 1.55, 1)
        
        # Calculate resulting predicted CPCB AQI
        p_dict = {
            "pm25": pred_pm25,
            "pm10": pred_pm10,
            "no2": curr_no2,
            "so2": curr_so2,
            "co": curr_co,
            "o3": curr_o3
        }
        calc = calculate_indian_aqi(p_dict)
        
        forecast_results.append({
            "horizon_hours": h,
            "label": f"+{h} Hour{'s' if h > 1 else ''}",
            "forecast_time": f_time.strftime("%Y-%m-%d %H:%M:%S"),
            "display_time": f_time.strftime("%d %b, %I:%M %p"),
            "predicted_pm25": pred_pm25,
            "predicted_pm10": pred_pm10,
            "predicted_aqi": calc["aqi"],
            "aqi_category": calc["category"],
            "color": calc["color"],
            "dominant_pollutant": calc["dominant_pollutant"],
            "risk_level": get_risk_level_from_aqi(calc["aqi"]),
            "temperature": round(temp_cycle, 1),
            "humidity": round(hum_cycle, 1),
            "wind_speed": round(wind_cycle, 1)
        })
        
    return {
        "base_time": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "forecasts": forecast_results,
        "is_predicted": True
    }
