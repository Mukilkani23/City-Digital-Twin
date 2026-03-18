"""Tests for graph analysis module."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import networkx as nx


def test_build_road_graph():
    """Test road graph construction from GeoJSON."""
    from backend.data.city_loader import load_city
    from backend.graph.infrastructure_graph import build_road_graph
    city = load_city("mumbai")
    graph = build_road_graph(city["roads"])
    assert isinstance(graph, nx.Graph)
    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0


def test_connectivity_analysis():
    """Test connectivity analysis returns valid metrics."""
    from backend.data.city_loader import load_city
    from backend.graph.infrastructure_graph import build_road_graph
    from backend.graph.graph_analysis import analyze_connectivity
    city = load_city("mumbai")
    graph = build_road_graph(city["roads"])
    connectivity = analyze_connectivity(graph)
    assert "total_nodes" in connectivity
    assert "blocked_percentage" in connectivity
    assert connectivity["blocked_percentage"] == 0.0


def test_find_critical_segments():
    """Test critical segment identification."""
    from backend.data.city_loader import load_city
    from backend.graph.infrastructure_graph import build_road_graph
    from backend.graph.graph_analysis import find_critical_segments
    city = load_city("mumbai")
    graph = build_road_graph(city["roads"])
    critical = find_critical_segments(graph, top_n=5)
    assert isinstance(critical, list)
    for seg in critical:
        assert "road_id" in seg
        assert "criticality_score" in seg


def test_resource_optimizer():
    """Test resource optimization produces valid placements."""
    from backend.graph.resource_optimizer import optimize_resource_placement
    buildings = [
        {"id": f"b{i}", "lat": 19.0 + i*0.001, "lon": 72.8 + i*0.001,
         "damage_state": "moderate", "building_type": "residential"}
        for i in range(20)
    ]
    result = optimize_resource_placement(buildings, num_resources=3)
    assert result["total_resources"] == 3
    assert len(result["placements"]) == 3
    assert result["coverage_percentage"] >= 0


if __name__ == "__main__":
    test_build_road_graph()
    test_connectivity_analysis()
    test_find_critical_segments()
    test_resource_optimizer()
    print("All graph analysis tests passed!")
