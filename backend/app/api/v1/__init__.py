from fastapi import APIRouter

from app.api.v1.demand import router as demand_router
from app.api.v1.rotary_screw import router as rotary_screw_router
from app.api.v1.multi_compressor import router as multi_compressor_router
from app.api.v1.air_dryer import router as air_dryer_router
from app.api.v1.receiver_piping import router as receiver_piping_router
from app.api.v1.system_orchestrator import router as system_orchestrator_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(demand_router)
api_router.include_router(rotary_screw_router)
api_router.include_router(multi_compressor_router)
api_router.include_router(air_dryer_router)
api_router.include_router(receiver_piping_router)
api_router.include_router(system_orchestrator_router)
