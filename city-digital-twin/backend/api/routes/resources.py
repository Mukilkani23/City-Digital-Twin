"""
Resource optimization API routes.
Handles POST /api/v1/optimize/resources
"""

from fastapi import APIRouter, HTTPException
from backend.api.schemas.infrastructure_schema import ResourceOptimizationRequest
from backend.graph.resource_optimizer import optimize_resource_placement
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/optimize", tags=["resources"])


@router.post("/resources")
async def optimize_resources(request: ResourceOptimizationRequest):
    """Find optimal positions for emergency resource placement."""
    try:
        logger.info(f"Resource optimization request: {request.num_resources} "
                    f"{request.resource_type}s, radius={request.coverage_radius_m}m")
        if not request.building_damage:
            return {
                "success": True,
                "placements": [],
                "resource_type": request.resource_type,
                "total_resources": 0,
                "total_at_risk": 0,
                "total_covered": 0,
                "coverage_percentage": 0.0,
                "uncovered_buildings": 0,
                "message": "No building damage data provided"
            }
        result = optimize_resource_placement(
            building_damage=request.building_damage,
            num_resources=request.num_resources,
            coverage_radius_m=request.coverage_radius_m,
            resource_type=request.resource_type,
        )
        result["success"] = True
        return result
    except Exception as e:
        logger.error(f"Resource optimization failed: {e}")
        raise HTTPException(status_code=500, detail={
            "error": True,
            "message": str(e),
            "code": "RESOURCE_OPTIMIZATION_ERROR"
        })
