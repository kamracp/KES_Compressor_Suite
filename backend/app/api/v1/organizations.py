from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.services.organization import (
    OrganizationCodeConflictError,
    OrganizationNotFoundError,
    organization_service,
)

router = APIRouter(
    prefix="/organizations",
    tags=["SaaS - Organizations"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    request: OrganizationCreate,
    db: DbSession,
) -> OrganizationResponse:
    try:
        return organization_service.create(
            db,
            request,
        )
    except OrganizationCodeConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[OrganizationResponse],
    status_code=status.HTTP_200_OK,
)
def list_organizations(
    db: DbSession,
    active_only: bool = Query(default=False),
) -> list[OrganizationResponse]:
    return list(
        organization_service.list(
            db,
            active_only=active_only,
        )
    )


@router.get(
    "/code/{organization_code}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
def get_organization_by_code(
    organization_code: str,
    db: DbSession,
) -> OrganizationResponse:
    try:
        return organization_service.get_by_code(
            db,
            organization_code,
        )
    except OrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
def get_organization(
    organization_id: int,
    db: DbSession,
) -> OrganizationResponse:
    try:
        return organization_service.get(
            db,
            organization_id,
        )
    except OrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
def update_organization(
    organization_id: int,
    request: OrganizationUpdate,
    db: DbSession,
) -> OrganizationResponse:
    try:
        return organization_service.update(
            db,
            organization_id=organization_id,
            organization_in=request,
        )
    except OrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
