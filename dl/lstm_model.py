"""
LSTM-based deep-learning forecaster for PM2.5.

The model learns from the previous 24 hourly observations and predicts
the next PM2.5 value. It is intentionally kept separate from the existing
Random Forest/XGBoost pipeline so the current application keeps working.
"""

from __future__ import annotations

import json
import os
import pickle
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


DEFAULT_FEATURES = [
    "pm25", "pm10", "no2", "so2", "co", "o3",
    "temperature", "humidity", "wind_speed", "pressure",
    "hour_sin", "hour_cos",
]


def _tensorflow():
    """Lazy TensorFlow import so the rest of the app can run without DL."""
    try:
        import tensorflow as tf
        return tf
    except ImportError as exc:
        raise ImportError(
            "TensorFlow is required for the LSTM module. "
            "Install the project requirements first."
        ) from exc


@dataclass
class LSTMArtifacts:
    model_path: str
    feature_scaler_path: str
    target_scaler_path: str
    metadata_path: str


class AirQualityLSTM:
    """Train, evaluate, save, load and forecast with an LSTM network."""

    def __init__(self, lookback: int = 24, features: Optional[List[str]] = None):
        self.lookback = lookback
        self.features = features or DEFAULT_FEATURES.copy()
        self.model = None
        self.feature_scaler = None
        self.target_scaler = None

    @staticmethod
    def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["timestamp"] = pd.to_datetime(out["timestamp"])
        out = out.sort_values("timestamp").reset_index(drop=True)
        out["hour_sin"] = np.sin(2 * np.pi * out["timestamp"].dt.hour / 24.0)
        out["hour_cos"] = np.cos(2 * np.pi * out["timestamp"].dt.hour / 24.0)
        return out

    def make_sequences(self, df: pd.DataFrame):
        from sklearn.preprocessing import StandardScaler

        data = self.add_time_features(df)
        missing = [c for c in self.features if c not in data.columns]
        if missing:
            raise ValueError(f"Missing LSTM features: {missing}")

        clean = data[self.features].replace([np.inf, -np.inf], np.nan).dropna()
        if len(clean) <= self.lookback:
            raise ValueError(
                f"Need more than {self.lookback} valid hourly records; "
                f"only {len(clean)} are available."
            )

        X_raw = clean.values.astype("float32")
        y_raw = clean["pm25"].values.astype("float32").reshape(-1, 1)

        self.feature_scaler = StandardScaler()
        self.target_scaler = StandardScaler()

        # Scalers are fitted only on the training portion by train().
        return X_raw, y_raw

    def build_model(self):
        tf = _tensorflow()
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(self.lookback, len(self.features))),
            tf.keras.layers.LSTM(64, return_sequences=True),
            tf.keras.layers.Dropout(0.20),
            tf.keras.layers.LSTM(32),
            tf.keras.layers.Dropout(0.15),
            tf.keras.layers.Dense(16, activation="relu"),
            tf.keras.layers.Dense(1),
        ])
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss="mse",
            metrics=[
                tf.keras.metrics.MeanAbsoluteError(name="mae"),
                tf.keras.metrics.RootMeanSquaredError(name="rmse"),
            ],
        )
        self.model = model
        return model

    def train(self, df: pd.DataFrame, epochs: int = 35, batch_size: int = 32,
              validation_fraction: float = 0.15) -> Dict:
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

        X_raw, y_raw = self.make_sequences(df)
        n = len(X_raw)
        train_end = int(n * (1.0 - validation_fraction))

        self.feature_scaler.fit(X_raw[:train_end])
        self.target_scaler.fit(y_raw[:train_end])

        X_scaled = self.feature_scaler.transform(X_raw).astype("float32")
        y_scaled = self.target_scaler.transform(y_raw).astype("float32").ravel()

        X_seq, y_seq, positions = [], [], []
        for i in range(self.lookback, len(X_scaled)):
            X_seq.append(X_scaled[i - self.lookback:i])
            y_seq.append(y_scaled[i])
            positions.append(i)

        X_seq = np.asarray(X_seq, dtype="float32")
        y_seq = np.asarray(y_seq, dtype="float32")
        positions = np.asarray(positions)

        train_mask = positions < train_end
        test_mask = ~train_mask

        X_train, y_train = X_seq[train_mask], y_seq[train_mask]
        X_test, y_test = X_seq[test_mask], y_seq[test_mask]

        if len(X_train) == 0 or len(X_test) == 0:
            raise ValueError("Not enough data for chronological train/test split.")

        self.build_model()

        tf = _tensorflow()
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=7, restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss", factor=0.5, patience=3, min_lr=1e-5
            ),
        ]

        history = self.model.fit(
            X_train, y_train,
            validation_split=0.15,
            epochs=epochs,
            batch_size=batch_size,
            shuffle=False,
            callbacks=callbacks,
            verbose=1,
        )

        pred_scaled = self.model.predict(X_test, verbose=0).reshape(-1, 1)
        pred = self.target_scaler.inverse_transform(pred_scaled).ravel()
        actual = self.target_scaler.inverse_transform(y_test.reshape(-1, 1)).ravel()

        rmse = float(np.sqrt(mean_squared_error(actual, pred)))
        mae = float(mean_absolute_error(actual, pred))
        r2 = float(r2_score(actual, pred))

        return {
            "model": "LSTM",
            "target": "PM2.5",
            "lookback_hours": self.lookback,
            "features": self.features,
            "train_samples": int(len(X_train)),
            "test_samples": int(len(X_test)),
            "epochs_requested": epochs,
            "epochs_completed": len(history.history.get("loss", [])),
            "metrics": {"rmse": rmse, "mae": mae, "r2": r2},
        }

    def forecast(self, history_df: pd.DataFrame, horizon: int = 24) -> List[Dict]:
        if self.model is None or self.feature_scaler is None or self.target_scaler is None:
            raise RuntimeError("LSTM model and scalers must be loaded/trained first.")

        data = self.add_time_features(history_df)
        data = data.dropna(subset=self.features).copy()
        if len(data) < self.lookback:
            raise ValueError(f"At least {self.lookback} historical records are required.")

        values = data[self.features].tail(self.lookback).values.astype("float32")
        current = values.copy()
        last_time = pd.to_datetime(data["timestamp"].iloc[-1])

        results = []
        for step in range(1, horizon + 1):
            scaled_window = self.feature_scaler.transform(current)
            pred_scaled = self.model.predict(
                scaled_window[np.newaxis, :, :], verbose=0
            )[0, 0]
            pred_pm25 = float(
                self.target_scaler.inverse_transform([[pred_scaled]])[0, 0]
            )
            pred_pm25 = max(0.0, pred_pm25)

            future_time = last_time + pd.Timedelta(hours=step)
            next_row = current[-1].copy()
            next_row[0] = pred_pm25

            # Update cyclical time features for the next step.
            next_row[-2] = np.sin(2 * np.pi * future_time.hour / 24.0)
            next_row[-1] = np.cos(2 * np.pi * future_time.hour / 24.0)

            current = np.vstack([current[1:], next_row])

            results.append({
                "step": step,
                "forecast_time": future_time.strftime("%Y-%m-%d %H:%M:%S"),
                "predicted_pm25": round(pred_pm25, 2),
            })

        return results

    def save(self, artifacts: LSTMArtifacts, metadata: Dict):
        if self.model is None:
            raise RuntimeError("Nothing to save. Train the model first.")

        os.makedirs(os.path.dirname(artifacts.model_path) or ".", exist_ok=True)
        self.model.save(artifacts.model_path)

        with open(artifacts.feature_scaler_path, "wb") as f:
            pickle.dump(self.feature_scaler, f)
        with open(artifacts.target_scaler_path, "wb") as f:
            pickle.dump(self.target_scaler, f)
        with open(artifacts.metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def load(self, artifacts: LSTMArtifacts):
        tf = _tensorflow()
        self.model = tf.keras.models.load_model(artifacts.model_path)

        with open(artifacts.feature_scaler_path, "rb") as f:
            self.feature_scaler = pickle.load(f)
        with open(artifacts.target_scaler_path, "rb") as f:
            self.target_scaler = pickle.load(f)

        return self
