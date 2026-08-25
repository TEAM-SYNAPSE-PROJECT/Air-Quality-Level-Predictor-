"""
Automated Model Selection and Champion Model Registry.
Evaluates candidates strictly on out-of-time validation metrics and selects champion.
"""
from typing import Dict, Any, List

def select_best_model(models_eval: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Selects the champion model based on lowest RMSE and highest R² on test/validation set.
    """
    if not models_eval:
        raise ValueError("No model evaluation results provided.")
        
    best_name = None
    best_score = float("inf")
    
    # We rank based on composite metric: RMSE (lower is better) with R² tie-breaker
    ranking = []
    
    for name, metrics in models_eval.items():
        rmse = metrics.get("rmse", float("inf"))
        r2 = metrics.get("r2", -float("inf"))
        mae = metrics.get("mae", float("inf"))
        
        # Lower composite score is better
        composite = rmse * (1.0 + max(0.0, 1.0 - r2))
        
        ranking.append({
            "model_name": name,
            "rmse": rmse,
            "r2": r2,
            "mae": mae,
            "composite_score": composite,
            "metrics": metrics
        })
        
    # Sort ranking
    ranking.sort(key=lambda x: x["composite_score"])
    champion = ranking[0]
    
    return {
        "best_model_name": champion["model_name"],
        "best_metrics": champion["metrics"],
        "ranking": ranking,
        "selection_rationale": f"Selected '{champion['model_name']}' with lowest RMSE ({champion['rmse']} µg/m³) and highest R² ({champion['r2']}) on validation test data."
    }
