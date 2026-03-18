"""
AI damage predictor using XGBoost.
Auto-trains on synthetic data on first run if no saved model exists.
Predicts building damage probability from building and hazard features.
"""

import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from backend.utils.logger import get_logger
from backend.config import MODEL_DIR

logger = get_logger(__name__)

_model = None
_feature_columns = [
    "flood_depth", "pga_g", "building_age", "floors",
    "material_code", "soil_code", "floor_area", "height"
]

MATERIAL_CODES = {
    "reinforced_concrete": 0, "masonry": 1, "steel": 2, "wood": 3,
}
SOIL_CODES = {
    "rock": 0, "stiff_soil": 1, "soft_soil": 2, "fill": 3,
}
MODEL_PATH = MODEL_DIR / "damage_model.json"


def get_model():
    """Get or train the damage prediction model."""
    global _model
    if _model is not None:
        return _model
    if MODEL_PATH.exists():
        logger.info(f"Loading saved damage model from {MODEL_PATH}")
        import xgboost as xgb
        _model = xgb.XGBClassifier()
        _model.load_model(str(MODEL_PATH))
        return _model
    logger.info("No saved model found. Training new damage prediction model...")
    _model = train_damage_model()
    return _model


def train_damage_model(n_samples: int = 5000) -> object:
    """Train an XGBoost damage classifier on synthetic data."""
    global _model
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    logger.info(f"Generating {n_samples} synthetic training samples...")
    X, y = _generate_training_data(n_samples)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        objective="multi:softmax",
        num_class=5,
        random_state=42,
        eval_metric="mlogloss",
        verbosity=0,
    )
    logger.info("Training XGBoost damage classifier...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"Model accuracy: {accuracy:.3f}")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save_model(str(MODEL_PATH))
    logger.info(f"Model saved to {MODEL_PATH}")
    _model = model
    return model


def predict_damage(buildings: list, flood_depth: float = 0.0,
                     pga_g: float = 0.0) -> list:
    """
    Predict damage for a list of buildings using the trained model.

    Args:
        buildings: List of building property dicts
        flood_depth: Default flood depth if not per-building
        pga_g: Default PGA in g if not per-building

    Returns:
        List of predictions with damage class and probability
    """
    model = get_model()
    if not buildings:
        return []
    features = []
    for bldg in buildings:
        fd = bldg.get("flood_depth", flood_depth)
        pga = bldg.get("pga_g", pga_g)
        age = 2024 - bldg.get("construction_year", 2000)
        floors = bldg.get("floors", 1)
        mat = MATERIAL_CODES.get(bldg.get("material", "masonry"), 1)
        soil = SOIL_CODES.get(bldg.get("soil_type", "stiff_soil"), 1)
        area = bldg.get("floor_area", 100.0)
        height = bldg.get("height", floors * 3.0)
        features.append([fd, pga, age, floors, mat, soil, area, height])
    X = np.array(features, dtype=np.float32)
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    damage_labels = ["none", "slight", "moderate", "extensive", "complete"]
    results = []
    for i, bldg in enumerate(buildings):
        pred_class = int(predictions[i])
        results.append({
            "id": bldg.get("id", f"bldg_{i}"),
            "predicted_damage": damage_labels[pred_class],
            "damage_probabilities": {
                label: round(float(probabilities[i][j]), 3)
                for j, label in enumerate(damage_labels)
            },
            "confidence": round(float(np.max(probabilities[i])), 3),
        })
    return results


def _generate_training_data(n_samples: int = 5000) -> tuple:
    """Generate synthetic training data for the damage model."""
    rng = np.random.RandomState(42)
    flood_depth = rng.exponential(0.5, n_samples).clip(0, 5.0)
    pga_g = rng.exponential(0.1, n_samples).clip(0, 2.0)
    building_age = rng.randint(1, 80, n_samples).astype(float)
    floors = rng.choice([1, 2, 3, 4, 5, 6, 8, 10, 15], n_samples)
    material_code = rng.randint(0, 4, n_samples).astype(float)
    soil_code = rng.randint(0, 4, n_samples).astype(float)
    floor_area = rng.uniform(50, 5000, n_samples)
    height = floors * 3.0
    X = np.column_stack([
        flood_depth, pga_g, building_age, floors,
        material_code, soil_code, floor_area, height
    ])
    hazard_score = (flood_depth * 2.0 + pga_g * 10.0 +
                    building_age * 0.02 + soil_code * 0.3 -
                    material_code * 0.2)
    noise = rng.normal(0, 0.5, n_samples)
    hazard_score += noise
    y = np.zeros(n_samples, dtype=int)
    y[hazard_score > 1.0] = 1
    y[hazard_score > 2.0] = 2
    y[hazard_score > 3.5] = 3
    y[hazard_score > 5.0] = 4
    return X.astype(np.float32), y
