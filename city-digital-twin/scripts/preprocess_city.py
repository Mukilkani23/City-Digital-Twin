"""
Preprocess city data for all available cities.
Downloads OSM data and generates DEM for each configured city.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data.city_loader import load_city
from backend.config import CITY_CONFIGS


def main():
    """Preprocess data for all configured cities."""
    cities = list(CITY_CONFIGS.keys())

    if len(sys.argv) > 1:
        cities = [sys.argv[1].lower()]

    print("=" * 60)
    print("City Data Preprocessing")
    print("=" * 60)

    for city_name in cities:
        print(f"\nProcessing {city_name.title()}...")
        try:
            city_data = load_city(city_name)
            stats = city_data["stats"]
            print(f"  Buildings: {stats['building_count']}")
            print(f"  Roads: {stats['road_count']}")
            print(f"  Facilities: {stats['facility_count']}")
            print(f"  DEM: {len(city_data['dem']['elevation'])}x"
                  f"{len(city_data['dem']['elevation'][0])}")
            print(f"  Status: OK")
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nPreprocessing complete for {len(cities)} cities!")


if __name__ == "__main__":
    main()
