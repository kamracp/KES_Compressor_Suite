from fastapi import FastAPI

from app.api.v1.compressed_air_report import router as compressed_air_report_router

from app.api.v1.compressed_air_assessments import router as compressed_air_assessments_router

from app.api.v1.compressed_air_advanced import router as compressed_air_advanced_router

from app.api.v1.compressed_air_brownfield import router as compressed_air_brownfield_router

from app.api.v1.compressed_air_greenfield import router as compressed_air_greenfield_router
from app.api.v1.compressed_air_standards import router as compressed_air_standards_router

from app.api.v1.calculation_cases import router as calculation_cases_router
from app.api.v1.compressor_calculations import router as compressor_router
from app.api.v1.compressor_execution import router as compressor_execution_router
from app.api.v1.pdf_report import router as pdf_report_router
from app.api.v1.pdf_report_v2 import router as pdf_report_v2_router
from app.api.v1.project_history import router as project_history_router
from app.api.v1.projects import router as projects_router
from app.api.v1.report_export import router as report_export_router
from app.api.v1.reporting import router as reporting_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(
    projects_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    compressor_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    calculation_cases_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    compressor_execution_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    reporting_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    project_history_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    report_export_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    pdf_report_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    pdf_report_v2_router,
    prefix=settings.api_v1_prefix,
)


app.include_router(
    compressed_air_greenfield_router,
    prefix=settings.api_v1_prefix,
)


app.include_router(
    compressed_air_brownfield_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    compressed_air_standards_router,
    prefix=settings.api_v1_prefix,
)


app.include_router(
    compressed_air_advanced_router,
    prefix=settings.api_v1_prefix,
)


app.include_router(
    compressed_air_assessments_router,
    prefix=settings.api_v1_prefix,
)


app.include_router(
    compressed_air_report_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
    }


@app.get("/api/v1/version")
def version() -> dict[str, str]:
    return {
        "version": settings.app_version,
        "environment": settings.environment,
    }
