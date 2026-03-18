"""
Weather data loader.
Provides synthetic weather scenarios for disaster simulation
since real-time weather APIs may not be available.
"""

import numpy as np
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def get_weather_scenario(city_name: str, scenario_type: str = "monsoon") -> dict:
    """Return a weather scenario for simulation input."""
    scenarios = {
        "monsoon": {
            "rainfall_mm": 150.0,
            "duration_hours": 6.0,
            "temperature_c": 28.0,
            "humidity_pct": 92.0,
            "wind_speed_kmh": 45.0,
            "description": "Heavy monsoon rainfall event"
        },
        "cyclone": {
            "rainfall_mm": 250.0,
            "duration_hours": 12.0,
            "temperature_c": 26.0,
            "humidity_pct": 95.0,
            "wind_speed_kmh": 120.0,
            "description": "Severe cyclone with heavy rain"
        },
        "cloudburst": {
            "rainfall_mm": 200.0,
            "duration_hours": 2.0,
            "temperature_c": 30.0,
            "humidity_pct": 88.0,
            "wind_speed_kmh": 30.0,
            "description": "Sudden intense cloudburst"
        },
        "moderate": {
            "rainfall_mm": 80.0,
            "duration_hours": 8.0,
            "temperature_c": 27.0,
            "humidity_pct": 80.0,
            "wind_speed_kmh": 20.0,
            "description": "Moderate sustained rainfall"
        },
    }
    scenario = scenarios.get(scenario_type, scenarios["monsoon"]).copy()
    scenario["city"] = city_name
    scenario["scenario_type"] = scenario_type
    logger.info(f"Weather scenario for {city_name}: {scenario['description']}")
    return scenario


def get_historical_rainfall(city_name: str, years: int = 10) -> dict:
    """Generate synthetic historical rainfall data for a city."""
    rng = np.random.RandomState(sum(ord(c) for c in city_name))
    city_baselines = {
        "mumbai": {"annual_mean": 2400, "peak_month": 7},
        "chennai": {"annual_mean": 1400, "peak_month": 11},
        "kolkata": {"annual_mean": 1600, "peak_month": 7},
        "delhi": {"annual_mean": 800, "peak_month": 8},
        "jakarta": {"annual_mean": 1800, "peak_month": 1},
    }
    baseline = city_baselines.get(city_name.lower(), {"annual_mean": 1200, "peak_month": 7})
    monthly_dist = np.zeros(12)
    for m in range(12):
        offset = abs(m - (baseline["peak_month"] - 1))
        offset = min(offset, 12 - offset)
        monthly_dist[m] = np.exp(-0.3 * offset)
    monthly_dist = monthly_dist / monthly_dist.sum() * baseline["annual_mean"]
    yearly_data = []
    for y in range(years):
        monthly = monthly_dist * rng.uniform(0.7, 1.3, 12)
        yearly_data.append({
            "year": 2014 + y,
            "monthly_mm": [round(float(v), 1) for v in monthly],
            "annual_mm": round(float(np.sum(monthly)), 1),
        })
    return {
        "city": city_name,
        "baseline_annual_mm": baseline["annual_mean"],
        "yearly_data": yearly_data,
    }


def get_soil_moisture(city_name: str, season: str = "wet") -> float:
    """Return estimated antecedent soil moisture condition."""
    moisture_map = {
        ("mumbai", "wet"): 0.85,
        ("mumbai", "dry"): 0.35,
        ("chennai", "wet"): 0.80,
        ("chennai", "dry"): 0.30,
        ("kolkata", "wet"): 0.82,
        ("kolkata", "dry"): 0.40,
        ("delhi", "wet"): 0.70,
        ("delhi", "dry"): 0.25,
        ("jakarta", "wet"): 0.88,
        ("jakarta", "dry"): 0.45,
    }
    return moisture_map.get((city_name.lower(), season), 0.60)
