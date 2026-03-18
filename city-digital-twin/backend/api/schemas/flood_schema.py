"""
Flood simulation request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional


class FloodSimulationRequest(BaseModel):
    """Request schema for rainfall-based flood simulation."""
    city_name: str = Field(..., description="Name of the city to simulate")
    rainfall_mm: float = Field(150.0, ge=10, le=500, description="Rainfall amount in mm")
    duration_hours: float = Field(6.0, ge=1, le=48, description="Storm duration in hours")
    curve_number: float = Field(80.0, ge=30, le=98, description="SCS curve number")

    class Config:
        json_schema_extra = {
            "example": {
                "city_name": "mumbai",
                "rainfall_mm": 150.0,
                "duration_hours": 6.0,
                "curve_number": 80.0,
            }
        }


class BathtubFloodRequest(BaseModel):
    """Request schema for bathtub (water level) flood simulation."""
    city_name: str = Field(..., description="Name of the city to simulate")
    water_level_m: float = Field(5.0, ge=0.1, le=30.0, description="Water surface elevation in meters")

    class Config:
        json_schema_extra = {
            "example": {
                "city_name": "mumbai",
                "water_level_m": 5.0,
            }
        }


class FloodSimulationResponse(BaseModel):
    """Response schema for flood simulation results."""
    success: bool = True
    flood_zones: dict = Field(..., description="GeoJSON FeatureCollection of flood zones")
    building_damage: list = Field(..., description="Per-building damage assessments")
    statistics: dict = Field(..., description="Summary statistics")
    damage_summary: dict = Field(..., description="Damage state distribution")
    road_damage: Optional[list] = Field(None, description="Road blockage assessments")
    cascade_analysis: Optional[dict] = Field(None, description="Cascading failure analysis")
    risk_scores: Optional[list] = Field(None, description="AI risk scores per building")
