"""
Flood simulator.
Implements two flood simulation modes:
1. Rainfall-based: Uses SCS Curve Number + DEM flow routing
2. Bathtub (water level): Instantly floods below a given elevation
"""

import numpy as np
from shapely.geometry import shape, Point
from backend.utils.logger import get_logger
from backend.utils.raster_utils import raster_to_polygons, classify_flood_depth
from backend.utils.geo_utils import feature_collection
from backend.simulation.rainfall_runoff import calculate_runoff_scs, distribute_runoff_on_dem

logger = get_logger(__name__)


def simulate_rainfall_flood(city_data: dict, rainfall_mm: float = 150.0,
                             duration_hours: float = 6.0, curve_number: float = 80.0) -> dict:
    """
    Run a rainfall-based flood simulation.

    Args:
        city_data: Full city dataset from city_loader
        rainfall_mm: Total rainfall in mm
        duration_hours: Storm duration in hours
        curve_number: SCS curve number for soil/land cover

    Returns:
        Dictionary with flood zones GeoJSON, building damage, and statistics
    """
    logger.info(f"Starting rainfall flood simulation: {rainfall_mm}mm over {duration_hours}h, CN={curve_number}")
    runoff = calculate_runoff_scs(rainfall_mm, curve_number, duration_hours)
    dem = city_data["dem"]
    elevation = np.array(dem["elevation"])
    lat_edges = np.array(dem["lat_edges"])
    lon_edges = np.array(dem["lon_edges"])
    flood_depth = distribute_runoff_on_dem(runoff["runoff_mm"], elevation)
    flood_features = raster_to_polygons(flood_depth, lat_edges, lon_edges, threshold=0.05)
    building_damage = _assess_building_flood_damage(city_data["buildings"], flood_depth, lat_edges, lon_edges)
    affected_area_km2 = _calculate_affected_area(flood_depth, lat_edges, lon_edges, threshold=0.1)
    stats = {
        "affected_area_km2": round(affected_area_km2, 3),
        "buildings_at_risk": sum(1 for b in building_damage if b["flood_depth"] > 0.1),
        "max_flood_depth_m": round(float(np.max(flood_depth)), 2),
        "mean_flood_depth_m": round(float(np.mean(flood_depth[flood_depth > 0.05])) if np.any(flood_depth > 0.05) else 0, 2),
        "runoff_mm": runoff["runoff_mm"],
        "peak_discharge_m3s": runoff["peak_discharge_m3s"],
    }
    damage_counts = _count_damage_states(building_damage)
    logger.info(f"Flood simulation complete: {stats['buildings_at_risk']} buildings at risk")
    return {
        "flood_zones": feature_collection(flood_features),
        "building_damage": building_damage,
        "statistics": stats,
        "damage_summary": damage_counts,
        "runoff": runoff,
        "hydrograph": runoff["hydrograph"],
    }


def simulate_bathtub_flood(city_data: dict, water_level_m: float = 5.0) -> dict:
    """
    Run a bathtub flood simulation — flood everything below a given elevation.

    Args:
        city_data: Full city dataset
        water_level_m: Water surface elevation in meters

    Returns:
        Dictionary with flood zones GeoJSON and building damage
    """
    logger.info(f"Starting bathtub flood simulation: water level = {water_level_m}m")
    dem = city_data["dem"]
    elevation = np.array(dem["elevation"])
    lat_edges = np.array(dem["lat_edges"])
    lon_edges = np.array(dem["lon_edges"])
    flood_depth = np.clip(water_level_m - elevation, 0, None)
    flood_features = raster_to_polygons(flood_depth, lat_edges, lon_edges, threshold=0.05)
    building_damage = _assess_building_flood_damage(city_data["buildings"], flood_depth, lat_edges, lon_edges)
    affected_area_km2 = _calculate_affected_area(flood_depth, lat_edges, lon_edges, threshold=0.1)
    stats = {
        "affected_area_km2": round(affected_area_km2, 3),
        "buildings_at_risk": sum(1 for b in building_damage if b["flood_depth"] > 0.1),
        "max_flood_depth_m": round(float(np.max(flood_depth)), 2),
        "water_level_m": water_level_m,
    }
    damage_counts = _count_damage_states(building_damage)
    logger.info(f"Bathtub simulation complete: {stats['buildings_at_risk']} buildings at risk")
    return {
        "flood_zones": feature_collection(flood_features),
        "building_damage": building_damage,
        "statistics": stats,
        "damage_summary": damage_counts,
    }


