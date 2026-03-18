"""
Emergency resource optimizer.
Uses greedy set-cover algorithm to find optimal placement
of rescue resources for maximum population coverage.
"""

import numpy as np
from backend.utils.logger import get_logger
from backend.utils.geo_utils import haversine_distance_vectorized

logger = get_logger(__name__)


def optimize_resource_placement(building_damage: list, num_resources: int = 5,
                                  coverage_radius_m: float = 1500.0,
                                  resource_type: str = "rescue_team") -> dict:
    """
    Find optimal positions to place emergency resources using greedy coverage.

    Args:
        building_damage: List of damaged buildings with lat/lon
        num_resources: Number of resources to place
        coverage_radius_m: Coverage radius per resource in meters
        resource_type: Type of resource (rescue_team, boat, ambulance)

    Returns:
        Dictionary with placement positions and coverage statistics
    """
    at_risk = [b for b in building_damage
               if b.get("damage_state", "none") not in ("none",)]
    if not at_risk:
        at_risk = building_damage[:50] if building_damage else []
    if not at_risk:
        return _empty_result(resource_type)
    logger.info(f"Optimizing {num_resources} {resource_type} placements for "
                f"{len(at_risk)} at-risk buildings")
    demand_lats = np.array([b["lat"] for b in at_risk])
    demand_lons = np.array([b["lon"] for b in at_risk])
    demand_weights = np.array([_damage_weight(b) for b in at_risk])
    candidate_lats, candidate_lons = _generate_candidates(
        demand_lats, demand_lons, grid_size=15
    )
    placements = []
    covered = np.zeros(len(at_risk), dtype=bool)
    for resource_idx in range(min(num_resources, len(candidate_lats))):
        best_score = -1
        best_idx = 0
        for ci in range(len(candidate_lats)):
            distances = haversine_distance_vectorized(
                candidate_lats[ci], candidate_lons[ci],
                demand_lats, demand_lons
            )
            newly_covered = (~covered) & (distances <= coverage_radius_m)
            score = np.sum(demand_weights[newly_covered])
            if score > best_score:
                best_score = score
                best_idx = ci
        distances = haversine_distance_vectorized(
            candidate_lats[best_idx], candidate_lons[best_idx],
            demand_lats, demand_lons
        )
        newly_covered = (~covered) & (distances <= coverage_radius_m)
        covered |= newly_covered
        placements.append({
            "id": f"{resource_type}_{resource_idx + 1}",
            "lat": round(float(candidate_lats[best_idx]), 6),
            "lon": round(float(candidate_lons[best_idx]), 6),
            "coverage_radius_m": coverage_radius_m,
            "buildings_covered": int(np.sum(newly_covered)),
            "weighted_coverage": round(float(best_score), 2),
            "resource_type": resource_type,
        })
        candidate_lats = np.delete(candidate_lats, best_idx)
        candidate_lons = np.delete(candidate_lons, best_idx)
        if len(candidate_lats) == 0:
            break
    total_covered = int(np.sum(covered))
    coverage_pct = round(total_covered / max(len(at_risk), 1) * 100, 1)
    logger.info(f"Resource optimization complete: {coverage_pct}% coverage with "
                f"{len(placements)} {resource_type}s")
    return {
        "placements": placements,
        "resource_type": resource_type,
        "total_resources": len(placements),
        "total_at_risk": len(at_risk),
        "total_covered": total_covered,
        "coverage_percentage": coverage_pct,
        "uncovered_buildings": len(at_risk) - total_covered,
    }


def _generate_candidates(demand_lats: np.ndarray, demand_lons: np.ndarray,
                           grid_size: int = 15) -> tuple:
    """Generate candidate placement positions as a grid over the demand area."""
    lat_min, lat_max = np.min(demand_lats), np.max(demand_lats)
    lon_min, lon_max = np.min(demand_lons), np.max(demand_lons)
    lat_pad = (lat_max - lat_min) * 0.1
    lon_pad = (lon_max - lon_min) * 0.1
    cand_lats = np.linspace(lat_min - lat_pad, lat_max + lat_pad, grid_size)
    cand_lons = np.linspace(lon_min - lon_pad, lon_max + lon_pad, grid_size)
    lat_grid, lon_grid = np.meshgrid(cand_lats, cand_lons)
    return lat_grid.flatten(), lon_grid.flatten()


def _damage_weight(building: dict) -> float:
    """Assign coverage weight based on damage severity."""
    weights = {
        "none": 0.1,
        "slight": 0.5,
        "moderate": 1.0,
        "extensive": 2.0,
        "complete": 3.0,
    }
    base = weights.get(building.get("damage_state", "none"), 1.0)
    if building.get("building_type") in ("hospital", "school", "shelter"):
        base *= 2.0
    return base


def _empty_result(resource_type: str) -> dict:
    """Return an empty optimization result."""
    return {
        "placements": [],
        "resource_type": resource_type,
        "total_resources": 0,
        "total_at_risk": 0,
        "total_covered": 0,
        "coverage_percentage": 0.0,
        "uncovered_buildings": 0,
    }
