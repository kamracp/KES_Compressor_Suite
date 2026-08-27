from app.api.v1.demand import router as demand_router
from app.api.v1.rotary_screw import router as rotary_screw_router
from app.api.v1.multi_compressor import router as multi_compressor_router
from app.api.v1.air_dryer import router as air_dryer_router
from app.api.v1.receiver_piping import router as receiver_piping_router
from app.api.v1.system_orchestrator import router as system_orchestrator_router
from app.api.v1.demand import router as demand_router
from app.api.v1.rotary_screw import router as rotary_screw_router
from app.api.v1.multi_compressor import router as multi_compressor_router
from app.api.v1.air_dryer import router as air_dryer_router
from app.api.v1.receiver_piping import router as receiver_piping_router
from app.api.v1.system_orchestrator import router as system_orchestrator_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.calculation_cases import router as calculation_cases_router
from app.api.v1.compressed_air_advanced import router as compressed_air_advanced_router
from app.api.v1.compressed_air_allied import router as compressed_air_allied_router
from app.api.v1.compressed_air_assessments import router as compressed_air_assessments_router
from app.api.v1.compressed_air_brownfield import router as compressed_air_brownfield_router
from app.api.v1.compressed_air_greenfield import router as compressed_air_greenfield_router
from app.api.v1.compressed_air_leakage import router as compressed_air_leakage_router
from app.api.v1.compressed_air_performance import router as compressed_air_performance_router
from app.api.v1.compressed_air_report import router as compressed_air_report_router
from app.api.v1.compressed_air_skid import router as compressed_air_skid_router
from app.api.v1.compressed_air_standards import router as compressed_air_standards_router
from app.api.v1.compressed_air_system_summary import router as compressed_air_system_summary_router
from app.api.v1.compressor_calculations import router as compressor_router
from app.api.v1.compressor_execution import router as compressor_execution_router
from app.api.v1.gas_properties import router as gas_properties_router
from app.api.v1.organizations import router as organizations_router
from app.api.v1.pdf_report import router as pdf_report_router
from app.api.v1.pdf_report_v2 import router as pdf_report_v2_router
from app.api.v1.project_history import router as project_history_router
from app.api.v1.projects import router as projects_router
from app.api.v1.rbac import router as rbac_router
from app.api.v1.rbac_bootstrap import router as rbac_bootstrap_router
from app.api.v1.report_export import router as report_export_router
from app.api.v1.reporting import router as reporting_router
from app.api.v1.users import router as users_router
from app.core.config import get_settings

settings = get_settings()



app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5175", "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    auth_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    organizations_router,
    prefix=settings.api_v1_prefix,
)


app.include_router(
    users_router,
    prefix=settings.api_v1_prefix,
)


app.include_router(
    rbac_router,
    prefix=settings.api_v1_prefix,
)


app.include_router(
    rbac_bootstrap_router,
    prefix=settings.api_v1_prefix,
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
    gas_properties_router,
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
    compressed_air_performance_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    compressed_air_leakage_router,
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
    compressed_air_allied_router,
    prefix=settings.api_v1_prefix,
)


app.include_router(
    compressed_air_skid_router,
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


app.include_router(
    compressed_air_system_summary_router,
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




# --- Compressed Air Engine Routers Registration ---



# --- Registered Compressor Engine Routers ---


# --- Compressed Air Engine Routers Registration ---
from app.api.v1.demand import router as demand_router
from app.api.v1.rotary_screw import router as rotary_screw_router
from app.api.v1.multi_compressor import router as multi_compressor_router
from app.api.v1.air_dryer import router as air_dryer_router
from app.api.v1.receiver_piping import router as receiver_piping_router
from app.api.v1.system_orchestrator import router as system_orchestrator_router

app.include_router(demand_router, prefix="/api/v1", tags=["Demand Calculations"])
app.include_router(rotary_screw_router, prefix="/api/v1", tags=["Rotary Screw Engine"])
app.include_router(multi_compressor_router, prefix="/api/v1", tags=["Multi-Compressor Engine"])
app.include_router(air_dryer_router, prefix="/api/v1", tags=["Air Dryer Engine"])
app.include_router(receiver_piping_router, prefix="/api/v1", tags=["Receiver & Piping Engine"])
app.include_router(system_orchestrator_router, prefix="/api/v1", tags=["System Orchestrator Engine"])

# Compressed Air Engine Sub-Routers
app.include_router(demand_router, prefix=settings.api_v1_prefix)
app.include_router(rotary_screw_router, prefix=settings.api_v1_prefix)
app.include_router(multi_compressor_router, prefix=settings.api_v1_prefix)
app.include_router(air_dryer_router, prefix=settings.api_v1_prefix)
app.include_router(receiver_piping_router, prefix=settings.api_v1_prefix)
app.include_router(system_orchestrator_router, prefix=settings.api_v1_prefix)

# Compressed Air Engine Sub-Routers
app.include_router(demand_router, prefix=settings.api_v1_prefix)
app.include_router(rotary_screw_router, prefix=settings.api_v1_prefix)
app.include_router(multi_compressor_router, prefix=settings.api_v1_prefix)
app.include_router(air_dryer_router, prefix=settings.api_v1_prefix)
app.include_router(receiver_piping_router, prefix=settings.api_v1_prefix)
app.include_router(system_orchestrator_router, prefix=settings.api_v1_prefix)
