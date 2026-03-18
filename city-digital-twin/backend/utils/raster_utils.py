"""
Raster utility functions.
Provides helpers for generating, interpolating, and converting raster/grid data.
"""

import numpy as np
from shapely.geometry import Polygon, mapping


def create_grid(south: float, west: float, north: float, east: float,
                resolution: int = 100) -> tuple:
    """Create a regular lat/lon grid and return (lats, lons, lat_edges, lon_edges)."""
    lat_edges = np.linspace(south, north, resolution + 1)
    lon_edges = np.linspace(west, east, resolution + 1)
    lats = (lat_edges[:-1] + lat_edges[1:]) / 2
    lons = (lon_edges[:-1] + lon_edges[1:]) / 2
    return lats, lons, lat_edges, lon_edges


def raster_to_polygons(values: np.ndarray, lat_edges: np.ndarray,
                        lon_edges: np.ndarray, threshold: float = 0.0) -> list:
    """Convert a 2D raster array to GeoJSON polygon features where values exceed threshold."""
    features = []
    rows, cols = values.shape
    for i in range(rows):
        for j in range(cols):
            val = float(values[i, j])
            if val > threshold:
                s, n = float(lat_edges[i]), float(lat_edges[i + 1])
                w, e = float(lon_edges[j]), float(lon_edges[j + 1])
                poly = Polygon([(w, s), (e, s), (e, n), (w, n), (w, s)])
                depth_category = classify_flood_depth(val)
                features.append({
                    "type": "Feature",
                    "geometry": mapping(poly),
                    "properties": {
                        "value": round(val, 3),
                        "depth_category": depth_category
                    }
                })
    return features


def classify_flood_depth(depth: float) -> str:
    """Classify flood depth into categories."""
    if depth < 0.1:
        return "negligible"
    elif depth < 0.3:
        return "shallow"
    elif depth < 1.0:
        return "moderate"
    elif depth < 2.0:
        return "deep"
    return "very_deep"


def interpolate_grid(grid: np.ndarray, factor: int = 2) -> np.ndarray:
    """Simple bilinear upscale of a 2D grid by an integer factor."""
    from scipy.ndimage import zoom
    return zoom(grid, factor, order=1)


def apply_gaussian_smooth(grid: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """Apply Gaussian smoothing to a 2D grid."""
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(grid, sigma=sigma)


def normalize_grid(grid: np.ndarray) -> np.ndarray:
    """Normalize grid values to 0–1 range."""
    min_val = np.nanmin(grid)
    max_val = np.nanmax(grid)
    if max_val - min_val == 0:
        return np.zeros_like(grid)
    return (grid - min_val) / (max_val - min_val)


def grid_statistics(grid: np.ndarray) -> dict:
    """Return summary statistics for a 2D grid."""
    return {
        "min": float(np.nanmin(grid)),
        "max": float(np.nanmax(grid)),
        "mean": float(np.nanmean(grid)),
        "std": float(np.nanstd(grid)),
        "nonzero_count": int(np.count_nonzero(grid)),
        "total_cells": int(grid.size)
    }
