"""
XGBoost Gradient Boosting Regressor for Air Quality & PM2.5 Prediction.
"""
from xgboost import XGBRegressor
import numpy as np

class XGBoostAirQualityModel:
    def __init__(self, n_estimators: int = 150, learning_rate: float = 0.05, max_depth: int = 6, random_state: int = 42):
        self.model_name = "XGBoost Regressor"
        self.model = XGBRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=random_state,
            n_jobs=-1
        )
        self.is_fitted = False
        
    def fit(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y)
        self.is_fitted = True
        return self
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet.")
        preds = self.model.predict(X)
        return np.clip(preds, a_min=0.0, a_max=None)
        
    def get_feature_importances(self, feature_names: list) -> dict:
        if not self.is_fitted:
            return {}
        importances = self.model.feature_importances_
        return dict(zip(feature_names, importances))