def _assess_building_flood_damage(buildings_geojson: dict, flood_depth: np.ndarray,
                                    lat_edges: np.ndarray, lon_edges: np.ndarray) -> list:
    """Assess flood damage for each building based on flood depth at its location."""
    results = []
    rows, cols = flood_depth.shape
    for feature in buildings_geojson.get("features", []):
        geom = shape(feature["geometry"])
        centroid = geom.centroid
        lat_idx = np.searchsorted(lat_edges, centroid.y) - 1
        lon_idx = np.searchsorted(lon_edges, centroid.x) - 1
        lat_idx = np.clip(lat_idx, 0, rows - 1)
        lon_idx = np.clip(lon_idx, 0, cols - 1)
        depth = float(flood_depth[lat_idx, lon_idx])
        damage_state = _flood_damage_state(depth)
        damage_ratio = _flood_damage_ratio(depth)
        props = feature.get("properties", {})
        results.append({
            "id": props.get("id", "unknown"),
            "building_type": props.get("building_type", "unknown"),
            "floors": props.get("floors", 1),
            "construction_year": props.get("construction_year", 2000),
            "material": props.get("material", "unknown"),
            "flood_depth": round(depth, 3),
            "damage_state": damage_state,
            "damage_ratio": round(damage_ratio, 3),
            "lat": round(centroid.y, 6),
            "lon": round(centroid.x, 6),
            "depth_category": classify_flood_depth(depth),
        })
    return results


def _flood_damage_state(depth: float) -> str:
    """Determine damage state based on flood depth."""
    if depth < 0.1:
        return "none"
    elif depth < 0.3:
        return "slight"
    elif depth < 1.0:
        return "moderate"
    elif depth < 2.0:
        return "extensive"
    return "complete"


def _flood_damage_ratio(depth: float) -> float:
    """Calculate damage ratio (0-1) from flood depth using a sigmoid curve."""
    if depth <= 0:
        return 0.0
    return min(1.0, 1.0 - np.exp(-0.5 * depth))


def _calculate_affected_area(flood_depth: np.ndarray, lat_edges: np.ndarray,
                               lon_edges: np.ndarray, threshold: float = 0.1) -> float:
    """Estimate the total flooded area in square kilometers."""
    affected_cells = np.sum(flood_depth > threshold)
    total_cells = flood_depth.size
    lat_span = abs(lat_edges[-1] - lat_edges[0]) * 111.32
    lon_span = abs(lon_edges[-1] - lon_edges[0]) * 111.32 * np.cos(np.radians(np.mean(lat_edges)))
    total_area = lat_span * lon_span
    return total_area * (affected_cells / total_cells)


def _count_damage_states(building_damage: list) -> dict:
    """Count buildings in each damage state."""
    counts = {"none": 0, "slight": 0, "moderate": 0, "extensive": 0, "complete": 0}
    for b in building_damage:
        state = b.get("damage_state", "none")
        if state in counts:
            counts[state] += 1
    return counts


def generate_flood_animation_frames(city_data: dict, max_water_level: float = 10.0,
                                      num_frames: int = 10) -> list:
    """Generate a series of bathtub flood frames for animation."""
    levels = np.linspace(0.5, max_water_level, num_frames)
    frames = []
    for level in levels:
        result = simulate_bathtub_flood(city_data, float(level))
        frames.append({
            "water_level": round(float(level), 2),
            "statistics": result["statistics"],
            "damage_summary": result["damage_summary"],
        })
    return frames
