"""
Earthquake simulation API routes.
Handles POST /api/v1/simulate/earthquake
"""

import numpy as np
from fastapi import APIRouter, HTTPException
from backend.api.schemas.earthquake_schema import EarthquakeSimulationRequest
from backend.data.city_loader import load_city
from backend.simulation.earthquake_simulator import simulate_earthquake
from backend.simulation.cascade_engine import analyze_cascading_failures
from backend.graph.infrastructure_graph import build_road_graph, update_graph_after_earthquake
from backend.graph.graph_analysis import analyze_connectivity, find_isolated_facilities
from backend.ml.risk_scorer import calculate_risk_scores
from backend.ml.damage_predictor import predict_damage
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/simulate", tags=["earthquake"])


@router.post("/earthquake")
async def run_earthquake_simulation(request: EarthquakeSimulationRequest):
    """Run an earthquake simulation for a city."""
    try:
        logger.info(f"Earthquake simulation request: {request.city_name}, "
                    f"M{request.magnitude}, depth={request.depth_km}km")
        city_data = load_city(request.city_name)
        result = simulate_earthquake(
            city_data,
            magnitude=request.magnitude,
            epicenter_lat=request.epicenter_lat,
            epicenter_lon=request.epicenter_lon,
            depth_km=request.depth_km,
        )
        road_graph = build_road_graph(city_data["roads"])
        road_graph = update_graph_after_earthquake(
            road_graph, result["building_damage"], city_data["roads"]
        )
        connectivity = analyze_connectivity(road_graph)
        isolated = find_isolated_facilities(road_graph, city_data["facilities"])
        road_damage = []
        for u, v, data in road_graph.edges(data=True):
            if not data.get("passable", True):
                road_damage.append({
                    "id": data.get("road_id", ""),
                    "blocked": True,
                    "geometry": {"type": "LineString", "coordinates": [list(u), list(v)]}
                })
        cascade = analyze_cascading_failures(
            result["building_damage"], road_damage, city_data["facilities"]
        )
        risk_scores = calculate_risk_scores(result["building_damage"], "earthquake")
        ai_predictions = predict_damage(result["building_damage"])
        result["road_damage"] = road_damage
        result["cascade_analysis"] = cascade
        result["connectivity"] = connectivity
        result["isolated_facilities"] = isolated
        result["risk_scores"] = risk_scores
        result["ai_predictions"] = ai_predictions
        result["statistics"]["roads_blocked_pct"] = connectivity["blocked_percentage"]
        result["statistics"]["hospitals_isolated"] = sum(
            1 for f in isolated if f.get("properties", {}).get("type") == "hospital"
        )
        result["success"] = True
        return result
    except Exception as e:
        logger.error(f"Earthquake simulation failed: {e}")
        raise HTTPException(status_code=500, detail={
            "error": True,
            "message": str(e),
            "code": "EARTHQUAKE_SIMULATION_ERROR"
        })
