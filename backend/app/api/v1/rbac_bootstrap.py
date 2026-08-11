from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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


@router.post(
    "/organization/{organization_id}",
    response_model=list[RoleResponse],
    status_code=status.HTTP_200_OK,
)
def bootstrap_organization_rbac(
    organization_id: int,
    db: DbSession,
) -> list[RoleResponse]:
    try:
        return list(
            rbac_bootstrap_service.bootstrap_organization(
                db,
                organization_id=organization_id,
            )
        )
    except OrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
