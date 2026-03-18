"""
Geospatial utility functions.
Provides helpers for coordinate conversions, distance calculations,
bounding box operations, and GeoJSON construction.
"""

import numpy as np
from shapely.geometry import Point, Polygon, mapping, shape
from shapely.ops import unary_union


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in meters."""
    r = 6371000
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlam = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2) ** 2
    return r * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def haversine_distance_vectorized(lat1: float, lon1: float,
                                   lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    """Vectorized haversine distance from one point to arrays of points (meters)."""
    r = 6371000
    phi1 = np.radians(lat1)
    phi2 = np.radians(lats)
    dphi = np.radians(lats - lat1)
    dlam = np.radians(lons - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2) ** 2
    return r * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def bounding_box(lat: float, lon: float, radius_m: float):
    """Return (south, west, north, east) bounding box around a point."""
    delta_lat = radius_m / 111320.0
    delta_lon = radius_m / (111320.0 * np.cos(np.radians(lat)))
    return (lat - delta_lat, lon - delta_lon, lat + delta_lat, lon + delta_lon)


def point_to_geojson(lat: float, lon: float, properties: dict = None) -> dict:
    """Convert lat/lon to a GeoJSON Feature with a Point geometry."""
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": properties or {}
    }


def polygon_to_geojson(coords: list, properties: dict = None) -> dict:
    """Convert coordinate ring to a GeoJSON Feature with a Polygon geometry."""
    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [coords]},
        "properties": properties or {}
    }


def feature_collection(features: list) -> dict:
    """Wrap a list of GeoJSON Features into a FeatureCollection."""
    return {"type": "FeatureCollection", "features": features}


def buffer_point(lat: float, lon: float, radius_m: float, segments: int = 32) -> Polygon:
    """Create a circular polygon buffer around a point (approximate, in degrees)."""
    delta_lat = radius_m / 111320.0
    delta_lon = radius_m / (111320.0 * np.cos(np.radians(lat)))
    angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)
    coords = [(lon + delta_lon * np.cos(a), lat + delta_lat * np.sin(a)) for a in angles]
    coords.append(coords[0])
    return Polygon(coords)


def polygon_area_sq_km(polygon) -> float:
    """Estimate area of a shapely polygon in square km (approximate for small areas)."""
    centroid = polygon.centroid
    lat_factor = 111.32
    lon_factor = 111.32 * np.cos(np.radians(centroid.y))
    coords = np.array(polygon.exterior.coords)
    scaled = coords.copy()
    scaled[:, 0] = coords[:, 0] * lon_factor
    scaled[:, 1] = coords[:, 1] * lat_factor
    scaled_poly = Polygon(scaled)
    return scaled_poly.area


def merge_polygons(polygons: list):
    """Merge a list of shapely polygons into a single geometry."""
    return unary_union(polygons)


def geometry_to_geojson(geom, properties: dict = None) -> dict:
    """Convert any shapely geometry to a GeoJSON Feature."""
    return {
        "type": "Feature",
        "geometry": mapping(geom),
        "properties": properties or {}
    }
