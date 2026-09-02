from fastapi import APIRouter, status

from app.api.dependencies.auth import CurrentUser
from app.schemas.reference_options import InputOptionsResponse
from app.services.reference_options import input_options

router = APIRouter(
    prefix="/reference",
    tags=["Reference - Input Options"],
)


@router.get(
    "/input-options",
    response_model=InputOptionsResponse,
    status_code=status.HTTP_200_OK,
)
def get_input_options(current_user: CurrentUser) -> InputOptionsResponse:
    del current_user
    return input_options()
