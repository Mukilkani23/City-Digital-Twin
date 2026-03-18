"""
Download DEM (Digital Elevation Model) data for a city.
Generates synthetic DEM as the primary method since real DEM
data sources require authentication or are not freely available.
"""

import sys
import json
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data.dem_processor import get_dem
from backend.config import RAW_DIR


def main():
    """Generate DEM data for the specified city."""
    city_name = sys.argv[1] if len(sys.argv) > 1 else "mumbai"
    output_dir = RAW_DIR / "dem"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating DEM data for {city_name}...")

    dem_data = get_dem(city_name, resolution=100)

    dem_path = output_dir / f"{city_name}_dem.json"
    with open(dem_path, "w") as f:
        json.dump(dem_data, f)
    print(f"  Saved DEM grid ({len(dem_data['elevation'])}x{len(dem_data['elevation'][0])})")
    print(f"  Elevation range: {dem_data['stats']['min_elevation']:.1f}m - "
          f"{dem_data['stats']['max_elevation']:.1f}m")
    print(f"  Mean elevation: {dem_data['stats']['mean_elevation']:.1f}m")

    print(f"\nDEM data saved to: {dem_path}")


if __name__ == "__main__":
    main()
