# City Digital Twin - Usage and Analysis Guide

Welcome to the **City Digital Twin** Disaster Simulation Platform. This document provides a comprehensive analysis of the underlying simulation engines, the UI components, data structures, and how to use the platform effectively. It details the scientific models used for the Flood and Earthquake scenarios and explains the visualizations (such as the grid and colors) used on the interactive map map.

---

## 1. The Grid System
The simulation engine heavily relies on a **raster-based grid system** derived from Digital Elevation Models (DEM) and OpenStreetMap data. 
- **Elevation Grid**: The terrain is represented as a 2D matrix (`grid`) of elevation values corresponding to specific latitude and longitude boundaries (`lat_edges` and `lon_edges`).
- **Flow Accumulation grids**: For flood routing, the simulation calculates the simple gradient of the terrain and routes water downstream into low areas.
- **Raster to Vector**: Once simulation calculations (like flood depth or peak ground acceleration) are computed over the continuous grid in numpy, they are vectorized (converted to polygons) using the `raster_to_polygons` utility so they can be smoothly visualized inside the Mapbox frontend.

The Mapbox frontend uses the dark-v11 map style as its base canvas, projecting these grids dynamically over 3D extruded building models.

---

## 2. Flood Scenario Analysis
The Flood Simulator is capable of running two principal modes: **Rainfall-Runoff (SCS Curve Number)** and **Bathtub (Static Water Level)**.

### Rainfall-Runoff Model
- **Scientific Basis**: Utilizes the USDA SCS Curve Number methodology. A *Curve Number* (range 30-98) defines the soil permeability and land cover (e.g., concrete has a high curve number, absorbing less water).
- **Runoff Calculation**: Translates total rainfall (in mm) over a defined duration (hours) into a surface runoff volume, accounting for initial abstraction (water intercepted by vegetation or small depressions).
- **Topographic Distribution**: This calculated runoff is then distributed over the DEM grid. The `calculate_runoff_scs` calculates total runoff, and `distribute_runoff_on_dem` routes it downhill, accumulating water in lower elevations based on the local gradient.

### Bathtub Model (Static Water Level)
- In this model, the user provides a direct reference water elevation (e.g., 5.0 meters). 
- The system simply subtracts the actual terrain elevation from this water plane. Any location where the terrain is below the water level is instantaneously simulated as flooded.

### Visual Representation of Water (The Blue Colors)
Flood zones are displayed using a transparent fill layer (`fill-color`) over the map, categorized by `depth_category`. The blue tones signify the depth of the water:
- **Shallow (`shallow`)**: Rendered as a light sky blue (`rgba(135, 206, 250, 0.4)`). These are areas with minimal inundation (<0.1m to 0.5m), causing slight disruption but minor structural damage.
- **Moderate (`moderate`)**: Rendered as royal blue (`rgba(65, 105, 225, 0.5)`). Depth typically between 0.5m to 1.5m. Vehicles may float, and ground floors are flooded.
- **Deep (`deep`)**: Rendered as a navy blue variant (`rgba(25, 25, 112, 0.6)`). Highly dangerous water levels, often causing extensive damage to single-story homes.
- **Very Deep (`very_deep`)**: Rendered as dark midnight blue (`rgba(10, 10, 60, 0.75)`). Catastrophic flooding.

These polygons gradually animate in (`fill-opacity` fade-in) for a dynamic visual effect when a simulation runs.

---

## 3. Earthquake Scenario Analysis
The Earthquake Simulator is deterministic and utilizes established seismic attenuation models and fragility curves.

### Seismic Waves and PGA
- **Parameters**: The user dictates the epicenter location (by clicking on the map), Moment Magnitude (`Mw`), and Fault Depth (`km`).
- **Attenuation Model**: The system calculates the Peak Ground Acceleration (PGA) in units of `g` (gravity) at every grid cell and building coordinates using a Boore-Atkinson-based logarithmic distance decay relationship. 
- **Soil Amplification**: Buildings located on soft soils have multiplier effects applied to their localized PGA compared to buildings on solid rock.

