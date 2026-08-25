"""
Machine-learning engine for AQI prediction and forecasting.

Models:
- XGBoost Regressor when xgboost is installed.
- RandomForest fallback when it is not.
- Isolation Forest for multivariate anomaly detection.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from xgboost import XGBRegressor
    XGB_AVAILABLE = True
except Exception:
    XGB_AVAILABLE = False

MODEL_FEATURES = [
    "humidity","no","no2","co","so2","pm25","pm10","o3","temperature",
    "hour","dayofweek","pm25_lag_1","pm25_lag_3","pm25_lag_6",
    "pm25_lag_12","pm25_lag_24","pm25_roll_6","wind_dispersion"
]

def engineer_features(df):
    out = df.copy()
    if "datetime" not in out.columns:
        out["datetime"] = pd.date_range(end=pd.Timestamp.now(), periods=len(out), freq="h")
    out["datetime"] = pd.to_datetime(out["datetime"], errors="coerce")
    out["hour"] = out["datetime"].dt.hour.fillna(12)
    out["dayofweek"] = out["datetime"].dt.dayofweek.fillna(0)
    for lag in [1,3,6,12,24]:
        out[f"pm25_lag_{lag}"] = out["pm25"].shift(lag)
    out["pm25_roll_6"] = out["pm25"].rolling(6).mean()
    out["wind_dispersion"] = 1.0 / (out["humidity"].clip(lower=1) + 1)
    out = out.replace([np.inf,-np.inf], np.nan).dropna()
    return out

def train_aqi_model(df):
    data = engineer_features(df)
    if len(data) < 60:
        raise ValueError("At least 60 usable rows are recommended for ML training.")
    # A simple target for this project: AQI proxy = maximum pollutant sub-index.
    from cpcb_aqi import calculate_aqi
    data["target_aqi"] = data.apply(
        lambda r: calculate_aqi({k: r[k] for k in ["pm25","pm10","no2","so2","co","o3"]})["aqi"],
        axis=1,
    )
    cols = [c for c in MODEL_FEATURES if c in data.columns]
    X, y = data[cols], data["target_aqi"]
    split = int(len(data) * .8)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    if XGB_AVAILABLE:
        model = XGBRegressor(
            n_estimators=250, max_depth=5, learning_rate=.05,
            subsample=.85, colsample_bytree=.85, objective="reg:squarederror",
            random_state=42, n_jobs=2
        )
        algorithm = "XGBoost Regressor"
    else:
        model = RandomForestRegressor(n_estimators=250, random_state=42, n_jobs=-1)
        algorithm = "Random Forest Regressor"

    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    metrics = {
        "MAE": float(mean_absolute_error(y_test, pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_test, pred))),
        "R2": float(r2_score(y_test, pred)),
        "algorithm": algorithm,
        "features": cols,
    }
    return model, metrics, data

def forecast_aqi(df, horizon=24):
    model, metrics, data = train_aqi_model(df)
    history = data.copy()
    future = []
    last = history.iloc[-1].copy()
    for step in range(1, horizon + 1):
        row = last.copy()
        if "datetime" in row:
            row["datetime"] = pd.to_datetime(last["datetime"]) + pd.Timedelta(hours=step)
        # Persistence + gentle time-of-day adjustment gives a stable recursive forecast.
        for col in ["pm25","pm10","no2","co","so2","o3","humidity","temperature","no"]:
            if col in row:
                row[col] = float(last[col])
        frame = pd.DataFrame([row])
        combined = pd.concat([history.tail(24), frame], ignore_index=True)
        engineered = engineer_features(combined)
        x = engineered[[c for c in metrics["features"] if c in engineered.columns]].iloc[[-1]]
        pred = float(model.predict(x)[0])
        future.append({
            "step": step,
            "datetime": row["datetime"],
            "predicted_aqi": max(0, min(500, round(pred, 1)))
        })
        last = row
    return pd.DataFrame(future), metrics

def isolation_forest_analysis(df):
    data = df[["humidity","no","no2","co","so2","pm25","pm10","o3","temperature"]].copy()
    data = data.replace([np.inf,-np.inf], np.nan).dropna()
    if len(data) < 20:
        raise ValueError("At least 20 rows are needed for anomaly detection.")
    model = IsolationForest(n_estimators=200, contamination=.05, random_state=42)
    model.fit(data)
    data["anomaly_score"] = model.decision_function(data)
    data["is_anomaly"] = model.predict(data) == -1
    return model, data
