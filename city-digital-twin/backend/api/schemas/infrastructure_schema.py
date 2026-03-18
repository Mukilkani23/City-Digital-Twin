"""
Infrastructure and resource schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional


class InfrastructureResponse(BaseModel):
    """Response schema for city infrastructure data."""
    success: bool = True
    city_name: str
    center: dict = Field(..., description="City center coordinates")
    buildings: dict = Field(..., description="Buildings GeoJSON FeatureCollection")
    roads: dict = Field(..., description="Roads GeoJSON FeatureCollection")
    facilities: dict = Field(..., description="Facilities GeoJSON FeatureCollection")
    stats: dict = Field(..., description="Infrastructure summary statistics")


class ResourceOptimizationRequest(BaseModel):
    """Request schema for resource placement optimization."""
    building_damage: list = Field(..., description="Building damage assessment list")
    num_resources: int = Field(5, ge=1, le=20, description="Number of resources to place")
    coverage_radius_m: float = Field(1500.0, ge=100, le=10000, description="Coverage radius in meters")
    resource_type: str = Field("rescue_team", description="Type of resource")

    class Config:
        json_schema_extra = {
            "example": {
                "building_damage": [],
                "num_resources": 5,
                "coverage_radius_m": 1500.0,
                "resource_type": "rescue_team",
            }
        }


class ResourceOptimizationResponse(BaseModel):
    """Response schema for resource optimization results."""
    success: bool = True
    placements: list = Field(..., description="Optimal resource placement positions")
    resource_type: str
    total_resources: int
    total_at_risk: int
    total_covered: int
    coverage_percentage: float


class RiskBaselineResponse(BaseModel):
    """Response schema for city risk baseline."""
    success: bool = True
    city_name: str
    average_risk: float
    median_risk: float
    max_risk: float
    total_buildings: int
    risk_distribution: dict
