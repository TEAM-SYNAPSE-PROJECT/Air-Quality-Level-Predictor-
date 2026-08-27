"""
Train the Deep Learning LSTM model.

Run from the project root:
    python -m dl.train_lstm

Artifacts are saved under models/deep_learning/.
"""

from __future__ import annotations

import os
import pandas as pd

from dl.lstm_model import AirQualityLSTM, LSTMArtifacts


DATA_PATH = "data/processed/cleaned_air_quality.csv"
OUTPUT_DIR = "models/deep_learning"


def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"{DATA_PATH} was not found. Run the existing ML training/data pipeline first."
        )

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(DATA_PATH)

    # The dataset is hourly in the current project. Sorting protects the
    # temporal order before the chronological split.
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    model = AirQualityLSTM(lookback=24)
    metrics = model.train(
        df,
        epochs=35,
        batch_size=32,
        validation_fraction=0.15,
    )

    artifacts = LSTMArtifacts(
        model_path=f"{OUTPUT_DIR}/aqi_lstm.keras",
        feature_scaler_path=f"{OUTPUT_DIR}/feature_scaler.pkl",
        target_scaler_path=f"{OUTPUT_DIR}/target_scaler.pkl",
        metadata_path=f"{OUTPUT_DIR}/metadata.json",
    )
    model.save(artifacts, metrics)

    print("\n=== Deep Learning Training Complete ===")
    print(f"Model: LSTM")
    print(f"RMSE: {metrics['metrics']['rmse']:.3f}")
    print(f"MAE : {metrics['metrics']['mae']:.3f}")
    print(f"R²  : {metrics['metrics']['r2']:.4f}")
    print(f"Saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
