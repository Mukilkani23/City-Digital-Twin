"""Tests for earthquake simulator."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np


def test_earthquake_simulation_returns_valid_results():
    """Test earthquake simulation returns valid structure."""
    from backend.data.city_loader import load_city
    from backend.simulation.earthquake_simulator import simulate_earthquake
    city = load_city("mumbai")
    result = simulate_earthquake(city, magnitude=6.5, depth_km=15.0)
    assert "building_damage" in result
    assert "pga_grid" in result
    assert "statistics" in result
    assert "damage_summary" in result
    assert result["statistics"]["magnitude"] == 6.5


def test_pga_decreases_with_distance():
    """Test PGA values decrease with distance from epicenter."""
    from backend.simulation.earthquake_simulator import _calculate_pga_vectorized
    distances = np.array([1.0, 5.0, 10.0, 50.0, 100.0])
    pga_values = _calculate_pga_vectorized(7.0, distances, 10.0)
    for i in range(len(pga_values) - 1):
        assert pga_values[i] >= pga_values[i + 1], "PGA should decrease with distance"


def test_damage_states_are_valid():
    """Test earthquake damage states are valid HAZUS categories."""
    from backend.data.city_loader import load_city
    from backend.simulation.earthquake_simulator import simulate_earthquake
    city = load_city("mumbai")
    result = simulate_earthquake(city, magnitude=7.0, depth_km=10.0)
    valid_states = {"none", "slight", "moderate", "extensive", "complete"}
    for bldg in result["building_damage"]:
        assert bldg["damage_state"] in valid_states
        assert bldg["pga_g"] >= 0


def test_higher_magnitude_causes_more_damage():
    """Test that higher magnitude causes more damage."""
    from backend.data.city_loader import load_city
    from backend.simulation.earthquake_simulator import simulate_earthquake
    city = load_city("mumbai")
    result_low = simulate_earthquake(city, magnitude=4.5, depth_km=20.0)
    result_high = simulate_earthquake(city, magnitude=8.0, depth_km=20.0)
    damaged_low = sum(1 for b in result_low["building_damage"] if b["damage_state"] != "none")
    damaged_high = sum(1 for b in result_high["building_damage"] if b["damage_state"] != "none")
    assert damaged_high >= damaged_low


if __name__ == "__main__":
    test_earthquake_simulation_returns_valid_results()
    test_pga_decreases_with_distance()
    test_damage_states_are_valid()
    test_higher_magnitude_causes_more_damage()
    print("All earthquake simulator tests passed!")
