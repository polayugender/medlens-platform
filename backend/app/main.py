from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.db.session import init_db
from app.api.routes_patients import router as patients_router
from app.api.routes_intake import router as intake_router
from app.api.routes_reports import router as reports_router
from app.api.routes_extraction import router as extraction_router
from app.api.routes_summary import router as summary_router
from app.api.routes_audit import router as audit_router
from app.api.routes_analytics import router as analytics_router
from app.api.routes_system import router as system_router
from app.api.routes_auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and tables
    await init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="MedLens AI-Powered Clinical Information Intelligence Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount local storage for reports and preview images
app.mount("/storage/reports", StaticFiles(directory=str(settings.REPORTS_DIR)), name="reports")
app.mount("/storage/previews", StaticFiles(directory=str(settings.PREVIEWS_DIR)), name="previews")

# Include Routers
app.include_router(patients_router, prefix=settings.API_V1_STR)
app.include_router(intake_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(extraction_router, prefix=settings.API_V1_STR)
app.include_router(summary_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(system_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "system": "MedLens Clinical Information Intelligence",
        "version": "1.0.0",
        "storage_ready": settings.REPORTS_DIR.exists()
    }
