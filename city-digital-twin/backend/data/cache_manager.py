"""
Cache manager for city data.
Provides in-memory and on-disk caching of loaded city datasets
to avoid repeated downloads and processing.
"""

import json
import hashlib
from pathlib import Path
from backend.utils.logger import get_logger
from backend.config import CACHE_DIR

logger = get_logger(__name__)

_memory_cache: dict = {}


def cache_key(city_name: str, data_type: str) -> str:
    """Generate a cache key from city name and data type."""
    raw = f"{city_name.lower()}_{data_type}"
    return hashlib.md5(raw.encode()).hexdigest()


def get_from_memory(city_name: str, data_type: str):
    """Retrieve data from in-memory cache."""
    key = cache_key(city_name, data_type)
    if key in _memory_cache:
        logger.info(f"Memory cache hit: {city_name}/{data_type}")
        return _memory_cache[key]
    return None


def put_to_memory(city_name: str, data_type: str, data):
    """Store data in in-memory cache."""
    key = cache_key(city_name, data_type)
    _memory_cache[key] = data
    logger.info(f"Cached in memory: {city_name}/{data_type}")


def get_from_disk(city_name: str, data_type: str):
    """Retrieve JSON data from disk cache."""
    file_path = CACHE_DIR / f"{cache_key(city_name, data_type)}.json"
    if file_path.exists():
        logger.info(f"Disk cache hit: {file_path}")
        with open(file_path, "r") as f:
            return json.load(f)
    return None


def put_to_disk(city_name: str, data_type: str, data: dict):
    """Store JSON data to disk cache."""
    file_path = CACHE_DIR / f"{cache_key(city_name, data_type)}.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    logger.info(f"Cached to disk: {file_path}")


def get_cached(city_name: str, data_type: str):
    """Try memory cache first, then disk cache."""
    result = get_from_memory(city_name, data_type)
    if result is not None:
        return result
    result = get_from_disk(city_name, data_type)
    if result is not None:
        put_to_memory(city_name, data_type, result)
    return result


def put_cached(city_name: str, data_type: str, data):
    """Store to both memory and disk cache."""
    put_to_memory(city_name, data_type, data)
    if isinstance(data, dict):
        put_to_disk(city_name, data_type, data)


def clear_cache(city_name: str = None):
    """Clear cache for a specific city or all."""
    global _memory_cache
    if city_name is None:
        _memory_cache.clear()
        for f in CACHE_DIR.glob("*.json"):
            f.unlink()
        logger.info("Cleared all caches")
    else:
        keys_to_remove = [k for k in _memory_cache
                          if k.startswith(hashlib.md5(city_name.lower().encode()).hexdigest()[:8])]
        for k in keys_to_remove:
            del _memory_cache[k]
        logger.info(f"Cleared cache for {city_name}")


def cache_stats() -> dict:
    """Return cache statistics."""
    disk_files = list(CACHE_DIR.glob("*.json"))
    return {
        "memory_entries": len(_memory_cache),
        "disk_entries": len(disk_files),
        "disk_size_mb": round(sum(f.stat().st_size for f in disk_files) / 1048576, 2)
    }
