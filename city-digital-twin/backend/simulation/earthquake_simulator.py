"""
Earthquake simulator.
Calculates Peak Ground Acceleration using attenuation relationships
and applies HAZUS fragility curves for damage assessment.
"""

import numpy as np
from shapely.geometry import shape
from backend.utils.logger import get_logger
from backend.utils.geo_utils import haversine_distance_vectorized, feature_collection

logger = get_logger(__name__)

FRAGILITY_CURVES = {
    "C1": {"slight": 0.15, "moderate": 0.30, "extensive": 0.60, "complete": 1.00},
    "C2": {"slight": 0.12, "moderate": 0.25, "extensive": 0.50, "complete": 0.90},
    "C3": {"slight": 0.10, "moderate": 0.20, "extensive": 0.45, "complete": 0.85},
    "RM1": {"slight": 0.13, "moderate": 0.28, "extensive": 0.55, "complete": 0.95},
    "RM2": {"slight": 0.11, "moderate": 0.23, "extensive": 0.48, "complete": 0.88},
    "URM": {"slight": 0.08, "moderate": 0.15, "extensive": 0.35, "complete": 0.70},
    "S1": {"slight": 0.18, "moderate": 0.35, "extensive": 0.65, "complete": 1.10},
    "S2": {"slight": 0.16, "moderate": 0.32, "extensive": 0.60, "complete": 1.05},
    "W1": {"slight": 0.10, "moderate": 0.22, "extensive": 0.45, "complete": 0.80},
    "W2": {"slight": 0.09, "moderate": 0.20, "extensive": 0.40, "complete": 0.75},
}

SOIL_AMPLIFICATION = {
    "rock": 1.0,
    "stiff_soil": 1.2,
    "soft_soil": 1.6,
    "fill": 2.0,
}


def simulate_earthquake(city_data: dict, magnitude: float = 6.5,
                          epicenter_lat: float = None, epicenter_lon: float = None,
                          depth_km: float = 15.0) -> dict:
    """
    Run an earthquake simulation.

    Args:
        city_data: Full city dataset from city_loader
        magnitude: Earthquake moment magnitude (4.0-9.0)
        epicenter_lat: Latitude of epicenter
        epicenter_lon: Longitude of epicenter
        depth_km: Earthquake depth in kilometers

    Returns:
        Dictionary with building damage, PGA map, and statistics
    """
    center = city_data["center"]
    if epicenter_lat is None:
        epicenter_lat = center["lat"]
    if epicenter_lon is None:
        epicenter_lon = center["lon"]
    logger.info(f"Starting earthquake simulation: M{magnitude} at "
                f"({epicenter_lat}, {epicenter_lon}), depth={depth_km}km")
    buildings = city_data["buildings"]
    building_damage = _assess_earthquake_damage(
        buildings, magnitude, epicenter_lat, epicenter_lon, depth_km
    )
    pga_grid = _generate_pga_grid(city_data["dem"], magnitude,
                                   epicenter_lat, epicenter_lon, depth_km)
    damage_counts = _count_damage_states(building_damage)
    total_buildings = len(building_damage)
    damaged = sum(1 for b in building_damage if b["damage_state"] != "none")
    stats = {
        "magnitude": magnitude,
        "depth_km": depth_km,
        "epicenter": {"lat": epicenter_lat, "lon": epicenter_lon},
        "total_buildings": total_buildings,
        "buildings_damaged": damaged,
        "max_pga_g": round(max(b["pga_g"] for b in building_damage) if building_damage else 0, 4),
        "mean_pga_g": round(np.mean([b["pga_g"] for b in building_damage]) if building_damage else 0, 4),
    }
    logger.info(f"Earthquake simulation complete: {damaged}/{total_buildings} buildings damaged")
    return {
        "building_damage": building_damage,
        "pga_grid": pga_grid,
        "statistics": stats,
        "damage_summary": damage_counts,
    }


