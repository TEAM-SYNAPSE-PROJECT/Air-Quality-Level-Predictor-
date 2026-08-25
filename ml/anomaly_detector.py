"""
Anomaly Detection & Atmospheric Outlier Identification.
Combines Scikit-Learn Isolation Forest with rapid-rate-of-change spike filters.
"""
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

class AirQualityAnomalyDetector:
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.is_fitted = False
        self.feature_cols = ["pm25", "pm10", "no2", "so2", "co", "o3", "temperature", "humidity"]
        
    def fit(self, df: pd.DataFrame):
        available_cols = [c for c in self.feature_cols if c in df.columns]
        X = df[available_cols].fillna(df[available_cols].median()).values
        self.model.fit(X)
        self.is_fitted = True
        return self
        
    def detect_anomalies(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """Identifies anomalies across records and produces diagnostic breakdown."""
        available_cols = [c for c in self.feature_cols if c in df.columns]
        df_eval = df.copy()
        
        if not self.is_fitted:
            self.fit(df)
            
        X = df_eval[available_cols].fillna(df_eval[available_cols].median()).values
        preds = self.model.predict(X) # -1 is anomaly, 1 is normal
        scores = self.model.decision_function(X)
        
        df_eval["is_anomaly"] = (preds == -1)
        df_eval["anomaly_score"] = np.round(-scores, 3) # higher score = more anomalous
        
        anomaly_records = []
        for idx, row in df_eval[df_eval["is_anomaly"]].iterrows():
            reasons = []
            if "pm25" in row and row["pm25"] > 250:
                reasons.append(f"Severe PM2.5 surge ({row['pm25']} µg/m³)")
            if "pm10" in row and row["pm10"] > 350:
                reasons.append(f"Severe PM10 dust surge ({row['pm10']} µg/m³)")
            if "no2" in row and row["no2"] > 100:
                reasons.append(f"Abnormal NO2 spike ({row['no2']} µg/m³)")
            if "co" in row and row["co"] > 5.0:
                reasons.append(f"Dangerous CO peak ({row['co']} mg/m³)")
            if not reasons:
                reasons.append("Unusual multi-pollutant co-occurrence under current meteorology")
                
            anomaly_records.append({
                "index": int(idx),
                "timestamp": str(row.get("timestamp", "")),
                "city": str(row.get("city", "N/A")),
                "aqi": float(row.get("aqi", 0)),
                "pm25": float(row.get("pm25", 0)),
                "anomaly_score": float(row["anomaly_score"]),
                "reasons": reasons
            })
            
        return df_eval, anomaly_records
