"""
Infrastructure API routes.
Handles GET /api/v1/city/{city_name}/infrastructure and risk-baseline
"""

from fastapi import APIRouter, HTTPException
from backend.data.city_loader import load_city, get_available_cities
from backend.ml.risk_scorer import calculate_city_risk_baseline
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/city", tags=["infrastructure"])


@router.get("/{city_name}/infrastructure")
async def get_city_infrastructure(city_name: str):
    """Get all infrastructure data for a city."""
    try:
        logger.info(f"Loading infrastructure for {city_name}")
        city_data = load_city(city_name)
        return {
            "success": True,
            "city_name": city_data["city_name"],
            "center": city_data["center"],
            "buildings": city_data["buildings"],
            "roads": city_data["roads"],
            "facilities": city_data["facilities"],
            "stats": city_data["stats"],
        }
    except Exception as e:
        logger.error(f"Failed to load infrastructure for {city_name}: {e}")
        raise HTTPException(status_code=500, detail={
            "error": True,
            "message": str(e),
            "code": "INFRASTRUCTURE_LOAD_ERROR"
        })


@router.get("/{city_name}/risk-baseline")
async def get_risk_baseline(city_name: str):
    """Get baseline risk profile for a city without any active disaster."""
    try:
        logger.info(f"Calculating risk baseline for {city_name}")
        city_data = load_city(city_name)
        baseline = calculate_city_risk_baseline(city_data["buildings"])
        return {
            "success": True,
            "city_name": city_name,
            **baseline,
        }
    except Exception as e:
        logger.error(f"Failed to calculate risk baseline for {city_name}: {e}")
        raise HTTPException(status_code=500, detail={
            "error": True,
            "message": str(e),
            "code": "RISK_BASELINE_ERROR"
        })


@router.get("/list")
async def list_cities():
    """Get list of available cities."""
    return {
        "success": True,
        "cities": get_available_cities(),
    }
