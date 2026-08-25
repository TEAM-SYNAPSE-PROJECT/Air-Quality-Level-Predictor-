"""
Model Evaluation & Benchmark Framework.
Computes standard regression metrics (MAE, RMSE, R², MAPE) and residual diagnostics.
"""
from typing import Dict, Any
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """Computes comprehensive statistical performance metrics."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    
    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))
    
    # Non-zero safe MAPE calculation
    non_zero_mask = y_true > 1.0
    if np.any(non_zero_mask):
        mape = float(np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100.0)
    else:
        mape = 0.0
        
    residuals = y_true - y_pred
    max_err = float(np.max(np.abs(residuals)))
    
    return {
        "mae": round(mae, 3),
        "mse": round(mse, 3),
        "rmse": round(rmse, 3),
        "r2": round(r2, 4),
        "mape": round(mape, 2),
        "max_error": round(max_err, 3),
        "mean_residual": round(float(np.mean(residuals)), 3),
        "std_residual": round(float(np.std(residuals)), 3)
    }
