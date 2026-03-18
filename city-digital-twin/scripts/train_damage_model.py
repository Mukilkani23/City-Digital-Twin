"""
Train the XGBoost damage prediction model.
Generates synthetic training data and saves the trained model.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.ml.damage_predictor import train_damage_model, predict_damage, MODEL_PATH


def main():
    """Train and evaluate the damage prediction model."""
    print("=" * 60)
    print("Training Damage Prediction Model")
    print("=" * 60)

    print("\nStep 1: Generating synthetic training data...")
    print("Step 2: Training XGBoost classifier...")

    model = train_damage_model(n_samples=5000)

    print(f"\nModel saved to: {MODEL_PATH}")
    print(f"Model type: {type(model).__name__}")

    print("\nStep 3: Testing predictions on sample buildings...")
    test_buildings = [
        {"flood_depth": 0.5, "pga_g": 0.0, "construction_year": 1980,
         "floors": 3, "material": "masonry", "soil_type": "soft_soil",
         "floor_area": 200, "height": 9.0, "id": "test_1"},
        {"flood_depth": 2.0, "pga_g": 0.0, "construction_year": 1965,
         "floors": 2, "material": "wood", "soil_type": "fill",
         "floor_area": 100, "height": 6.0, "id": "test_2"},
        {"flood_depth": 0.0, "pga_g": 0.3, "construction_year": 2015,
         "floors": 10, "material": "reinforced_concrete", "soil_type": "rock",
         "floor_area": 1000, "height": 30.0, "id": "test_3"},
    ]

    predictions = predict_damage(test_buildings)
    print("\nSample Predictions:")
    print("-" * 50)
    for pred in predictions:
        print(f"  {pred['id']}: {pred['predicted_damage']} "
              f"(confidence: {pred['confidence']:.2f})")

    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
