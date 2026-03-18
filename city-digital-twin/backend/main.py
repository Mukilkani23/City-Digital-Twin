"""
City Digital Twin - Main FastAPI Application.
Entry point for the backend server. Wires all routes,
serves the frontend, and handles startup tasks.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from backend.utils.logger import get_logger
from backend.config import HOST, PORT, DEBUG

logger = get_logger("city-digital-twin")

app = FastAPI(
    title="City Digital Twin",
    description="Disaster Simulation Platform for urban infrastructure analysis",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.api.routes.flood import router as flood_router
from backend.api.routes.earthquake import router as earthquake_router
from backend.api.routes.infrastructure import router as infrastructure_router
from backend.api.routes.scenarios import router as scenarios_router
from backend.api.routes.resources import router as resources_router

app.include_router(flood_router)
app.include_router(earthquake_router)
app.include_router(infrastructure_router)
app.include_router(scenarios_router)
app.include_router(resources_router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("=" * 60)
    logger.info("City Digital Twin - Starting up...")
    logger.info("=" * 60)
    logger.info("Pre-loading data and training ML model...")
    try:
        from backend.data.city_loader import preload_sample_city
        preload_sample_city()
        logger.info("Sample city data pre-loaded")
    except Exception as e:
        logger.warning(f"Sample data pre-load skipped: {e}")
    try:
        from backend.ml.damage_predictor import get_model
        get_model()
        logger.info("ML damage prediction model ready")
    except Exception as e:
        logger.warning(f"ML model init skipped: {e}")
    logger.info("=" * 60)
    logger.info(f"Server ready at http://localhost:{PORT}")
    logger.info("=" * 60)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "city-digital-twin", "version": "1.0.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "An internal server error occurred",
            "code": "INTERNAL_ERROR",
        }
    )


frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/src", StaticFiles(directory=str(frontend_dir / "src")), name="src")

    @app.get("/")
    async def serve_frontend():
        """Serve the frontend index.html."""
        index_path = frontend_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return JSONResponse({"error": True, "message": "Frontend not found"}, status_code=404)


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {HOST}:{PORT}")
    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info",
    )
