# Datasets

## Data Sources

### OpenStreetMap (via osmnx)
- **Buildings**: Footprint polygons with building type, height, levels
- **Roads**: Street network with road classification and geometry
- **Facilities**: Hospitals, fire stations, shelters with locations
- **Fallback**: Synthetic data generated if OSM fetch fails

### Digital Elevation Model (Synthetic)
- Generated using multi-octave sine/cosine noise
- Includes realistic hills, valleys, and drainage channels
- City-specific base elevations (e.g., Mumbai ~10m, Delhi ~216m)
- 100×100 grid resolution covering the city bounding box

### Weather Data (Synthetic)
- Pre-defined weather scenarios: monsoon, cyclone, cloudburst, moderate
- City-specific historical rainfall baselines
- Soil moisture conditions by season

## Building Attributes

Each building is enriched with:
| Attribute | Description | Source |
|-----------|-------------|--------|
| `building_type` | residential, commercial, hospital, etc. | OSM / synthetic |
| `floors` | Number of floors (1-15) | OSM `building:levels` / synthetic |
| `construction_year` | Year built (1950-2023) | OSM `start_date` / synthetic |
| `material` | reinforced_concrete, masonry, steel, wood | Synthetic |
| `soil_type` | rock, stiff_soil, soft_soil, fill | Synthetic |
| `structural_class` | HAZUS class (C1, C2, RM1, URM, S1, W1, etc.) | Synthetic |

## File Structure

```
data/
├── raw/          # Downloaded raw data
│   ├── dem/      # DEM JSON files
│   ├── osm/      # OSM GeoJSON files
│   └── weather/  # Weather data
├── processed/    # Cached processed data
│   ├── graphs/   # Serialized road graphs
│   ├── rasters/  # Processed raster data
│   └── vectors/  # Processed vector data
└── sample/       # Pre-generated sample data for offline demo
```
