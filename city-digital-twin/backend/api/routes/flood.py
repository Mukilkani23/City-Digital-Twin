"""
Flood simulation API routes.
Handles POST /api/v1/simulate/flood and POST /api/v1/simulate/flood/bathtub
"""

import numpy as np
from fastapi import APIRouter, HTTPException
from backend.api.schemas.flood_schema import FloodSimulationRequest, BathtubFloodRequest
from backend.data.city_loader import load_city
from backend.simulation.flood_simulator import simulate_rainfall_flood, simulate_bathtub_flood
from backend.simulation.cascade_engine import assess_road_damage, analyze_cascading_failures
from backend.graph.infrastructure_graph import build_road_graph, update_graph_after_flood
from backend.graph.graph_analysis import analyze_connectivity, find_isolated_facilities
from backend.ml.risk_scorer import calculate_risk_scores
from backend.ml.damage_predictor import predict_damage
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/simulate", tags=["flood"])


@router.post("/flood")
async def run_flood_simulation(request: FloodSimulationRequest):
    """Run a rainfall-based flood simulation for a city."""
    try:
        logger.info(f"Flood simulation request: {request.city_name}, "
                    f"{request.rainfall_mm}mm, {request.duration_hours}h")
        city_data = load_city(request.city_name)
        result = simulate_rainfall_flood(
            city_data,
            rainfall_mm=request.rainfall_mm,
            duration_hours=request.duration_hours,
            curve_number=request.curve_number,
        )
        dem = city_data["dem"]
        elevation = np.array(dem["elevation"])
        lat_edges = np.array(dem["lat_edges"])
        lon_edges = np.array(dem["lon_edges"])
        from backend.simulation.rainfall_runoff import distribute_runoff_on_dem, calculate_runoff_scs
        runoff = calculate_runoff_scs(request.rainfall_mm, request.curve_number, request.duration_hours)
        flood_depth = distribute_runoff_on_dem(runoff["runoff_mm"], elevation)
        road_damage = assess_road_damage(
            city_data["roads"], flood_depth, lat_edges, lon_edges
        )
        road_graph = build_road_graph(city_data["roads"])
        road_graph = update_graph_after_flood(road_graph, road_damage)
        connectivity = analyze_connectivity(road_graph)
        isolated = find_isolated_facilities(road_graph, city_data["facilities"])
        cascade = analyze_cascading_failures(
            result["building_damage"], road_damage, city_data["facilities"]
        )
        risk_scores = calculate_risk_scores(result["building_damage"], "flood")
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
        logger.error(f"Flood simulation failed: {e}")
        raise HTTPException(status_code=500, detail={
            "error": True,
            "message": str(e),
            "code": "FLOOD_SIMULATION_ERROR"
        })


@router.post("/flood/bathtub")
async def run_bathtub_flood(request: BathtubFloodRequest):
    """Run a fast bathtub flood simulation for animation."""
    try:
        logger.info(f"Bathtub flood request: {request.city_name}, {request.water_level_m}m")
        city_data = load_city(request.city_name)
        result = simulate_bathtub_flood(city_data, water_level_m=request.water_level_m)
        result["success"] = True
        return result
    except Exception as e:
        logger.error(f"Bathtub flood simulation failed: {e}")
        raise HTTPException(status_code=500, detail={
            "error": True,
            "message": str(e),
            "code": "BATHTUB_FLOOD_ERROR"
        })
