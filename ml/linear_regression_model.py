"""
Linear Regression Baseline Model for Air Quality & PM2.5 Prediction.
"""
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import numpy as np

class LinearAirQualityModel:
    def __init__(self, alpha: float = 1.0):
        self.model_name = "Linear Regression (Ridge)"
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("regressor", Ridge(alpha=alpha, random_state=42))
        ])
        self.is_fitted = False
        
    def fit(self, X: np.ndarray, y: np.ndarray):
        self.pipeline.fit(X, y)
        self.is_fitted = True
        return self
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet.")
        preds = self.pipeline.predict(X)
        # Air quality / pollutant values cannot be negative
        return np.clip(preds, a_min=0.0, a_max=None)
        
    def get_feature_coefficients(self, feature_names: list) -> dict:
        if not self.is_fitted:
            return {}
        coefs = self.pipeline.named_steps["regressor"].coef_
        return dict(zip(feature_names, coefs))
