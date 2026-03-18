"""
OpenStreetMap data processor.
Fetches road networks and building footprints from OSM via osmnx,
with automatic fallback to synthetic data generation.
"""

import numpy as np
from shapely.geometry import Polygon, LineString, mapping
from backend.utils.logger import get_logger
from backend.config import CITY_CONFIGS

logger = get_logger(__name__)


def fetch_buildings(city_name: str) -> dict:
    """Fetch building footprints from OSM, falling back to synthetic data."""
    config = CITY_CONFIGS.get(city_name.lower())
    if config is None:
        logger.warning(f"Unknown city {city_name}, generating synthetic buildings")
        return generate_synthetic_buildings(19.076, 72.8777, 3000)
    try:
        import osmnx as ox
        logger.info(f"Fetching OSM buildings for {city_name}...")
        tags = {"building": True}
        gdf = ox.features_from_point(
            (config["lat"], config["lon"]),
            tags=tags,
            dist=config["radius"]
        )
        features = []
        for idx, row in gdf.iterrows():
            if row.geometry is None:
                continue
            geom = row.geometry
            if geom.geom_type == "Polygon":
                props = extract_building_properties(row, idx)
                features.append({
                    "type": "Feature",
                    "geometry": mapping(geom),
                    "properties": props
                })
        if len(features) < 10:
            raise ValueError("Too few buildings fetched")
        logger.info(f"Fetched {len(features)} buildings from OSM")
        return {"type": "FeatureCollection", "features": features[:2000]}
    except Exception as e:
        logger.warning(f"OSM fetch failed for {city_name}: {e}. Using synthetic data.")
        return generate_synthetic_buildings(config["lat"], config["lon"], config["radius"])


def extract_building_properties(row, idx) -> dict:
    """Extract and enrich building properties from an OSM row."""
    rng = np.random.RandomState(hash(str(idx)) % 2**31)
    materials = ["reinforced_concrete", "masonry", "steel", "wood"]
    soil_types = ["rock", "stiff_soil", "soft_soil", "fill"]
    structural_classes = ["C1", "C2", "C3", "RM1", "RM2", "URM", "S1", "S2", "W1", "W2"]
    floors = int(row.get("building:levels", rng.randint(1, 8)))
    year = int(row.get("start_date", rng.randint(1960, 2020)))
    return {
        "id": f"bldg_{abs(hash(str(idx))) % 100000}",
        "building_type": str(row.get("building", "residential")),
        "floors": floors,
        "construction_year": year,
        "material": rng.choice(materials),
        "soil_type": rng.choice(soil_types),
        "structural_class": rng.choice(structural_classes),
        "floor_area": round(float(row.geometry.area) * 111320 * 111320 * floors, 1),
        "height": floors * 3.0,
    }


def fetch_roads(city_name: str) -> dict:
    """Fetch road network from OSM, falling back to synthetic data."""
    config = CITY_CONFIGS.get(city_name.lower())
    if config is None:
        logger.warning(f"Unknown city {city_name}, generating synthetic roads")
        return generate_synthetic_roads(19.076, 72.8777, 3000)
    try:
        import osmnx as ox
        logger.info(f"Fetching OSM roads for {city_name}...")
        graph = ox.graph_from_point(
            (config["lat"], config["lon"]),
            dist=config["radius"],
            network_type="drive"
        )
        edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
        features = []
        for idx, row in edges.iterrows():
            geom = row.geometry
            name = row.get("name", "unnamed")
            if isinstance(name, list):
                name = name[0] if name else "unnamed"
            highway = row.get("highway", "residential")
            if isinstance(highway, list):
                highway = highway[0]
            features.append({
                "type": "Feature",
                "geometry": mapping(geom),
                "properties": {
                    "id": f"road_{len(features)}",
                    "name": str(name),
                    "highway": str(highway),
                    "length": round(float(row.get("length", geom.length * 111320)), 1),
                    "lanes": int(row.get("lanes", 2) if not isinstance(row.get("lanes"), list) else 2),
                }
            })
        if len(features) < 5:
            raise ValueError("Too few roads fetched")
        logger.info(f"Fetched {len(features)} road segments from OSM")
        return {"type": "FeatureCollection", "features": features[:3000]}
    except Exception as e:
        logger.warning(f"OSM road fetch failed for {city_name}: {e}. Using synthetic data.")
        return generate_synthetic_roads(config["lat"], config["lon"], config["radius"])


