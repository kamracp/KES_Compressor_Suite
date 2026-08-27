from fastapi import APIRouter, Depends
from app.api.dependencies.permissions import require_permission
from app.services.receiver_piping import (
    ReceiverPipingInput,
    ReceiverPipingOutput,
    receiver_piping_engine,
)

router = APIRouter(prefix="/receiver-piping", tags=["Air Receiver & Piping Infrastructure"])

@router.post("/size", response_model=ReceiverPipingOutput)
def size_receiver_and_piping(
    payload: ReceiverPipingInput,
    _user = Depends(require_permission("project.read")),
):
    return receiver_piping_engine.calculate(payload)
