# Architecture

## System Overview

```
┌─────────────┐     HTTP/JSON      ┌──────────────────────┐
│   Frontend   │ ◄──────────────► │   FastAPI Backend     │
│  (Mapbox GL) │                   │                      │
│  (Chart.js)  │                   │  ┌────────────────┐  │
│  (Vanilla JS)│                   │  │  API Routes    │  │
└─────────────┘                   │  └───────┬────────┘  │
                                   │          │           │
                                   │  ┌───────▼────────┐  │
                                   │  │  Simulation    │  │
                                   │  │  Engine        │  │
                                   │  └───────┬────────┘  │
                                   │          │           │
                                   │  ┌───────▼────────┐  │
                                   │  │  Graph         │  │
                                   │  │  Analysis      │  │
                                   │  └───────┬────────┘  │
                                   │          │           │
                                   │  ┌───────▼────────┐  │
                                   │  │  ML Predictor  │  │
                                   │  └────────────────┘  │
                                   └──────────────────────┘
```

## Data Flow

1. **City Loading**: User selects a city → backend fetches OSM data (or falls back to synthetic) → caches in memory
2. **Simulation**: User configures parameters → backend runs flood/earthquake physics models → returns GeoJSON + damage assessments
3. **Analysis**: Infrastructure graph is built from roads → connectivity analysis identifies isolated facilities and critical segments
4. **ML Prediction**: XGBoost model scores each building with a 0-100 risk score based on hazard exposure and structural vulnerability
5. **Optimization**: Greedy set-cover algorithm places emergency resources for maximum coverage of at-risk buildings
6. **Visualization**: Frontend renders results on Mapbox dark map with 3D building extrusions, flood polygons, heatmaps, and resource markers

## Key Design Decisions

- **Synthetic data first**: All data generation works offline. OSM/DEM fetching is attempted first but synthetic fallback is always available.
- **Vectorized computation**: NumPy array operations throughout simulation for sub-10-second performance.
- **Auto-training ML**: Model trains on first startup with synthetic data (~20s) and is saved for subsequent runs.
- **Cache-first loading**: Memory cache → disk cache → sample files → OSM → synthetic generation.
