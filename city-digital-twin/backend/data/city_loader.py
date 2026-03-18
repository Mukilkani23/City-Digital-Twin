"""
City data loader.
Orchestrates loading of all city datasets: buildings, roads, facilities, DEM.
Uses cache for fast repeat access and synthetic fallback for reliability.
"""

import json
from pathlib import Path
from backend.utils.logger import get_logger
from backend.config import CITY_CONFIGS, SAMPLE_DIR
from backend.data import cache_manager
from backend.data.osm_processor import fetch_buildings, fetch_roads, fetch_facilities
from backend.data.dem_processor import get_dem

logger = get_logger(__name__)


def load_city(city_name: str) -> dict:
    """Load all data for a city, using cache if available."""
    city_key = city_name.lower()
    cached = cache_manager.get_from_memory(city_key, "full_city")
    if cached is not None:
        logger.info(f"City {city_name} loaded from memory cache")
        return cached

    logger.info(f"Loading city data for {city_name}...")
    buildings = _load_buildings(city_key)
    roads = _load_roads(city_key)
    facilities = _load_facilities(city_key)
    dem = _load_dem(city_key)

    config = CITY_CONFIGS.get(city_key, CITY_CONFIGS["mumbai"])
    city_data = {
        "city_name": city_name,
        "center": {"lat": config["lat"], "lon": config["lon"]},
        "radius": config["radius"],
        "buildings": buildings,
        "roads": roads,
        "facilities": facilities,
        "dem": dem,
        "stats": {
            "building_count": len(buildings.get("features", [])),
            "road_count": len(roads.get("features", [])),
            "facility_count": len(facilities.get("features", [])),
        }
    }
    cache_manager.put_to_memory(city_key, "full_city", city_data)
    logger.info(f"City {city_name} loaded: {city_data['stats']}")
    return city_data


def _load_buildings(city_key: str) -> dict:
    """Load buildings from cache, then OSM, then sample data."""
    cached = cache_manager.get_cached(city_key, "buildings")
    if cached is not None:
        return cached
    sample_path = SAMPLE_DIR / f"{city_key}_buildings.geojson"
    if sample_path.exists():
        logger.info(f"Loading buildings from sample file: {sample_path}")
        with open(sample_path, "r") as f:
            data = json.load(f)
        cache_manager.put_cached(city_key, "buildings", data)
        return data
    data = fetch_buildings(city_key)
    cache_manager.put_cached(city_key, "buildings", data)
    return data


def _load_roads(city_key: str) -> dict:
    """Load roads from cache, then OSM, then sample data."""
    cached = cache_manager.get_cached(city_key, "roads")
    if cached is not None:
        return cached
    sample_path = SAMPLE_DIR / f"{city_key}_roads.geojson"
    if sample_path.exists():
        logger.info(f"Loading roads from sample file: {sample_path}")
        with open(sample_path, "r") as f:
            data = json.load(f)
        cache_manager.put_cached(city_key, "roads", data)
        return data
    data = fetch_roads(city_key)
    cache_manager.put_cached(city_key, "roads", data)
    return data


def _load_facilities(city_key: str) -> dict:
    """Load facilities from cache, then OSM, then sample data."""
    cached = cache_manager.get_cached(city_key, "facilities")
    if cached is not None:
        return cached
    sample_path = SAMPLE_DIR / f"{city_key}_facilities.geojson"
    if sample_path.exists():
        logger.info(f"Loading facilities from sample file: {sample_path}")
        with open(sample_path, "r") as f:
            data = json.load(f)
        cache_manager.put_cached(city_key, "facilities", data)
        return data
    data = fetch_facilities(city_key)
    cache_manager.put_cached(city_key, "facilities", data)
    return data


def _load_dem(city_key: str) -> dict:
    """Load DEM from cache or generate synthetic."""
    cached = cache_manager.get_from_memory(city_key, "dem")
    if cached is not None:
        return cached
    data = get_dem(city_key)
    cache_manager.put_to_memory(city_key, "dem", data)
    return data


def get_available_cities() -> list:
    """Return list of available cities."""
    cities = []
    for name, config in CITY_CONFIGS.items():
        cities.append({
            "name": name.title(),
            "key": name,
            "lat": config["lat"],
            "lon": config["lon"],
            "country": config["country"],
        })
    return cities


def preload_sample_city():
    """Pre-load sample city data at startup for fast first response."""
    sample_files = list(SAMPLE_DIR.glob("*.geojson"))
    if sample_files:
        city_key = sample_files[0].stem.split("_")[0]
        logger.info(f"Pre-loading sample city: {city_key}")
        load_city(city_key)
    else:
        logger.info("No sample data found. Generating synthetic city data for Mumbai...")
        load_city("mumbai")
