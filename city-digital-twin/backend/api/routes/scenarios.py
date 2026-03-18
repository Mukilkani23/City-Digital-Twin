"""
Scenario management API routes.
Handles scenario comparison and management.
"""

from fastapi import APIRouter, HTTPException
from backend.data.city_loader import load_city
from backend.simulation.flood_simulator import simulate_rainfall_flood
from backend.simulation.earthquake_simulator import simulate_earthquake
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/scenarios", tags=["scenarios"])

_scenario_store: dict = {}


@router.post("/save")
async def save_scenario(scenario: dict):
    """Save a simulation result as a named scenario for later comparison."""
    try:
        name = scenario.get("name", f"scenario_{len(_scenario_store)}")
        _scenario_store[name] = {
            "name": name,
            "type": scenario.get("type", "flood"),
            "parameters": scenario.get("parameters", {}),
            "statistics": scenario.get("statistics", {}),
            "damage_summary": scenario.get("damage_summary", {}),
        }
        logger.info(f"Saved scenario: {name}")
        return {"success": True, "name": name, "total_saved": len(_scenario_store)}
    except Exception as e:
        logger.error(f"Failed to save scenario: {e}")
        raise HTTPException(status_code=500, detail={
            "error": True,
            "message": str(e),
            "code": "SCENARIO_SAVE_ERROR"
        })


@router.get("/list")
async def list_scenarios():
    """List all saved scenarios."""
    return {
        "success": True,
        "scenarios": list(_scenario_store.values()),
        "total": len(_scenario_store),
    }


@router.get("/{name}")
async def get_scenario(name: str):
    """Get a saved scenario by name."""
    if name not in _scenario_store:
        raise HTTPException(status_code=404, detail={
            "error": True,
            "message": f"Scenario '{name}' not found",
            "code": "SCENARIO_NOT_FOUND"
        })
    return {"success": True, "scenario": _scenario_store[name]}


@router.post("/compare")
async def compare_scenarios(request: dict):
    """Compare two scenarios side by side."""
    try:
        city_name = request.get("city_name", "mumbai")
        scenario_a = request.get("scenario_a", {})
        scenario_b = request.get("scenario_b", {})
        city_data = load_city(city_name)
        result_a = _run_scenario(city_data, scenario_a)
        result_b = _run_scenario(city_data, scenario_b)
        comparison = {
            "scenario_a": {
                "parameters": scenario_a,
                "statistics": result_a.get("statistics", {}),
                "damage_summary": result_a.get("damage_summary", {}),
            },
            "scenario_b": {
                "parameters": scenario_b,
                "statistics": result_b.get("statistics", {}),
                "damage_summary": result_b.get("damage_summary", {}),
            },
            "differences": _compare_stats(
                result_a.get("statistics", {}),
                result_b.get("statistics", {})
            ),
        }
        return {"success": True, "comparison": comparison}
    except Exception as e:
        logger.error(f"Scenario comparison failed: {e}")
        raise HTTPException(status_code=500, detail={
            "error": True,
            "message": str(e),
            "code": "COMPARISON_ERROR"
        })


def _run_scenario(city_data: dict, params: dict) -> dict:
    """Execute a scenario based on its parameters."""
    scenario_type = params.get("type", "flood")
    if scenario_type == "flood":
        return simulate_rainfall_flood(
            city_data,
            rainfall_mm=params.get("rainfall_mm", 150),
            duration_hours=params.get("duration_hours", 6),
            curve_number=params.get("curve_number", 80),
        )
    elif scenario_type == "earthquake":
        return simulate_earthquake(
            city_data,
            magnitude=params.get("magnitude", 6.5),
            depth_km=params.get("depth_km", 15),
        )
    return {}


def _compare_stats(stats_a: dict, stats_b: dict) -> dict:
    """Calculate differences between two statistics dicts."""
    diffs = {}
    all_keys = set(list(stats_a.keys()) + list(stats_b.keys()))
    for key in all_keys:
        val_a = stats_a.get(key)
        val_b = stats_b.get(key)
        if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
            diffs[key] = {
                "scenario_a": val_a,
                "scenario_b": val_b,
                "difference": round(val_b - val_a, 4),
                "change_pct": round((val_b - val_a) / max(abs(val_a), 0.001) * 100, 1),
            }
    return diffs
