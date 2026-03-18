"""
Graph analysis module.
Provides connectivity analysis, isolation detection, and
critical segment identification for the road network.
"""

import numpy as np
import networkx as nx
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def analyze_connectivity(graph: nx.Graph) -> dict:
    """
    Analyze overall connectivity of the road network.

    Returns metrics about connected components, network efficiency,
    and accessibility.
    """
    passable_edges = [(u, v) for u, v, d in graph.edges(data=True) if d.get("passable", True)]
    blocked_edges = [(u, v) for u, v, d in graph.edges(data=True) if not d.get("passable", True)]
    total_edges = graph.number_of_edges()
    blocked_pct = (len(blocked_edges) / max(total_edges, 1)) * 100
    if passable_edges:
        subgraph = graph.edge_subgraph(passable_edges).copy()
        components = list(nx.connected_components(subgraph))
        largest_component = max(components, key=len) if components else set()
    else:
        components = []
        largest_component = set()
    return {
        "total_nodes": graph.number_of_nodes(),
        "total_edges": total_edges,
        "passable_edges": len(passable_edges),
        "blocked_edges": len(blocked_edges),
        "blocked_percentage": round(blocked_pct, 1),
        "connected_components": len(components),
        "largest_component_size": len(largest_component),
        "network_fragmentation": round(1.0 - len(largest_component) / max(graph.number_of_nodes(), 1), 3),
    }


def find_isolated_facilities(graph: nx.Graph, facilities_geojson: dict) -> list:
    """
    Find facilities that are unreachable through the passable road network.

    A facility is considered isolated if it's not in the largest
    connected component of the passable network.
    """
    passable_edges = [(u, v) for u, v, d in graph.edges(data=True) if d.get("passable", True)]
    if not passable_edges:
        return facilities_geojson.get("features", [])
    subgraph = graph.edge_subgraph(passable_edges).copy()
    components = list(nx.connected_components(subgraph))
    if not components:
        return facilities_geojson.get("features", [])
    largest = max(components, key=len)
    isolated = []
    for feature in facilities_geojson.get("features", []):
        coords = feature.get("geometry", {}).get("coordinates", [])
        if len(coords) < 2:
            continue
        nearest_node = _find_nearest_node(graph, coords[0], coords[1])
        if nearest_node is None or nearest_node not in largest:
            feature_copy = dict(feature)
            props = dict(feature_copy.get("properties", {}))
            props["isolated"] = True
            feature_copy["properties"] = props
            isolated.append(feature_copy)
    logger.info(f"Found {len(isolated)} isolated facilities")
    return isolated


def find_critical_segments(graph: nx.Graph, top_n: int = 10) -> list:
    """
    Identify the most critical road segments.

    A segment is critical if removing it significantly increases
    the number of disconnected components.
    """
    passable_edges = [(u, v) for u, v, d in graph.edges(data=True) if d.get("passable", True)]
    if not passable_edges:
        return []
    subgraph = graph.edge_subgraph(passable_edges).copy()
    base_components = nx.number_connected_components(subgraph)
    criticality = []
    edges_to_check = list(subgraph.edges(data=True))
    sample_size = min(len(edges_to_check), 200)
    rng = np.random.RandomState(42)
    sampled_indices = rng.choice(len(edges_to_check), sample_size, replace=False)
    for idx in sampled_indices:
        u, v, data = edges_to_check[idx]
        test_graph = subgraph.copy()
        test_graph.remove_edge(u, v)
        new_components = nx.number_connected_components(test_graph)
        if new_components > base_components:
            criticality.append({
                "edge": [list(u), list(v)],
                "road_id": data.get("road_id", ""),
                "name": data.get("name", "unnamed"),
                "highway": data.get("highway", ""),
                "components_added": new_components - base_components,
                "criticality_score": round((new_components - base_components) /
                                          max(base_components, 1) * 100, 1),
            })
    criticality.sort(key=lambda x: x["components_added"], reverse=True)
    return criticality[:top_n]


def shortest_path_to_facility(graph: nx.Graph, start_lat: float, start_lon: float,
                                 facility_type: str, facilities_geojson: dict) -> dict:
    """Find the shortest path from a point to the nearest facility of a given type."""
    start_node = _find_nearest_node(graph, start_lon, start_lat)
    if start_node is None:
        return {"found": False, "message": "Could not find starting node"}
    target_facilities = [f for f in facilities_geojson.get("features", [])
                        if f["properties"].get("type") == facility_type]
    if not target_facilities:
        return {"found": False, "message": f"No {facility_type} facilities found"}
    best_path = None
    best_distance = float("inf")
    best_facility = None
    for facility in target_facilities:
        coords = facility["geometry"]["coordinates"]
        target_node = _find_nearest_node(graph, coords[0], coords[1])
        if target_node is None:
            continue
        try:
            path = nx.shortest_path(graph, start_node, target_node, weight="length")
            distance = nx.shortest_path_length(graph, start_node, target_node, weight="length")
            if distance < best_distance:
                best_distance = distance
                best_path = path
                best_facility = facility
        except nx.NetworkXNoPath:
            continue
    if best_path is None:
        return {"found": False, "message": f"No reachable {facility_type} found"}
    return {
        "found": True,
        "facility": best_facility["properties"],
        "distance_m": round(best_distance, 1),
        "path": [list(node) for node in best_path],
    }


def _find_nearest_node(graph: nx.Graph, lon: float, lat: float):
    """Find the graph node nearest to the given coordinates."""
    min_dist = float("inf")
    nearest = None
    for node in graph.nodes():
        dist = (node[0] - lon) ** 2 + (node[1] - lat) ** 2
        if dist < min_dist:
            min_dist = dist
            nearest = node
    return nearest
