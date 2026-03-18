"""
Surrogate model for fast simulation approximation.
Uses a trained regression model to quickly estimate simulation outcomes
without running the full physics-based simulation.
"""

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from backend.utils.logger import get_logger

logger = get_logger(__name__)

_surrogate_models = {}


def get_flood_surrogate() -> GradientBoostingRegressor:
    """Get or train the flood simulation surrogate model."""
    if "flood" in _surrogate_models:
        return _surrogate_models["flood"]
    model = _train_flood_surrogate()
    _surrogate_models["flood"] = model
    return model


def get_earthquake_surrogate() -> GradientBoostingRegressor:
    """Get or train the earthquake simulation surrogate model."""
    if "earthquake" in _surrogate_models:
        return _surrogate_models["earthquake"]
    model = _train_earthquake_surrogate()
    _surrogate_models["earthquake"] = model
    return model


def predict_flood_impact(rainfall_mm: float, duration_hours: float,
                           curve_number: float, city_elevation_mean: float) -> dict:
    """
    Quickly estimate flood impact without full simulation.

    Args:
        rainfall_mm: Rainfall amount (50-300mm)
        duration_hours: Storm duration (1-24h)
        curve_number: SCS curve number (60-95)
        city_elevation_mean: Mean city elevation (m)

    Returns:
        Estimated impact metrics
    """
    model = get_flood_surrogate()
    X = np.array([[rainfall_mm, duration_hours, curve_number, city_elevation_mean]])
    prediction = model.predict(X)[0]
    affected_pct = min(100, max(0, prediction))
    return {
        "estimated_affected_area_pct": round(float(affected_pct), 1),
        "estimated_buildings_at_risk_pct": round(float(affected_pct * 0.7), 1),
        "estimated_roads_blocked_pct": round(float(affected_pct * 0.4), 1),
        "confidence": "approximate",
        "method": "surrogate_model",
    }


def predict_earthquake_impact(magnitude: float, depth_km: float,
                                distance_to_center_km: float) -> dict:
    """
    Quickly estimate earthquake impact without full simulation.

    Args:
        magnitude: Earthquake magnitude (4-9)
        depth_km: Earthquake depth (5-50km)
        distance_to_center_km: Distance from city center to epicenter

    Returns:
        Estimated impact metrics
    """
    model = get_earthquake_surrogate()
    X = np.array([[magnitude, depth_km, distance_to_center_km]])
    prediction = model.predict(X)[0]
    affected_pct = min(100, max(0, prediction))
    return {
        "estimated_buildings_damaged_pct": round(float(affected_pct), 1),
        "estimated_roads_blocked_pct": round(float(affected_pct * 0.3), 1),
        "estimated_max_pga_g": round(float(_estimate_pga(magnitude, depth_km, distance_to_center_km)), 4),
        "confidence": "approximate",
        "method": "surrogate_model",
    }


def _train_flood_surrogate() -> GradientBoostingRegressor:
    """Train a surrogate model for flood simulation."""
    logger.info("Training flood surrogate model...")
    rng = np.random.RandomState(42)
    n = 500
    rainfall = rng.uniform(50, 300, n)
    duration = rng.uniform(1, 24, n)
    cn = rng.uniform(60, 95, n)
    elevation = rng.uniform(5, 50, n)
    s_mm = (25400 / cn) - 254
    ia = 0.2 * s_mm
    runoff = np.where(rainfall > ia, ((rainfall - ia) ** 2) / (rainfall - ia + s_mm), 0)
    affected = (runoff / rainfall.clip(1)) * 100 * (1 - elevation / 100).clip(0)
    affected += rng.normal(0, 3, n)
    affected = affected.clip(0, 100)
    X = np.column_stack([rainfall, duration, cn, elevation])
    model = GradientBoostingRegressor(n_estimators=50, max_depth=4, random_state=42)
    model.fit(X, affected)
    logger.info("Flood surrogate model trained")
    return model


def _train_earthquake_surrogate() -> GradientBoostingRegressor:
    """Train a surrogate model for earthquake simulation."""
    logger.info("Training earthquake surrogate model...")
    rng = np.random.RandomState(42)
    n = 500
    magnitude = rng.uniform(4, 9, n)
    depth = rng.uniform(5, 50, n)
    distance = rng.uniform(0, 50, n)
    r_hyp = np.sqrt(distance ** 2 + depth ** 2).clip(1)
    pga = 10 ** (0.527 * (magnitude - 6) - 1.039 * np.log10(r_hyp) - 0.0033 * r_hyp - 1.301)
    affected = pga * 200
    affected += rng.normal(0, 5, n)
    affected = affected.clip(0, 100)
    X = np.column_stack([magnitude, depth, distance])
    model = GradientBoostingRegressor(n_estimators=50, max_depth=4, random_state=42)
    model.fit(X, affected)
    logger.info("Earthquake surrogate model trained")
    return model


def _estimate_pga(magnitude: float, depth_km: float, distance_km: float) -> float:
    """Quick PGA estimate using attenuation formula."""
    r_hyp = max(1.0, np.sqrt(distance_km ** 2 + depth_km ** 2))
    log_pga = 0.527 * (magnitude - 6) - 1.039 * np.log10(r_hyp) - 0.0033 * r_hyp - 1.301
    return min(3.0, max(0.0, 10 ** log_pga))
