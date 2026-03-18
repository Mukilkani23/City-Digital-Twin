# City-Digital-Twin
🏙️ City Digital Twin — A disaster simulation platform that lets  city planners visualize how floods and earthquakes destroy urban  infrastructure in real time. Predict building damage, find blocked  roads, locate isolated hospitals, and optimize emergency response  — before disaster strikes.


<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-ML_Engine-FF6600?style=for-the-badge)](https://xgboost.readthedocs.io)
[![Mapbox](https://img.shields.io/badge/Mapbox_GL-Maps-000000?style=for-the-badge&logo=mapbox&logoColor=white)](https://mapbox.com)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

</div>

---

## 📌 What Is This?

Cities are not prepared. When a flood hits or an earthquake strikes, emergency teams are flying blind — no simulation, no prediction, no plan.

**City Digital Twin** changes that.

It builds a living, interactive digital replica of any city. Feed it a disaster scenario. Watch it show you exactly which buildings collapse, which roads flood, which hospitals get cut off — and where to send help first.

This is not a visualization tool. It is a **decision engine**.

---

## ⚡ Quick Start (Local Python)

Follow these precise steps to run the application directly on your machine using Python.

**Step 1: Open your terminal**
Make sure your terminal is opened in the `city-digital-twin` root directory.

**Step 2: Create a Virtual Environment (Recommended)**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

**Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Generate Offline Sample Data (Optional but recommended)**
```bash
python scripts/generate_sample_data.py
```

**Step 5: Launch the Platform**
```bash
python backend/main.py
```

**Step 6: Open the Application**
Once the server starts running, open your web browser and go to:
```
http://localhost:8000
```

**What happens on first launch:**
- City data loads automatically (from OpenStreetMap or synthetic fallback)
- XGBoost damage prediction model trains itself (~20 seconds)
- Full interactive dashboard is ready to use

No database setup. No cloud account needed. No manual configuration.

---

## 🗺️ Live Demo Flow

```
1. Select a city          →  Mumbai, Chennai, Kolkata, Delhi, Jakarta
2. Choose disaster type   →  🌊 Flood  or  🌍 Earthquake
3. Set parameters         →  Rainfall intensity / Magnitude / Epicenter
4. Click Simulate         →  Watch the disaster propagate across the map
5. Read the results       →  Damaged buildings, blocked roads, isolated hospitals
6. Optimize response      →  AI places rescue teams at optimal positions
```

---

## 🔥 Core Features

### 🌊 Flood Simulation
- **Rainfall mode** — Input storm intensity (mm/hr) and duration. The system calculates surface runoff using the SCS Curve Number method, routes water downhill across the terrain, and produces a flood depth map across the entire city.
- **Bathtub mode** — Drag a water level slider and watch the city flood in real time. Perfect for animated demos.
- Buildings are classified by flood damage: Minor → Moderate → Severe → Destroyed.

### 🌍 Earthquake Simulation
- Set magnitude, epicenter (click anywhere on the map), and depth.
- Peak Ground Acceleration calculated at every building using seismic attenuation.
- HAZUS-standard fragility curves assign damage states per structural type: None → Slight → Moderate → Extensive → Complete.

### 🕸️ Infrastructure Cascade Analysis
- The road network is modeled as a graph. After a disaster, flooded or collapsed roads become impassable edges.
- The system identifies which hospitals, fire stations, and emergency shelters are now unreachable.
- Critical bridge segments are highlighted — these are the roads whose failure disconnects the most people.

### 🤖 AI Damage Prediction
- XGBoost classifier trained on building age, material, floor count, soil type, flood depth, and ground shaking.
- Every building gets a **Risk Score from 0 to 100**, visible in the building popup on the map.
- Model auto-trains on first run. No manual setup required.

### 🚁 Emergency Resource Optimizer
- After any simulation, click **Optimize Resources**.
- A greedy coverage algorithm finds the best positions to pre-stage rescue boats, ambulances, or relief teams.
- Shows coverage radius on the map and percentage of demand nodes covered.

### 📊 Scenario Comparison
- Run two scenarios side by side.
- Split-screen map with a draggable divider.
- Compare: current drainage vs upgraded drainage, before vs after infrastructure investment.

---

## 🧱 Architecture

```
┌────────────────────────────────────────────┐
│              BROWSER (Vanilla JS)                       │
│   Mapbox GL Map  │  Panels  │  Charts.js               │
└──────────────────┬──────────────────────────┘
                   │ REST API
┌──────────────────▼──────────────────────────┐
│           FastAPI Backend (Python)           │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │  Flood   │  │Earthquake│  │  Graph    │  │
│  │Simulator │  │Simulator │  │ Analysis  │  │
│  └──────────┘  └──────────┘  └───────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │      XGBoost ML Damage Predictor     │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │   Data Layer (OSM → Synthetic)       │    │
│  └──────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │   data/            │
         │   ├── raw/         │
         │   ├── processed/   │
         │   └── sample/      │
         └────────────────────┘
```

---

## 🌐 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check — confirms server is running |
| `GET` | `/api/v1/city/list` | List all available cities |
| `GET` | `/api/v1/city/{name}/infrastructure` | Roads, buildings, facilities as GeoJSON |
| `GET` | `/api/v1/city/{name}/risk-baseline` | Pre-disaster risk scores per building |
| `POST` | `/api/v1/simulate/flood` | Run full rainfall flood simulation |
| `POST` | `/api/v1/simulate/flood/bathtub` | Fast water-level flood (for animation) |
| `POST` | `/api/v1/simulate/earthquake` | Run seismic damage simulation |
| `POST` | `/api/v1/optimize/resources` | Optimal emergency resource placement |
| `POST` | `/api/v1/scenarios/save` | Save a simulation scenario |
| `POST` | `/api/v1/scenarios/compare` | Compare two saved scenarios |

Full API documentation: [`docs/api_reference.md`](docs/api_reference.md)

---

## 📁 Project Structure

```
city-digital-twin/
│
├── backend/                    # FastAPI application
│   ├── main.py                 # App entry point — start here
│   ├── config.py               # Environment config and constants
│   ├── api/
│   │   ├── routes/             # flood, earthquake, infrastructure, resources
│   │   └── schemas/            # Pydantic request/response models
│   ├── simulation/             # Flood + earthquake physics engines
│   ├── graph/                  # Road network analysis + resource optimizer
│   ├── ml/                     # XGBoost damage predictor + risk scorer
│   ├── data/                   # City loader, OSM processor, DEM generator
│   └── utils/                  # Logging, geo helpers, raster utilities
│
├── frontend/                   # Vanilla JS dashboard
│   ├── index.html              # Single page app entry
│   └── src/
│       ├── map/                # Mapbox GL layer modules
│       ├── panels/             # Sidebar control panels
│       ├── api/                # Backend API client
│       └── styles/             # CSS design system
│
├── data/
│   ├── raw/                    # Downloaded OSM and DEM files
│   ├── processed/              # Cached graphs and rasters
│   └── sample/                 # Offline demo GeoJSON (Mumbai)
│
├── scripts/                    # CLI tools for data and model management
├── docs/                       # Architecture, API, datasets, demo guide
├── requirements.txt
├── .env.example
└── docker-compose.yml
```

---

## 🔧 Environment Setup

Copy the example env file and fill in your Mapbox token:

```bash
cp .env.example .env
```

Edit `.env`:

```env
MAPBOX_TOKEN=your_mapbox_token_here
DEFAULT_CITY=Mumbai
```

Get a free Mapbox token at [mapbox.com](https://mapbox.com) — free tier covers 50,000 map loads per month. No credit card required.

---

## 📡 Offline Mode

This platform runs completely without internet if needed.

```bash
# Generate all sample data first
python scripts/generate_sample_data.py

# Then start normally — it will use local data automatically
python backend/main.py
```

The data fallback chain works like this:

```
Try OpenStreetMap (live)
      ↓ if fails
Load data/sample/ GeoJSON (pre-generated)
      ↓ if not found
Generate fully synthetic city in memory
      ↓ always works
Simulation runs successfully
```

The app will never crash due to missing data.

---

## ➕ Adding a New City

1. Open `backend/config.py` and add your city to `CITY_CONFIGS`:

```python
"tokyo": {
    "lat": 35.6762,
    "lon": 139.6503,
    "radius": 4000,
    "country": "Japan"
}
```

2. Add the city name to the dropdown in `frontend/index.html`.

3. Restart the server. Data loads automatically on first request.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.11, FastAPI, Uvicorn |
| Geospatial | GeoPandas, osmnx, Shapely, Rasterio |
| Graph Analysis | NetworkX |
| Machine Learning | XGBoost, scikit-learn, SciPy |
| Data Processing | NumPy, Pandas |
| Map Rendering | Mapbox GL JS (CDN) |
| Charts | Chart.js (CDN) |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Containerization | Docker + Docker Compose |

---

## 🚀 Docker Deployment

If you prefer using Docker to avoid installing Python dependencies locally, follow these steps:

**Step 1: Start Docker Desktop**
Ensure that Docker Desktop is actively running on your system.

**Step 2: Build and Run the Container**
Open your terminal in the `city-digital-twin` directory and run:
```bash
docker compose up --build
```
*(This will download Python, install all dependencies inside an isolated container, and start the server).*

**Step 3: Open the Application**
Once you see logs indicating the server has started, open your browser to:
```
http://localhost:8001
```
*(Note: We use port 8001 for Docker to avoid conflicts with your other existing backend services).*

---

## 🧪 Running Tests

```bash
cd city-digital-twin
python -m pytest backend/tests/ -v
```

Four test suites cover flood simulation, earthquake simulation, graph analysis, and the ML damage predictor.

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [`docs/architecture.md`](docs/architecture.md) | System design and data flow |
| [`docs/api_reference.md`](docs/api_reference.md) | Full API endpoint documentation |
| [`docs/datasets.md`](docs/datasets.md) | Data sources and download guide |
| [`docs/demo_script.md`](docs/demo_script.md) | 7-minute hackathon demo walkthrough |

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built for cities that cannot afford to wait for the next disaster to plan for it.**

</div>
