"""
End-to-End Machine Learning Training Pipeline.
Executes chronological time-based split, trains Linear Regression, Random Forest,
and XGBoost, computes benchmark metrics, selects champion model, and serializes artifacts.
"""
import os
import json
import pickle
import pandas as pd
import numpy as np
from datetime import datetime

from ml.data_validation import run_data_validation
from ml.data_cleaning import clean_air_quality_dataset
from ml.feature_engineering import build_features
from ml.linear_regression_model import LinearAirQualityModel
from ml.random_forest_model import RandomForestAirQualityModel
from ml.xgboost_model import XGBoostAirQualityModel
from ml.model_evaluation import evaluate_predictions
from ml.model_selector import select_best_model
from ml.anomaly_detector import AirQualityAnomalyDetector

def train_and_evaluate_all():
    os.makedirs("models", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    print("=== STEP 1: Loading & Validating Data ===")
    data_path = "data/sample_air_quality.csv"
    if not os.path.exists(data_path):
        from scripts.generate_datasets import generate_datasets
        generate_datasets()
        
    df_raw = pd.read_csv(data_path)
    val_report = run_data_validation(df_raw)
    print(f"Validation Status: {val_report['status']}, Records: {val_report['total_records']}")
    
    print("=== STEP 2: Data Cleaning & Preprocessing ===")
    df_clean, clean_meta = clean_air_quality_dataset(df_raw)
    df_clean.to_csv("data/processed/cleaned_air_quality.csv", index=False)
    
    print("=== STEP 3: Feature Engineering (No Leakage) ===")
    target_col = "pm25"
    df_features, feature_cols = build_features(df_clean, target_col=target_col)
    df_features.to_csv("data/processed/featured_air_quality.csv", index=False)
    print(f"Generated {len(feature_cols)} features for {len(df_features)} records.")
    
    print("=== STEP 4: Chronological Time-Based Split ===")
    # 70% Train, 15% Validation, 15% Test (Strict time order)
    n = len(df_features)
    train_end = int(n * 0.70)
    val_end = int(n * 0.85)
    
    train_df = df_features.iloc[:train_end]
    val_df = df_features.iloc[train_end:val_end]
    test_df = df_features.iloc[val_end:]
    
    X_train = train_df[feature_cols].values
    y_train = train_df[target_col].values
    
    X_val = val_df[feature_cols].values
    y_val = val_df[target_col].values
    
    X_test = test_df[feature_cols].values
    y_test = test_df[target_col].values
    
    print(f"Train size: {len(X_train)}, Validation size: {len(X_val)}, Test size: {len(X_test)}")
    
    print("=== STEP 5: Training Regression Models ===")
    models = {
        "Linear Regression": LinearAirQualityModel(alpha=10.0),
        "Random Forest": RandomForestAirQualityModel(n_estimators=120, max_depth=10),
        "XGBoost": XGBoostAirQualityModel(n_estimators=150, learning_rate=0.04, max_depth=5)
    }
    
    evaluation_results = {}
    test_predictions = {}
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        
        # Evaluate on out-of-time Test set
        y_pred = model.predict(X_test)
        metrics = evaluate_predictions(y_test, y_pred)
        evaluation_results[name] = metrics
        test_predictions[name] = [float(p) for p in y_pred[:100]] # sample for visualization
        print(f"{name} -> RMSE: {metrics['rmse']:.2f}, MAE: {metrics['mae']:.2f}, R²: {metrics['r2']:.4f}")
        
    print("=== STEP 6: Champion Model Selection ===")
    selection_res = select_best_model(evaluation_results)
    best_name = selection_res["best_model_name"]
    best_model = models[best_name]
    print(f"Selected Champion: {best_name}")
    print(f"Rationale: {selection_res['selection_rationale']}")
    
    print("=== STEP 7: Training Anomaly Detector ===")
    anomaly_detector = AirQualityAnomalyDetector(contamination=0.04)
    anomaly_detector.fit(df_clean)
    
    # Save artifacts
    print("=== STEP 8: Serializing Models & Metadata ===")
    with open("models/best_model.pkl", "wb") as f:
        pickle.dump(best_model, f)
    with open("models/linear_model.pkl", "wb") as f:
        pickle.dump(models["Linear Regression"], f)
    with open("models/rf_model.pkl", "wb") as f:
        pickle.dump(models["Random Forest"], f)
    with open("models/xgb_model.pkl", "wb") as f:
        pickle.dump(models["XGBoost"], f)
    with open("models/anomaly_detector.pkl", "wb") as f:
        pickle.dump(anomaly_detector, f)
        
    metadata = {
        "trained_at": datetime.now().isoformat(),
        "target_variable": target_col,
        "feature_count": len(feature_cols),
        "feature_names": feature_cols,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "models_evaluated": list(models.keys()),
        "champion_model": best_name,
        "evaluation_metrics": evaluation_results,
        "selection_ranking": selection_res["ranking"],
        "test_actuals_sample": [float(y) for y in y_test[:100]],
        "test_predictions_sample": test_predictions,
        "validation_report": {
            "status": val_report["status"],
            "total_records": val_report["total_records"]
        }
    }
    
    with open("models/model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    print("Training pipeline finished successfully!")
    return metadata

if __name__ == "__main__":
    train_and_evaluate_all()
