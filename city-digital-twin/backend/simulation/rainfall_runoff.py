"""
Rainfall-runoff calculator using SCS Curve Number method.
Computes surface runoff from rainfall events for flood simulation.
"""

import numpy as np
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def calculate_runoff_scs(rainfall_mm: float, curve_number: float,
                          duration_hours: float = 6.0) -> dict:
    """
    Calculate surface runoff using SCS Curve Number method.

    Args:
        rainfall_mm: Total rainfall in millimeters
        curve_number: SCS curve number (60-98)
        duration_hours: Storm duration in hours

    Returns:
        Dictionary with runoff depth, peak discharge, and hydrograph data
    """
    cn = np.clip(curve_number, 30, 98)
    s_mm = (25400.0 / cn) - 254.0
    ia = 0.2 * s_mm
    if rainfall_mm <= ia:
        runoff_mm = 0.0
    else:
        runoff_mm = ((rainfall_mm - ia) ** 2) / (rainfall_mm - ia + s_mm)
    runoff_fraction = runoff_mm / max(rainfall_mm, 0.001)
    c_runoff = 0.278
    area_km2 = 10.0
    intensity_mm_hr = rainfall_mm / max(duration_hours, 0.1)
    peak_discharge_m3s = c_runoff * intensity_mm_hr * area_km2 * runoff_fraction
    hydrograph = _generate_hydrograph(peak_discharge_m3s, duration_hours)
    logger.info(f"SCS runoff: P={rainfall_mm}mm, CN={cn}, Q={runoff_mm:.1f}mm, "
                f"Qp={peak_discharge_m3s:.1f}m³/s")
    return {
        "rainfall_mm": rainfall_mm,
        "curve_number": cn,
        "retention_mm": round(s_mm, 2),
        "initial_abstraction_mm": round(ia, 2),
        "runoff_mm": round(runoff_mm, 2),
        "runoff_fraction": round(runoff_fraction, 4),
        "peak_discharge_m3s": round(peak_discharge_m3s, 2),
        "duration_hours": duration_hours,
        "hydrograph": hydrograph,
    }


def _generate_hydrograph(peak_discharge: float, duration_hours: float,
                           steps: int = 24) -> list:
    """Generate a synthetic unit hydrograph (SCS triangular)."""
    time_to_peak = duration_hours * 0.6
    recession_time = duration_hours * 1.67
    total_time = time_to_peak + recession_time
    times = np.linspace(0, total_time, steps)
    discharge = np.zeros(steps)
    for i, t in enumerate(times):
        if t <= time_to_peak:
            discharge[i] = peak_discharge * (t / time_to_peak) if time_to_peak > 0 else 0
        else:
            elapsed = t - time_to_peak
            discharge[i] = peak_discharge * max(0, 1 - elapsed / recession_time)
    return [{"time_hours": round(float(t), 2), "discharge_m3s": round(float(q), 2)}
            for t, q in zip(times, discharge)]


def distribute_runoff_on_dem(runoff_mm: float, elevation: np.ndarray,
                              flow_accumulation: np.ndarray = None) -> np.ndarray:
    """
    Distribute runoff across a DEM grid based on elevation and flow accumulation.
    Returns a 2D flood depth grid in meters.
    """
    rows, cols = elevation.shape
    runoff_m = runoff_mm / 1000.0
    if flow_accumulation is None:
        flow_accumulation = _simple_flow_accumulation(elevation)
    norm_accum = flow_accumulation / max(np.max(flow_accumulation), 1.0)
    elev_normalized = 1.0 - (elevation - np.min(elevation)) / max(np.ptp(elevation), 0.001)
    flood_propensity = 0.6 * elev_normalized + 0.4 * norm_accum
    flood_depth = flood_propensity * runoff_m * 5.0
    from scipy.ndimage import gaussian_filter
    flood_depth = gaussian_filter(flood_depth, sigma=2.0)
    flood_depth = np.clip(flood_depth, 0, None)
    return flood_depth


def _simple_flow_accumulation(elevation: np.ndarray) -> np.ndarray:
    """Simplified flow accumulation using gradient-based approach."""
    from scipy.ndimage import gaussian_filter
    smoothed = gaussian_filter(elevation, sigma=1.0)
    dy, dx = np.gradient(smoothed)
    gradient_mag = np.sqrt(dx ** 2 + dy ** 2)
    inv_gradient = 1.0 / (gradient_mag + 0.001)
    low_areas = np.max(smoothed) - smoothed
    accumulation = inv_gradient * low_areas
    accumulation = gaussian_filter(accumulation, sigma=2.0)
    return accumulation


def calculate_time_of_concentration(area_km2: float, slope_pct: float,
                                      length_m: float) -> float:
    """Calculate time of concentration using Kirpich formula (minutes)."""
    if slope_pct <= 0 or length_m <= 0:
        return 30.0
    tc = 0.0195 * (length_m ** 0.77) * (slope_pct / 100.0) ** (-0.385)
    return round(max(tc, 5.0), 2)
