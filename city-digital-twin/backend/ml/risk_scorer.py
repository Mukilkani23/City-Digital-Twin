"""
Risk scorer module.
Computes composite risk scores (0-100) for buildings
by combining hazard exposure, vulnerability, and AI predictions.
"""

import numpy as np
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def calculate_risk_scores(building_damage: list, disaster_type: str = "flood") -> list:
    """
    Calculate composite risk scores for buildings.

    Combines structural vulnerability, hazard exposure, and historical risk
    into a 0-100 score.

    Args:
        building_damage: List of building damage assessments
        disaster_type: "flood" or "earthquake"

    Returns:
        List of buildings enriched with risk scores and factors
    """
    if not building_damage:
        return []
    results = []
    for bldg in building_damage:
        hazard_score = _hazard_exposure_score(bldg, disaster_type)
        vulnerability_score = _vulnerability_score(bldg)
        consequence_score = _consequence_score(bldg)
        composite = (hazard_score * 0.4 +
                    vulnerability_score * 0.35 +
                    consequence_score * 0.25)
        risk_score = round(min(100.0, max(0.0, composite)), 1)
        risk_factors = _identify_risk_factors(bldg, disaster_type,
                                               hazard_score, vulnerability_score)
        results.append({
            **bldg,
            "risk_score": risk_score,
            "risk_level": _risk_level(risk_score),
            "hazard_score": round(hazard_score, 1),
            "vulnerability_score": round(vulnerability_score, 1),
            "consequence_score": round(consequence_score, 1),
            "risk_factors": risk_factors,
        })
    logger.info(f"Risk scores calculated for {len(results)} buildings")
    return results


def _hazard_exposure_score(bldg: dict, disaster_type: str) -> float:
    """Calculate hazard exposure score (0-100)."""
    if disaster_type == "flood":
        depth = bldg.get("flood_depth", 0.0)
        return min(100.0, depth * 40.0)
    else:
        pga = bldg.get("pga_g", 0.0)
        return min(100.0, pga * 200.0)


def _vulnerability_score(bldg: dict) -> float:
    """Calculate structural vulnerability score (0-100)."""
    score = 50.0
    age = 2024 - bldg.get("construction_year", 2000)
    score += min(20.0, age * 0.4)
    material_vuln = {
        "reinforced_concrete": -15,
        "steel": -10,
        "masonry": 5,
        "wood": 15,
    }
    score += material_vuln.get(bldg.get("material", "masonry"), 0)
    soil_vuln = {
        "rock": -10,
        "stiff_soil": 0,
        "soft_soil": 10,
        "fill": 20,
    }
    score += soil_vuln.get(bldg.get("soil_type", "stiff_soil"), 0)
    floors = bldg.get("floors", 1)
    if floors > 5:
        score += 5
    return min(100.0, max(0.0, score))


def _consequence_score(bldg: dict) -> float:
    """Calculate consequence score based on building importance."""
    type_scores = {
        "hospital": 95,
        "school": 80,
        "shelter": 85,
        "fire_station": 90,
        "government": 70,
        "commercial": 50,
        "residential": 40,
        "industrial": 45,
    }
    base = type_scores.get(bldg.get("building_type", "residential"), 40)
    floors = bldg.get("floors", 1)
    base += min(10, floors * 1.5)
    return min(100.0, base)


def _identify_risk_factors(bldg: dict, disaster_type: str,
                             hazard_score: float, vulnerability_score: float) -> list:
    """Identify top risk contributing factors for a building."""
    factors = []
    if disaster_type == "flood" and bldg.get("flood_depth", 0) > 0.5:
        factors.append({
            "factor": "High flood exposure",
            "impact": "high",
            "detail": f"Flood depth: {bldg.get('flood_depth', 0):.2f}m"
        })
    if disaster_type == "earthquake" and bldg.get("pga_g", 0) > 0.2:
        factors.append({
            "factor": "Strong ground shaking",
            "impact": "high",
            "detail": f"PGA: {bldg.get('pga_g', 0):.3f}g"
        })
    age = 2024 - bldg.get("construction_year", 2000)
    if age > 30:
        factors.append({
            "factor": "Aging structure",
            "impact": "medium",
            "detail": f"Built in {bldg.get('construction_year', 2000)} ({age} years old)"
        })
    if bldg.get("material") in ("wood", "masonry"):
        factors.append({
            "factor": f"Vulnerable material ({bldg.get('material')})",
            "impact": "medium",
            "detail": "More susceptible to damage"
        })
    if bldg.get("soil_type") in ("soft_soil", "fill"):
        factors.append({
            "factor": f"Poor soil conditions ({bldg.get('soil_type')})",
            "impact": "medium",
            "detail": "Amplifies ground motion and settlement"
        })
    return factors[:3]


def _risk_level(score: float) -> str:
    """Classify risk score into a level."""
    if score < 20:
        return "low"
    elif score < 40:
        return "moderate"
    elif score < 60:
        return "high"
    elif score < 80:
        return "very_high"
    return "critical"


def calculate_city_risk_baseline(buildings_geojson: dict) -> dict:
    """Calculate baseline risk profile for a city without any active disaster."""
    features = buildings_geojson.get("features", [])
    if not features:
        return {"average_risk": 0, "risk_distribution": {}}
    scores = []
    for f in features:
        props = f.get("properties", {})
        vuln = _vulnerability_score(props)
        consequence = _consequence_score(props)
        baseline = vuln * 0.5 + consequence * 0.5
        scores.append(round(min(100, baseline), 1))
    return {
        "average_risk": round(float(np.mean(scores)), 1),
        "median_risk": round(float(np.median(scores)), 1),
        "max_risk": round(float(np.max(scores)), 1),
        "total_buildings": len(scores),
        "risk_distribution": {
            "low": int(np.sum(np.array(scores) < 20)),
            "moderate": int(np.sum((np.array(scores) >= 20) & (np.array(scores) < 40))),
            "high": int(np.sum((np.array(scores) >= 40) & (np.array(scores) < 60))),
            "very_high": int(np.sum((np.array(scores) >= 60) & (np.array(scores) < 80))),
            "critical": int(np.sum(np.array(scores) >= 80)),
        },
        "building_scores": scores[:100],
    }
