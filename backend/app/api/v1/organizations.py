from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.core.database import get_db
from app.schemas.organization import (
    OrganizationResponse,
    OrganizationUpdate,
)
from app.services.organization import (
    OrganizationNotFoundError,
    organization_service,
)

router = APIRouter(
    prefix="/organizations",
    tags=["SaaS - Organizations"],
)

DbSession = Annotated[
    Session,
    Depends(get_db),
]

OrganizationReader = Annotated[
    CurrentUser,
    Depends(require_permission("organization.read")),
]

OrganizationManager = Annotated[
    CurrentUser,
    Depends(require_permission("organization.manage")),
]


def _require_current_organization(
    *,
    requested_organization_id: int,
    current_organization_id: int,
) -> None:
    if requested_organization_id != current_organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )


@router.get(
    "",
    response_model=list[OrganizationResponse],
    status_code=status.HTTP_200_OK,
)
def list_organizations(
    db: DbSession,
    current_user: OrganizationReader,
    active_only: bool = Query(default=False),
) -> list[OrganizationResponse]:
    try:
        organization = organization_service.get(
            db,
            current_user.organization_id,
        )
    except OrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if active_only and not organization.active:
        return []

    return [organization]


@router.get(
    "/code/{organization_code}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
def get_organization_by_code(
    organization_code: str,
    db: DbSession,
    current_user: OrganizationReader,
) -> OrganizationResponse:
    try:
        organization = organization_service.get(
            db,
            current_user.organization_id,
        )
    except OrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if organization.organization_code != organization_code.strip().upper():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    return organization


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
def get_organization(
    organization_id: int,
    db: DbSession,
    current_user: OrganizationReader,
) -> OrganizationResponse:
    _require_current_organization(
        requested_organization_id=organization_id,
        current_organization_id=current_user.organization_id,
    )

    try:
        return organization_service.get(
            db,
            current_user.organization_id,
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
    current_user: OrganizationManager,
) -> OrganizationResponse:
    _require_current_organization(
        requested_organization_id=organization_id,
        current_organization_id=current_user.organization_id,
    )

    try:
        return organization_service.update(
            db,
            organization_id=current_user.organization_id,
            organization_in=request,
        )
    except OrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
