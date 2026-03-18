"""
Download OpenStreetMap data for a city.
Fetches road network and building footprints and caches them locally.
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data.osm_processor import fetch_buildings, fetch_roads, fetch_facilities
from backend.config import RAW_DIR


def main():
    """Download OSM data for the specified city."""
    city_name = sys.argv[1] if len(sys.argv) > 1 else "mumbai"
    output_dir = RAW_DIR / "osm"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading OSM data for {city_name}...")

    print(f"  Fetching buildings...")
    buildings = fetch_buildings(city_name)
    buildings_path = output_dir / f"{city_name}_buildings.geojson"
    with open(buildings_path, "w") as f:
        json.dump(buildings, f, indent=2)
    print(f"  Saved {len(buildings.get('features', []))} buildings")

    print(f"  Fetching roads...")
    roads = fetch_roads(city_name)
    roads_path = output_dir / f"{city_name}_roads.geojson"
    with open(roads_path, "w") as f:
        json.dump(roads, f, indent=2)
    print(f"  Saved {len(roads.get('features', []))} road segments")

    print(f"  Fetching facilities...")
    facilities = fetch_facilities(city_name)
    facilities_path = output_dir / f"{city_name}_facilities.geojson"
    with open(facilities_path, "w") as f:
        json.dump(facilities, f, indent=2)
    print(f"  Saved {len(facilities.get('features', []))} facilities")

    print(f"\nOSM data download complete for {city_name}!")
    print(f"Files saved to: {output_dir}")


if __name__ == "__main__":
    main()
