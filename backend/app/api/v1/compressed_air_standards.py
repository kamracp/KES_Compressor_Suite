from fastapi import APIRouter, status

from app.schemas.compressed_air_standards import (
    StandardsRuleQueryRequest,
    StandardsRulesResponse,
)
from app.services.compressed_air_standards import (
    compressed_air_standards_service,
)

router = APIRouter(
    prefix="/compressed-air/standards",
    tags=["Compressed Air - Standards & Compliance"],
)


@router.post(
    "/query",
    response_model=StandardsRulesResponse,
    status_code=status.HTTP_200_OK,
)
def query_compressed_air_standards(
    request: StandardsRuleQueryRequest,
) -> StandardsRulesResponse:
    """Query the controlled compressed-air standards rule registry."""

    return compressed_air_standards_service.query_rules(request)
