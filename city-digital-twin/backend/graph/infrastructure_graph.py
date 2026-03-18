"""
Infrastructure graph builder.
Constructs a NetworkX graph from road network GeoJSON data
for connectivity analysis and pathfinding.
"""

import numpy as np
import networkx as nx
from shapely.geometry import shape, LineString
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def build_road_graph(roads_geojson: dict) -> nx.Graph:
    """
    Build a NetworkX graph from road GeoJSON features.

    Nodes represent intersections (road endpoints),
    Edges represent road segments with length and metadata.
    """
    graph = nx.Graph()
    features = roads_geojson.get("features", [])
    logger.info(f"Building road graph from {len(features)} road segments")
    for feature in features:
        coords = feature.get("geometry", {}).get("coordinates", [])
        if len(coords) < 2:
            continue
        props = feature.get("properties", {})
        start = tuple(round(c, 6) for c in coords[0][:2])
        end = tuple(round(c, 6) for c in coords[-1][:2])
        length = props.get("length", _calculate_edge_length(coords))
        highway = props.get("highway", "residential")
        speed = _road_speed(highway)
        graph.add_node(start, lon=start[0], lat=start[1])
        graph.add_node(end, lon=end[0], lat=end[1])
        graph.add_edge(start, end,
                       road_id=props.get("id", "unknown"),
                       name=props.get("name", "unnamed"),
                       highway=highway,
                       length=length,
                       lanes=props.get("lanes", 2),
                       speed_kmh=speed,
                       travel_time=length / (speed * 1000 / 3600) if speed > 0 else float("inf"),
                       passable=True,
                       flood_depth=0.0)
    logger.info(f"Road graph built: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    return graph


def _calculate_edge_length(coords: list) -> float:
    """Calculate approximate length of a polyline in meters."""
    total = 0.0
    for i in range(len(coords) - 1):
        dx = (coords[i + 1][0] - coords[i][0]) * 111320 * np.cos(np.radians(coords[i][1]))
        dy = (coords[i + 1][1] - coords[i][1]) * 111320
        total += np.sqrt(dx ** 2 + dy ** 2)
    return round(total, 1)


def _road_speed(highway: str) -> float:
    """Return typical speed in km/h for a road type."""
    speeds = {
        "motorway": 80, "trunk": 60, "primary": 50,
        "secondary": 40, "tertiary": 30, "residential": 20,
        "service": 15, "unclassified": 25,
    }
    return speeds.get(highway, 25)


def update_graph_after_flood(graph: nx.Graph, road_damage: list) -> nx.Graph:
    """Update edge passability based on flood damage assessment."""
    damage_map = {r["id"]: r for r in road_damage}
    blocked_count = 0
    for u, v, data in graph.edges(data=True):
        road_id = data.get("road_id", "")
        if road_id in damage_map:
            rd = damage_map[road_id]
            data["passable"] = not rd.get("blocked", False)
            data["flood_depth"] = rd.get("flood_depth", 0.0)
            if not data["passable"]:
                blocked_count += 1
    logger.info(f"Graph updated: {blocked_count} roads blocked")
    return graph


def update_graph_after_earthquake(graph: nx.Graph, building_damage: list,
                                     roads_geojson: dict) -> nx.Graph:
    """Update edge passability based on earthquake damage near roads."""
    damaged_locs = set()
    for bldg in building_damage:
        if bldg.get("damage_state") in ("extensive", "complete"):
            damaged_locs.add((round(bldg["lon"], 4), round(bldg["lat"], 4)))
    blocked_count = 0
    for u, v, data in graph.edges(data=True):
        mid_lon = (u[0] + v[0]) / 2
        mid_lat = (u[1] + v[1]) / 2
        near_damage = any(
            abs(loc[0] - mid_lon) < 0.002 and abs(loc[1] - mid_lat) < 0.002
            for loc in damaged_locs
        )
        if near_damage:
            data["passable"] = False
            blocked_count += 1
    logger.info(f"Post-earthquake: {blocked_count} roads blocked by debris")
    return graph


def get_passable_subgraph(graph: nx.Graph) -> nx.Graph:
    """Return a subgraph containing only passable edges."""
    passable_edges = [(u, v) for u, v, d in graph.edges(data=True) if d.get("passable", True)]
    return graph.edge_subgraph(passable_edges).copy()


def graph_to_geojson(graph: nx.Graph) -> dict:
    """Convert graph edges to GeoJSON for visualization."""
    features = []
    for u, v, data in graph.edges(data=True):
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [list(u), list(v)]
            },
            "properties": {
                "road_id": data.get("road_id", ""),
                "name": data.get("name", ""),
                "highway": data.get("highway", ""),
                "passable": data.get("passable", True),
                "flood_depth": data.get("flood_depth", 0.0),
                "length": data.get("length", 0),
            }
        })
    return {"type": "FeatureCollection", "features": features}
