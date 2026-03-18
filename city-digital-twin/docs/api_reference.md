# API Reference

## Base URL

```
http://localhost:8000
```

## Health Check

### `GET /health`

Returns server health status.

**Response:**
```json
{"status": "healthy", "service": "city-digital-twin", "version": "1.0.0"}
```

---

## City Data

### `GET /api/v1/city/list`

List all available cities.

### `GET /api/v1/city/{city_name}/infrastructure`

Get all infrastructure data for a city (buildings, roads, facilities).

**Parameters:** `city_name` — one of: `mumbai`, `chennai`, `kolkata`, `delhi`, `jakarta`

### `GET /api/v1/city/{city_name}/risk-baseline`

Get baseline risk profile without any active disaster.

---

## Flood Simulation

### `POST /api/v1/simulate/flood`

Run rainfall-based flood simulation.

**Request Body:**
```json
{
    "city_name": "mumbai",
    "rainfall_mm": 150.0,
    "duration_hours": 6.0,
    "curve_number": 80.0
}
```

**Response:** Flood zones GeoJSON, building damage list, statistics, road damage, risk scores.

### `POST /api/v1/simulate/flood/bathtub`

Fast bathtub flood simulation for animation.

**Request Body:**
```json
{
    "city_name": "mumbai",
    "water_level_m": 5.0
}
```

---

## Earthquake Simulation

### `POST /api/v1/simulate/earthquake`

Run earthquake simulation with PGA calculation and HAZUS fragility curves.

**Request Body:**
```json
{
    "city_name": "mumbai",
    "magnitude": 6.5,
    "epicenter_lat": 19.076,
    "epicenter_lon": 72.877,
    "depth_km": 15.0
}
```

---

## Resource Optimization

### `POST /api/v1/optimize/resources`

Optimize emergency resource placement using greedy coverage algorithm.

**Request Body:**
```json
{
    "building_damage": [...],
    "num_resources": 5,
    "coverage_radius_m": 1500.0,
    "resource_type": "rescue_team"
}
```

---

## Error Format

All errors return:
```json
{
    "error": true,
    "message": "Description of what went wrong",
    "code": "ERROR_CODE"
}
```
