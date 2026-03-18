"""
Generate sample GeoJSON data for offline demo.
Creates realistic building, road, and facility datasets for a fictional city.
"""

import json
import sys
import os
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data.osm_processor import (
    generate_synthetic_buildings,
    generate_synthetic_roads,
    generate_synthetic_facilities,
)


def main():
    """Generate and save sample GeoJSON data."""
    output_dir = PROJECT_ROOT / "data" / "sample"
    output_dir.mkdir(parents=True, exist_ok=True)

    cities = {
        "mumbai": {"lat": 19.076, "lon": 72.8777, "radius": 3000},
        "chennai": {"lat": 13.0827, "lon": 80.2707, "radius": 3000},
    }

    for city_name, config in cities.items():
        print(f"\n{'=' * 50}")
        print(f"Generating sample data for {city_name.title()}...")
        print(f"{'=' * 50}")

        print(f"  Generating 500 buildings...")
        buildings = generate_synthetic_buildings(
            config["lat"], config["lon"], config["radius"], count=500
        )
        buildings_path = output_dir / f"{city_name}_buildings.geojson"
        with open(buildings_path, "w") as f:
            json.dump(buildings, f, indent=2)
        print(f"  Saved {len(buildings['features'])} buildings to {buildings_path}")

        print(f"  Generating road network...")
        roads = generate_synthetic_roads(
            config["lat"], config["lon"], config["radius"], grid_size=15
        )
        roads_path = output_dir / f"{city_name}_roads.geojson"
        with open(roads_path, "w") as f:
            json.dump(roads, f, indent=2)
        print(f"  Saved {len(roads['features'])} road segments to {roads_path}")

        print(f"  Generating emergency facilities...")
        facilities = generate_synthetic_facilities(
            config["lat"], config["lon"], config["radius"]
        )
        facilities_path = output_dir / f"{city_name}_facilities.geojson"
        with open(facilities_path, "w") as f:
            json.dump(facilities, f, indent=2)
        print(f"  Saved {len(facilities['features'])} facilities to {facilities_path}")

    print(f"\nSample data generation complete!")
    print(f"Files saved to: {output_dir}")


if __name__ == "__main__":
    main()