def generate_synthetic_buildings(lat: float, lon: float, radius: int, count: int = 500) -> dict:
    """Generate synthetic building footprints around a center point."""
    logger.info(f"Generating {count} synthetic buildings around ({lat}, {lon})")
    rng = np.random.RandomState(42)
    features = []
    materials = ["reinforced_concrete", "masonry", "steel", "wood"]
    soil_types = ["rock", "stiff_soil", "soft_soil", "fill"]
    structural_classes = ["C1", "C2", "C3", "RM1", "RM2", "URM", "S1", "S2", "W1", "W2"]
    building_types = ["residential", "commercial", "industrial", "hospital",
                      "school", "government", "fire_station", "shelter"]
    type_weights = [0.5, 0.2, 0.1, 0.02, 0.05, 0.05, 0.03, 0.05]
    delta = radius / 111320.0
    for i in range(count):
        clat = lat + rng.uniform(-delta, delta)
        clon = lon + rng.uniform(-delta, delta)
        size = rng.uniform(0.0001, 0.0005)
        w, h = size * rng.uniform(0.5, 1.5), size * rng.uniform(0.5, 1.5)
        coords = [
            [clon - w / 2, clat - h / 2],
            [clon + w / 2, clat - h / 2],
            [clon + w / 2, clat + h / 2],
            [clon - w / 2, clat + h / 2],
            [clon - w / 2, clat - h / 2],
        ]
        floors = int(rng.choice([1, 2, 3, 4, 5, 6, 8, 10, 15], p=[0.2, 0.2, 0.15, 0.15, 0.1, 0.08, 0.05, 0.04, 0.03]))
        btype = rng.choice(building_types, p=type_weights)
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [coords]},
            "properties": {
                "id": f"bldg_{i}",
                "building_type": btype,
                "floors": floors,
                "construction_year": int(rng.randint(1950, 2023)),
                "material": rng.choice(materials),
                "soil_type": rng.choice(soil_types),
                "structural_class": rng.choice(structural_classes),
                "floor_area": round(size * 111320 * size * 111320 * floors, 1),
                "height": floors * 3.0,
            }
        })
    return {"type": "FeatureCollection", "features": features}


def generate_synthetic_roads(lat: float, lon: float, radius: int, grid_size: int = 15) -> dict:
    """Generate a synthetic grid road network."""
    logger.info(f"Generating synthetic road grid around ({lat}, {lon})")
    rng = np.random.RandomState(42)
    features = []
    delta = radius / 111320.0
    lats = np.linspace(lat - delta, lat + delta, grid_size)
    lons = np.linspace(lon - delta, lon + delta, grid_size)
    road_id = 0
    highway_types = ["primary", "secondary", "tertiary", "residential"]
    for i, lt in enumerate(lats):
        for j in range(len(lons) - 1):
            if rng.random() < 0.85:
                line = LineString([(lons[j], lt), (lons[j + 1], lt)])
                htype = highway_types[0] if i == grid_size // 2 else rng.choice(highway_types[1:])
                features.append({
                    "type": "Feature",
                    "geometry": mapping(line),
                    "properties": {
                        "id": f"road_{road_id}",
                        "name": f"Street {road_id}",
                        "highway": htype,
                        "length": round(float(line.length * 111320), 1),
                        "lanes": 2 if htype == "residential" else 4,
                    }
                })
                road_id += 1
    for j, ln in enumerate(lons):
        for i in range(len(lats) - 1):
            if rng.random() < 0.85:
                line = LineString([(ln, lats[i]), (ln, lats[i + 1])])
                htype = highway_types[0] if j == grid_size // 2 else rng.choice(highway_types[1:])
                features.append({
                    "type": "Feature",
                    "geometry": mapping(line),
                    "properties": {
                        "id": f"road_{road_id}",
                        "name": f"Avenue {road_id}",
                        "highway": htype,
                        "length": round(float(line.length * 111320), 1),
                        "lanes": 2 if htype == "residential" else 4,
                    }
                })
                road_id += 1
    return {"type": "FeatureCollection", "features": features}


def fetch_facilities(city_name: str) -> dict:
    """Fetch or generate emergency facilities (hospitals, fire stations, shelters)."""
    config = CITY_CONFIGS.get(city_name.lower(), CITY_CONFIGS["mumbai"])
    lat, lon = config["lat"], config["lon"]
    try:
        import osmnx as ox
        hospitals_gdf = ox.features_from_point((lat, lon), tags={"amenity": "hospital"}, dist=config["radius"])
        features = []
        for idx, row in hospitals_gdf.iterrows():
            if row.geometry and row.geometry.centroid:
                c = row.geometry.centroid
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [c.x, c.y]},
                    "properties": {"type": "hospital", "name": str(row.get("name", f"Hospital {len(features)}"))}
                })
        if len(features) >= 3:
            return {"type": "FeatureCollection", "features": features}
    except Exception:
        pass
    return generate_synthetic_facilities(lat, lon, config["radius"])


def generate_synthetic_facilities(lat: float, lon: float, radius: int) -> dict:
    """Generate synthetic emergency facilities."""
    rng = np.random.RandomState(99)
    delta = radius / 111320.0
    features = []
    facility_specs = [
        ("hospital", 5, "Hospital"),
        ("fire_station", 3, "Fire Station"),
        ("shelter", 10, "Emergency Shelter"),
    ]
    for ftype, count, label in facility_specs:
        for i in range(count):
            flat = lat + rng.uniform(-delta * 0.8, delta * 0.8)
            flon = lon + rng.uniform(-delta * 0.8, delta * 0.8)
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [flon, flat]},
                "properties": {
                    "type": ftype,
                    "name": f"{label} {i + 1}",
                    "capacity": int(rng.randint(50, 500)),
                }
            })
    return {"type": "FeatureCollection", "features": features}
