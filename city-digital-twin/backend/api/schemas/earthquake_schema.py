"""
Earthquake simulation request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional


class EarthquakeSimulationRequest(BaseModel):
    """Request schema for earthquake simulation."""
    city_name: str = Field(..., description="Name of the city to simulate")
    magnitude: float = Field(6.5, ge=4.0, le=9.5, description="Earthquake magnitude")
    epicenter_lat: Optional[float] = Field(None, description="Epicenter latitude")
    epicenter_lon: Optional[float] = Field(None, description="Epicenter longitude")
    depth_km: float = Field(15.0, ge=1.0, le=100.0, description="Earthquake depth in km")

    class Config:
        json_schema_extra = {
            "example": {
                "city_name": "mumbai",
                "magnitude": 6.5,
                "epicenter_lat": 19.076,
                "epicenter_lon": 72.877,
                "depth_km": 15.0,
            }
        }


class EarthquakeSimulationResponse(BaseModel):
    """Response schema for earthquake simulation results."""
    success: bool = True
    building_damage: list = Field(..., description="Per-building damage assessments")
    pga_grid: dict = Field(..., description="Gridded PGA values for heatmap")
    statistics: dict = Field(..., description="Summary statistics")
    damage_summary: dict = Field(..., description="Damage state distribution")
    road_damage: Optional[list] = Field(None, description="Road blockage assessments")
    cascade_analysis: Optional[dict] = Field(None, description="Cascading failure analysis")
    risk_scores: Optional[list] = Field(None, description="AI risk scores per building")