def _assess_earthquake_damage(buildings_geojson: dict, magnitude: float,
                                 epi_lat: float, epi_lon: float,
                                 depth_km: float) -> list:
    """Calculate PGA and damage state for each building."""
    features = buildings_geojson.get("features", [])
    if not features:
        return []
    lats = np.array([shape(f["geometry"]).centroid.y for f in features])
    lons = np.array([shape(f["geometry"]).centroid.x for f in features])
    distances_km = haversine_distance_vectorized(epi_lat, epi_lon, lats, lons) / 1000.0
    pga_values = _calculate_pga_vectorized(magnitude, distances_km, depth_km)
    results = []
    for i, feature in enumerate(features):
        props = feature.get("properties", {})
        soil_type = props.get("soil_type", "stiff_soil")
        structural_class = props.get("structural_class", "C1")
        soil_amp = SOIL_AMPLIFICATION.get(soil_type, 1.2)
        pga = float(pga_values[i]) * soil_amp
        damage_state = _determine_damage_state(pga, structural_class)
        damage_probability = _damage_probability(pga, structural_class)
        results.append({
            "id": props.get("id", f"bldg_{i}"),
            "building_type": props.get("building_type", "unknown"),
            "floors": props.get("floors", 1),
            "construction_year": props.get("construction_year", 2000),
            "material": props.get("material", "unknown"),
            "structural_class": structural_class,
            "soil_type": soil_type,
            "pga_g": round(pga, 4),
            "damage_state": damage_state,
            "damage_probability": round(damage_probability, 3),
            "lat": round(float(lats[i]), 6),
            "lon": round(float(lons[i]), 6),
        })
    return results


def _calculate_pga_vectorized(magnitude: float, distances_km: np.ndarray,
                                 depth_km: float) -> np.ndarray:
    """
    Calculate PGA using a simplified Boore-Atkinson attenuation relationship.
    Returns PGA in units of g.
    """
    r_hyp = np.sqrt(distances_km ** 2 + depth_km ** 2)
    r_hyp = np.clip(r_hyp, 1.0, None)
    log_pga = (0.527 * (magnitude - 6.0)
               - 1.039 * np.log10(r_hyp)
               - 0.0033 * r_hyp
               - 1.301)
    pga = 10 ** log_pga
    pga = np.clip(pga, 0, 3.0)
    return pga


def _determine_damage_state(pga: float, structural_class: str) -> str:
    """Determine the damage state based on PGA and structural class fragility."""
    curves = FRAGILITY_CURVES.get(structural_class, FRAGILITY_CURVES["C1"])
    if pga >= curves["complete"]:
        return "complete"
    elif pga >= curves["extensive"]:
        return "extensive"
    elif pga >= curves["moderate"]:
        return "moderate"
    elif pga >= curves["slight"]:
        return "slight"
    return "none"


def _damage_probability(pga: float, structural_class: str) -> float:
    """Calculate overall damage probability using lognormal fragility curves."""
    curves = FRAGILITY_CURVES.get(structural_class, FRAGILITY_CURVES["C1"])
    beta = 0.6
    prob = 0.0
    for state, median in curves.items():
        if median > 0:
            from scipy.stats import norm
            state_p = norm.cdf(np.log(pga / median) / beta)
            prob = max(prob, state_p)
    return min(prob, 1.0)


def _generate_pga_grid(dem_data: dict, magnitude: float,
                         epi_lat: float, epi_lon: float,
                         depth_km: float) -> dict:
    """Generate a gridded PGA map for heatmap visualization."""
    lat_edges = np.array(dem_data["lat_edges"])
    lon_edges = np.array(dem_data["lon_edges"])
    lats = (lat_edges[:-1] + lat_edges[1:]) / 2
    lons = (lon_edges[:-1] + lon_edges[1:]) / 2
    lat_grid, lon_grid = np.meshgrid(lats, lons, indexing="ij")
    distances_km = haversine_distance_vectorized(
        epi_lat, epi_lon, lat_grid.flatten(), lon_grid.flatten()
    ).reshape(lat_grid.shape) / 1000.0
    pga_grid = _calculate_pga_vectorized(magnitude, distances_km.flatten(), depth_km)
    pga_grid = pga_grid.reshape(lat_grid.shape)
    return {
        "pga": pga_grid.tolist(),
        "lat_edges": lat_edges.tolist(),
        "lon_edges": lon_edges.tolist(),
        "max_pga": round(float(np.max(pga_grid)), 4),
    }


def _count_damage_states(building_damage: list) -> dict:
    """Count buildings in each damage state."""
    counts = {"none": 0, "slight": 0, "moderate": 0, "extensive": 0, "complete": 0}
    for b in building_damage:
        state = b.get("damage_state", "none")
        if state in counts:
            counts[state] += 1
    return counts
