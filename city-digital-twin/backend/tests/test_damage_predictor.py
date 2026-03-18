"""Tests for damage predictor ML model."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np


def test_model_trains_successfully():
    """Test that the XGBoost model trains without errors."""
    from backend.ml.damage_predictor import train_damage_model
    model = train_damage_model(n_samples=500)
    assert model is not None


def test_predict_damage_returns_valid_results():
    """Test damage prediction returns valid predictions."""
    from backend.ml.damage_predictor import predict_damage
    buildings = [
        {"flood_depth": 1.0, "pga_g": 0.0, "construction_year": 1990,
         "floors": 3, "material": "masonry", "soil_type": "soft_soil",
         "floor_area": 200, "height": 9.0, "id": "test_1"},
        {"flood_depth": 0.0, "pga_g": 0.5, "construction_year": 2010,
         "floors": 10, "material": "reinforced_concrete", "soil_type": "rock",
         "floor_area": 1000, "height": 30.0, "id": "test_2"},
    ]
    results = predict_damage(buildings)
    assert len(results) == 2
    valid_states = {"none", "slight", "moderate", "extensive", "complete"}
    for r in results:
        assert r["predicted_damage"] in valid_states
        assert 0 <= r["confidence"] <= 1
        assert sum(r["damage_probabilities"].values()) > 0.99


def test_risk_scorer():
    """Test risk score calculation."""
    from backend.ml.risk_scorer import calculate_risk_scores
    buildings = [
        {"id": "b1", "flood_depth": 2.0, "damage_state": "extensive",
         "construction_year": 1970, "material": "wood", "soil_type": "fill",
         "floors": 2, "building_type": "residential"},
    ]
    results = calculate_risk_scores(buildings, "flood")
    assert len(results) == 1
    assert 0 <= results[0]["risk_score"] <= 100
    assert results[0]["risk_level"] in ("low", "moderate", "high", "very_high", "critical")
    assert len(results[0]["risk_factors"]) > 0


def test_empty_input():
    """Test that empty input returns empty results."""
    from backend.ml.damage_predictor import predict_damage
    from backend.ml.risk_scorer import calculate_risk_scores
    assert predict_damage([]) == []
    assert calculate_risk_scores([]) == []


if __name__ == "__main__":
    test_model_trains_successfully()
    test_predict_damage_returns_valid_results()
    test_risk_scorer()
    test_empty_input()
    print("All damage predictor tests passed!")
