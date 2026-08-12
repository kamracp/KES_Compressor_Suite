from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.core.database import get_db
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project import (
    ProjectAlreadyExistsError,
    ProjectNotFoundError,
    project_service,
)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]

ProjectReader = Annotated[
    CurrentUser,
    Depends(require_permission("project.read")),
]

ProjectWriter = Annotated[
    CurrentUser,
    Depends(require_permission("project.write")),
]


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    payload: ProjectCreate,
    db: DatabaseSession,
    current_user: ProjectWriter,
) -> ProjectRead:
    try:
        return project_service.create_project(
            db,
            organization_id=current_user.organization_id,
            payload=payload,
        )
    except ProjectAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[ProjectRead],
)
def list_projects(
    db: DatabaseSession,
    current_user: ProjectReader,
) -> list[ProjectRead]:
    return project_service.list_projects(
        db,
        organization_id=current_user.organization_id,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
)
def get_project(
    project_id: int,
    db: DatabaseSession,
    current_user: ProjectReader,
) -> ProjectRead:
    try:
        return project_service.get_project(
            db,
            organization_id=current_user.organization_id,
            project_id=project_id,
        )
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: DatabaseSession,
    current_user: ProjectWriter,
) -> ProjectRead:
    try:
        return project_service.update_project(
            db,
            organization_id=current_user.organization_id,
            project_id=project_id,
            payload=payload,
        )
    except ProjectAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: int,
    db: DatabaseSession,
    current_user: ProjectWriter,
) -> Response:
    try:
        project_service.delete_project(
            db,
            organization_id=current_user.organization_id,
            project_id=project_id,
        )
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
