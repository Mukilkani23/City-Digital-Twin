"""
DEM (Digital Elevation Model) processor.
Generates synthetic elevation data when real DEM tiles are unavailable.
Uses Perlin-like noise to create realistic terrain with hills, valleys, and drainage.
"""

import numpy as np
from backend.utils.logger import get_logger
from backend.config import CITY_CONFIGS

logger = get_logger(__name__)


def get_dem(city_name: str, resolution: int = 100) -> dict:
    """Get a DEM grid for a city, generating synthetic terrain as primary method."""
    config = CITY_CONFIGS.get(city_name.lower(), CITY_CONFIGS["mumbai"])
    lat, lon, radius = config["lat"], config["lon"], config["radius"]
    delta = radius / 111320.0
    south, north = lat - delta, lat + delta
    west, east = lon - delta, lon + delta
    elevation = generate_synthetic_dem(south, west, north, east, resolution, city_name)
    lat_edges = np.linspace(south, north, resolution + 1)
    lon_edges = np.linspace(west, east, resolution + 1)
    return {
        "elevation": elevation.tolist(),
        "lat_edges": lat_edges.tolist(),
        "lon_edges": lon_edges.tolist(),
        "resolution": resolution,
        "bounds": {"south": south, "west": west, "north": north, "east": east},
        "stats": {
            "min_elevation": float(np.min(elevation)),
            "max_elevation": float(np.max(elevation)),
            "mean_elevation": float(np.mean(elevation)),
        }
    }


def generate_synthetic_dem(south: float, west: float, north: float, east: float,
                            resolution: int = 100, city_name: str = "default") -> np.ndarray:
    """Generate a synthetic DEM using multi-octave noise for realistic terrain."""
    seed = sum(ord(c) for c in city_name)
    rng = np.random.RandomState(seed)
    elevation = np.zeros((resolution, resolution))
    base_elevation = _city_base_elevation(city_name)
    y = np.linspace(0, 1, resolution)
    x = np.linspace(0, 1, resolution)
    xx, yy = np.meshgrid(x, y)
    for octave in range(4):
        freq = 2 ** (octave + 1)
        amplitude = 15.0 / (2 ** octave)
        phase_x = rng.uniform(0, 2 * np.pi)
        phase_y = rng.uniform(0, 2 * np.pi)
        elevation += amplitude * np.sin(freq * xx * np.pi + phase_x) * np.cos(freq * yy * np.pi + phase_y)
    num_hills = rng.randint(3, 8)
    for _ in range(num_hills):
        cx, cy = rng.uniform(0.1, 0.9), rng.uniform(0.1, 0.9)
        height = rng.uniform(5, 25)
        width = rng.uniform(0.1, 0.3)
        elevation += height * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * width ** 2))
    num_valleys = rng.randint(2, 5)
    for _ in range(num_valleys):
        start_x, start_y = rng.uniform(0, 0.3), rng.uniform(0, 1)
        end_x, end_y = rng.uniform(0.7, 1), rng.uniform(0, 1)
        for t in np.linspace(0, 1, 50):
            vx = start_x + t * (end_x - start_x) + rng.uniform(-0.02, 0.02)
            vy = start_y + t * (end_y - start_y) + rng.uniform(-0.02, 0.02)
            dist = np.sqrt((xx - vx) ** 2 + (yy - vy) ** 2)
            elevation -= 3.0 * np.exp(-dist ** 2 / 0.005)
    elevation += base_elevation
    elevation = np.clip(elevation, 0, None)
    from scipy.ndimage import gaussian_filter
    elevation = gaussian_filter(elevation, sigma=1.5)
    return elevation


def _city_base_elevation(city_name: str) -> float:
    """Return approximate base elevation for known cities."""
    elevations = {
        "mumbai": 10.0,
        "chennai": 6.0,
        "kolkata": 9.0,
        "delhi": 216.0,
        "jakarta": 8.0,
    }
    return elevations.get(city_name.lower(), 15.0)


def compute_slope(elevation: np.ndarray, cell_size: float = 30.0) -> np.ndarray:
    """Compute terrain slope in degrees from elevation grid."""
    dy, dx = np.gradient(elevation, cell_size)
    slope_rad = np.arctan(np.sqrt(dx ** 2 + dy ** 2))
    return np.degrees(slope_rad)


def compute_flow_direction(elevation: np.ndarray) -> np.ndarray:
    """Compute simplified D8 flow direction from elevation grid."""
    rows, cols = elevation.shape
    flow_dir = np.zeros_like(elevation, dtype=int)
    padded = np.pad(elevation, 1, mode="edge")
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for i in range(rows):
        for j in range(cols):
            pi, pj = i + 1, j + 1
            min_elev = padded[pi, pj]
            min_dir = 0
            for k, (di, dj) in enumerate(directions):
                neighbor_elev = padded[pi + di, pj + dj]
                if neighbor_elev < min_elev:
                    min_elev = neighbor_elev
                    min_dir = k + 1
            flow_dir[i, j] = min_dir
    return flow_dir


def compute_flow_accumulation(elevation: np.ndarray) -> np.ndarray:
    """Compute flow accumulation using vectorized approach."""
    rows, cols = elevation.shape
    flat_idx = np.arange(rows * cols)
    flat_elev = elevation.flatten()
    sorted_idx = np.argsort(-flat_elev)
    accumulation = np.ones(rows * cols, dtype=float)
    padded = np.pad(elevation, 1, mode="constant", constant_values=np.inf)
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for idx in sorted_idx:
        i, j = divmod(idx, cols)
        pi, pj = i + 1, j + 1
        min_elev = padded[pi, pj]
        min_ni, min_nj = -1, -1
        for di, dj in directions:
            ni, nj = pi + di, pj + dj
            if padded[ni, nj] < min_elev:
                min_elev = padded[ni, nj]
                min_ni, min_nj = i + di, j + dj
        if 0 <= min_ni < rows and 0 <= min_nj < cols:
            target_idx = min_ni * cols + min_nj
            accumulation[target_idx] += accumulation[idx]
    return accumulation.reshape(rows, cols)
