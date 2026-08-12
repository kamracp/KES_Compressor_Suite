from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.core.database import get_db
from app.schemas.project_history import ProjectCalculationHistoryResponse
from app.services.project_history import (
    ProjectHistoryProjectNotFoundError,
    project_history_service,
)

router = APIRouter(
    prefix="/projects",
    tags=["Project Calculation History"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]

ProjectHistoryReader = Annotated[
    CurrentUser,
    Depends(require_permission("project.read")),
]


@router.get(
    "/{project_id}/calculation-history",
    response_model=ProjectCalculationHistoryResponse,
)
def get_project_calculation_history(
    project_id: int,
    db: DatabaseSession,
    current_user: ProjectHistoryReader,
) -> ProjectCalculationHistoryResponse:
    try:
        return project_history_service.get_project_history(
            db,
            organization_id=current_user.organization_id,
            project_id=project_id,
        )
    except ProjectHistoryProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