### Structural Fragility
The system employs HAZUS fragility curves. These curves define the probability of different structural states being exceeded.
- Different structural classes (e.g., Unreinforced Masonry `URM`, Concrete `C1`, Wood `W1`) have different tolerance metrics.
- A log-normal cumulative distribution function checks the local PGA against the median PGA tolerance for Slight, Moderate, Extensive, or Complete damage states.

### Visual Representation of Damage
Buildings are extruded into full 3D prisms (`fill-extrusion`) based on the number of `floors`. After an earthquake (or flood) simulation, the building color represents its calculated `damage_state`:
- **None (`none`)**: Vibrant Green (`#22c55e`). The structure is fundamentally undisturbed and safe.
- **Slight (`slight`)**: Lime Green (`#84cc16`). Non-structural interior or exterior cosmetic damage, but structurally sound.
- **Moderate (`moderate`)**: Yellow/Gold (`#eab308`). Evident structural damage requiring repair.
- **Extensive (`extensive`)**: Orange (`#f97316`). Severe damage, partial localized collapse, uninhabitable without major reconstruction.
- **Complete (`complete`)**: Red (`#ef4444`). Total structural collapse or damage so severe the building must be demolished.

---

## 4. Cascading Effects and AI Risk Scoring

### Cascading Infra Failure
- **Road Network Analysis**: The platform evaluates flood depths over road segments. If `flood_depth > 0.3m`, the road segment is considered `blocked` and colored red on the map.
- **Isolated Facilities**: By comparing blocked roads against critical infrastructure (Hospitals, Shelters, Fire Stations), the platform uses graph-algorithms and probabilistic checks to identify facilities that are structurally undamaged but entirely inaccessible to the populace.

### XGBoost AI Predictor
- Under the hood, a pre-trained XGBoost regression model takes the physics outputs (like flood_depth and pga_g) and combines them with structural metadata (material, age, building area).
- It generates a holistic `risk_score` (0-100) per building. This AI score drives the data populated when you click on an individual building to inspect its risk profile.

### Emergency Optimization
- A greedy set-cover algorithm evaluates the highest-risk buildings and optimally positions rescue response vehicles or shelters such that the coverage radius encapsulates the highest volume of high-risk citizens.

---

## 5. Step-by-Step Usage Guide

1. **Start the Engine**: Run `python backend/main.py`. The server hosts the frontend static files on port 8000 and exposes the REST API.
2. **Navigate the Map**: Access `http://localhost:8000`. Select your desired city (e.g., Chennai, Mumbai) from the sidebar. The UI will fly to the coordinates and fetch the pre-processed synthetic or OSM layout.
3. **Configure Flood Scenario**:
   - Open the FLOOD tab.
   - Adjust Rainfall (mm), Storm Duration (hours), and Soil Permeability (Curve Number).
   - Click "Simulate". Wait ~5 seconds for the grid matrices to compute and the blue polygons to render.
4. **Configure Earthquake Scenario**:
   - Open the EARTHQUAKE tab.
   - Adjust Magnitude and Depth.
   - Click directly on the map surface to drop the epicenter marker (represented by a pulsating red wave circle).
   - Click "Simulate". Watch the 3D buildings recalculate their colors from Green to combinations of Yellow, Orange, and Red depending on proximity.
5. **Analyze Results**:
   - Review the generated Top Level Statistics (e.g., "30% Roads Blocked").
   - Click on any building geometry to see its granular Risk Score computed by the AI.
   - Click "Optimize Emergency Resources" in the toolkit pane to watch the algorithm drop coverage zones over the most affected regions.

*This guide ensures users can thoroughly understand the technical depths, scientific formulas, and user-interface representations baked into the City Digital Twin platform.*
