"""
Application configuration module.
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")

DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
CACHE_DIR = BASE_DIR / os.getenv("CACHE_DIR", "data/processed")
SAMPLE_DIR = BASE_DIR / os.getenv("SAMPLE_DIR", "data/sample")
MODEL_DIR = BASE_DIR / os.getenv("MODEL_DIR", "backend/ml/models")
RAW_DIR = DATA_DIR / "raw"

for directory in [DATA_DIR, CACHE_DIR, SAMPLE_DIR, MODEL_DIR, RAW_DIR,
                  CACHE_DIR / "graphs", CACHE_DIR / "rasters", CACHE_DIR / "vectors",
                  RAW_DIR / "dem", RAW_DIR / "osm", RAW_DIR / "weather"]:
    directory.mkdir(parents=True, exist_ok=True)

CITY_CONFIGS = {
    "mumbai": {"lat": 19.076, "lon": 72.8777, "radius": 3000, "country": "India"},
    "chennai": {"lat": 13.0827, "lon": 80.2707, "radius": 3000, "country": "India"},
    "kolkata": {"lat": 22.5726, "lon": 88.3639, "radius": 3000, "country": "India"},
    "delhi": {"lat": 28.6139, "lon": 77.2090, "radius": 3000, "country": "India"},
    "jakarta": {"lat": -6.2088, "lon": 106.8456, "radius": 3000, "country": "Indonesia"},
}

OSM_TIMEOUT = 30
OSM_MAX_RETRIES = 2
SIMULATION_MAX_TIME = 10
DEFAULT_CRS = "EPSG:4326"
PROJECTED_CRS = "EPSG:3857"
