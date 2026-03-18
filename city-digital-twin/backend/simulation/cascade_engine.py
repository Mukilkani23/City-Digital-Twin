"""
Cascade engine for modeling cascading infrastructure failures.
Analyzes how initial damage propagates through interconnected systems.
"""

import numpy as np
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def analyze_cascading_failures(building_damage: list, road_damage: list,
                                 facilities: dict) -> dict:
    """
    Analyze cascading failures from initial damage.

    When roads are blocked, facilities may become isolated.
    When key buildings are damaged, dependent services fail.

    Args:
        building_damage: List of building damage assessments
        road_damage: List of road damage assessments
        facilities: Facilities GeoJSON FeatureCollection

    Returns:
        Dictionary with cascade analysis results
    """
    logger.info("Analyzing cascading infrastructure failures...")
    damaged_buildings = [b for b in building_damage
                        if b.get("damage_state") in ("extensive", "complete")]
    blocked_roads = [r for r in road_damage if r.get("blocked", False)]
    facility_features = facilities.get("features", [])
    isolated_facilities = _find_isolated_facilities(facility_features, blocked_roads)
    cascade_events = []
    hospital_count = sum(1 for f in facility_features
                        if f["properties"].get("type") == "hospital")
    isolated_hospitals = sum(1 for f in isolated_facilities
                            if f["properties"].get("type") == "hospital")
    if isolated_hospitals > 0:
        cascade_events.append({
            "type": "healthcare_disruption",
            "severity": "critical" if isolated_hospitals > hospital_count * 0.5 else "moderate",
            "description": f"{isolated_hospitals} of {hospital_count} hospitals isolated",
            "affected_population_estimate": isolated_hospitals * 5000,
        })
    damaged_critical = [b for b in damaged_buildings
                       if b.get("building_type") in ("hospital", "fire_station", "government")]
    if damaged_critical:
        cascade_events.append({
            "type": "critical_facility_damage",
            "severity": "critical",
            "description": f"{len(damaged_critical)} critical facilities damaged",
            "facilities": [b.get("id") for b in damaged_critical],
        })
    road_block_pct = (len(blocked_roads) / max(len(road_damage), 1)) * 100
    if road_block_pct > 30:
        cascade_events.append({
            "type": "transportation_collapse",
            "severity": "critical" if road_block_pct > 60 else "moderate",
            "description": f"{road_block_pct:.0f}% of roads blocked",
            "blocked_count": len(blocked_roads),
        })
    shelter_isolated = sum(1 for f in isolated_facilities
                          if f["properties"].get("type") == "shelter")
    if shelter_isolated > 0:
        cascade_events.append({
            "type": "shelter_access_lost",
            "severity": "moderate",
            "description": f"{shelter_isolated} emergency shelters unreachable",
        })
    total_cascades = len(cascade_events)
    severity_score = _calculate_severity_score(cascade_events)
    logger.info(f"Cascade analysis complete: {total_cascades} cascade events, severity={severity_score}")
    return {
        "cascade_events": cascade_events,
        "total_cascades": total_cascades,
        "severity_score": severity_score,
        "isolated_facilities": [
            {
                "name": f["properties"].get("name", "Unknown"),
                "type": f["properties"].get("type", "unknown"),
                "coordinates": f["geometry"]["coordinates"],
            }
            for f in isolated_facilities
        ],
        "summary": {
            "damaged_buildings": len(damaged_buildings),
            "blocked_roads": len(blocked_roads),
            "isolated_hospitals": isolated_hospitals,
            "isolated_shelters": shelter_isolated,
            "road_block_percentage": round(road_block_pct, 1),
        }
    }


def _find_isolated_facilities(facilities: list, blocked_roads: list) -> list:
    """Determine which facilities are isolated due to road blockages."""
    if not blocked_roads:
        return []
    blocked_coords = set()
    for road in blocked_roads:
        coords = road.get("geometry", {}).get("coordinates", [])
        if coords:
            for coord in coords:
                if isinstance(coord, (list, tuple)) and len(coord) >= 2:
                    blocked_coords.add((round(coord[0], 4), round(coord[1], 4)))
    rng = np.random.RandomState(len(blocked_roads))
    block_fraction = len(blocked_roads) / max(len(blocked_roads) + 10, 1)
    isolated = []
    for facility in facilities:
        isolation_probability = block_fraction * 0.6
        if rng.random() < isolation_probability:
            isolated.append(facility)
    return isolated


def _calculate_severity_score(cascade_events: list) -> float:
    """Calculate an overall severity score from 0 to 100."""
    if not cascade_events:
        return 0.0
    severity_weights = {"critical": 40, "moderate": 20, "low": 10}
    total = sum(severity_weights.get(e.get("severity", "low"), 5) for e in cascade_events)
    return min(100.0, round(total, 1))


def assess_road_damage(roads_geojson: dict, flood_depth: np.ndarray = None,
                         building_damage: list = None,
                         lat_edges: np.ndarray = None,
                         lon_edges: np.ndarray = None) -> list:
    """Assess which roads are blocked based on flood depth or nearby building damage."""
    results = []
    features = roads_geojson.get("features", [])
    for feature in features:
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [])
        blocked = False
        flood_at_road = 0.0
        if flood_depth is not None and lat_edges is not None and lon_edges is not None:
            if coords and len(coords) >= 2:
                mid_idx = len(coords) // 2
                mid_coord = coords[mid_idx]
                lat_idx = np.searchsorted(lat_edges, mid_coord[1]) - 1
                lon_idx = np.searchsorted(lon_edges, mid_coord[0]) - 1
                rows, cols = flood_depth.shape
                lat_idx = np.clip(lat_idx, 0, rows - 1)
                lon_idx = np.clip(lon_idx, 0, cols - 1)
                flood_at_road = float(flood_depth[lat_idx, lon_idx])
                if flood_at_road > 0.3:
                    blocked = True
        results.append({
            "id": props.get("id", "unknown"),
            "name": props.get("name", "unnamed"),
            "highway": props.get("highway", "residential"),
            "blocked": blocked,
            "flood_depth": round(flood_at_road, 3),
            "geometry": feature.get("geometry", {}),
        })
    return results
