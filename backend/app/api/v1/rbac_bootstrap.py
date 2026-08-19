from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.core.database import get_db
from app.schemas.rbac import RoleResponse
from app.services.organization import OrganizationNotFoundError
from app.services.rbac_bootstrap import rbac_bootstrap_service

router = APIRouter(
    prefix="/rbac/bootstrap",
    tags=["SaaS - RBAC Bootstrap"],
)

DbSession = Annotated[
    Session,
    Depends(get_db),
]

RoleManager = Annotated[
    CurrentUser,
    Depends(require_permission("role.manage")),
]


@router.post(
    "/organization/{organization_id}",
    response_model=list[RoleResponse],
    status_code=status.HTTP_200_OK,
)
def bootstrap_organization_rbac(
    organization_id: int,
    db: DbSession,
    current_user: RoleManager,
) -> list[RoleResponse]:
    if organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    try:
        return list(
            rbac_bootstrap_service.bootstrap_organization(
                db,
                organization_id=current_user.organization_id,
            )
        )
    except OrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
