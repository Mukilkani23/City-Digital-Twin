"""Tests for flood simulator."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np


def test_scs_runoff_calculation():
    """Test SCS Curve Number runoff calculation."""
    from backend.simulation.rainfall_runoff import calculate_runoff_scs
    result = calculate_runoff_scs(150.0, 80.0, 6.0)
    assert result["rainfall_mm"] == 150.0
    assert result["curve_number"] == 80.0
    assert result["runoff_mm"] > 0
    assert result["runoff_mm"] < 150.0
    assert result["peak_discharge_m3s"] > 0
    assert len(result["hydrograph"]) > 0


def test_zero_rainfall_produces_no_runoff():
    """Test that zero rainfall produces no runoff."""
    from backend.simulation.rainfall_runoff import calculate_runoff_scs
    result = calculate_runoff_scs(0.0, 80.0, 6.0)
    assert result["runoff_mm"] == 0.0


def test_flood_simulation_returns_valid_geojson():
    """Test flood simulation returns valid GeoJSON."""
    from backend.data.city_loader import load_city
    from backend.simulation.flood_simulator import simulate_rainfall_flood
    city = load_city("mumbai")
    result = simulate_rainfall_flood(city, 150.0, 6.0, 80.0)
    assert "flood_zones" in result
    assert result["flood_zones"]["type"] == "FeatureCollection"
    assert "building_damage" in result
    assert "statistics" in result
    assert result["statistics"]["affected_area_km2"] >= 0


def test_bathtub_flood():
    """Test bathtub flood simulation."""
    from backend.data.city_loader import load_city
    from backend.simulation.flood_simulator import simulate_bathtub_flood
    city = load_city("mumbai")
    result = simulate_bathtub_flood(city, 5.0)
    assert "flood_zones" in result
    assert "building_damage" in result
    assert result["statistics"]["water_level_m"] == 5.0


def test_flood_damage_assessment():
    """Test that flood damage assessment produces valid states."""
    from backend.data.city_loader import load_city
    from backend.simulation.flood_simulator import simulate_rainfall_flood
    city = load_city("mumbai")
    result = simulate_rainfall_flood(city, 200.0, 6.0, 85.0)
    valid_states = {"none", "slight", "moderate", "extensive", "complete"}
    for bldg in result["building_damage"]:
        assert bldg["damage_state"] in valid_states
        assert 0 <= bldg["flood_depth"]
        assert bldg["id"] is not None


if __name__ == "__main__":
    test_scs_runoff_calculation()
    test_zero_rainfall_produces_no_runoff()
    test_flood_simulation_returns_valid_geojson()
    test_bathtub_flood()
    test_flood_damage_assessment()
    print("All flood simulator tests passed!")
