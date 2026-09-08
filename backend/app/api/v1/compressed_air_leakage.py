from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.permissions import require_permission
from app.core.database import get_db
from app.domain.compressed_air.energy.leakage_energy import (
    InvalidLeakageEnergyInputError,
)
from app.domain.compressed_air.leakage.leakage_analysis import (
    InvalidLeakageManagementInputError,
)
from app.schemas.compressed_air_leak_lifecycle import (
    CompressedAirLeakAssignRequest,
    CompressedAirLeakCloseRequest,
    CompressedAirLeakCreateRequest,
    CompressedAirLeakKpiSnapshotCreateRequest,
    CompressedAirLeakKpiSnapshotResponse,
    CompressedAirLeakListResponse,
    CompressedAirLeakResponse,
    CompressedAirLeakStatusHistoryResponse,
)
from app.schemas.compressed_air_leakage import (
    CompressedAirLeakageManagementRequest,
    CompressedAirLeakageManagementResponse,
)
from app.services.compressed_air_leak_lifecycle import (
    CompressedAirLeakNotFoundError,
    CompressedAirLeakProjectNotFoundError,
    DuplicateCompressedAirLeakCodeError,
    DuplicateCompressedAirLeakKpiSnapshotCodeError,
    InvalidCompressedAirLeakTransitionError,
    compressed_air_leak_lifecycle_service,
)
from app.services.compressed_air_leakage import (
    compressed_air_leakage_service,
)

router = APIRouter(
    prefix="/compressed-air/leakage",
    tags=["Compressed Air - Leakage Management"],
)

DbSession = Annotated[Session, Depends(get_db)]

LeakLifecycleReader = Annotated[
    CurrentUser,
    Depends(require_permission("assessment.read")),
]

LeakLifecycleWriter = Annotated[
    CurrentUser,
    Depends(require_permission("assessment.write")),
]


@router.post(
    "/analyze",
    response_model=CompressedAirLeakageManagementResponse,
    status_code=status.HTTP_200_OK,
)
def analyze_compressed_air_leakage(
    request: CompressedAirLeakageManagementRequest,
) -> CompressedAirLeakageManagementResponse:
    """Analyze a compressed-air leakage register and repair opportunity."""

    try:
        return compressed_air_leakage_service.analyze(request)

    except (
        InvalidLeakageManagementInputError,
        InvalidLeakageEnergyInputError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.post(
    "/projects/{project_id}/records",
    response_model=CompressedAirLeakResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_compressed_air_leak(
    project_id: int,
    request: CompressedAirLeakCreateRequest,
    db: DbSession,
    current_user: LeakLifecycleWriter,
) -> CompressedAirLeakResponse:
    """Tag one persistent compressed-air leak within a project."""

    try:
        return compressed_air_leak_lifecycle_service.create(
            db,
            organization_id=current_user.organization_id,
            project_id=project_id,
            request=request,
            actor=current_user.email,
        )
    except CompressedAirLeakProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DuplicateCompressedAirLeakCodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/projects/{project_id}/records",
    response_model=CompressedAirLeakListResponse,
)
def list_compressed_air_leaks(
    project_id: int,
    db: DbSession,
    current_user: LeakLifecycleReader,
) -> CompressedAirLeakListResponse:
    """List the tenant-scoped leakage lifecycle register."""

    try:
        return compressed_air_leak_lifecycle_service.list_by_project(
            db,
            organization_id=current_user.organization_id,
            project_id=project_id,
        )
    except CompressedAirLeakProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/records/{leak_id}",
    response_model=CompressedAirLeakResponse,
)
def get_compressed_air_leak(
    leak_id: int,
    db: DbSession,
    current_user: LeakLifecycleReader,
) -> CompressedAirLeakResponse:
    """Get one tenant-scoped compressed-air leak."""

    try:
        return compressed_air_leak_lifecycle_service.get_by_id(
            db,
            organization_id=current_user.organization_id,
            leak_id=leak_id,
        )
    except CompressedAirLeakNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/records/{leak_id}/assign",
    response_model=CompressedAirLeakResponse,
)
def assign_compressed_air_leak(
    leak_id: int,
    request: CompressedAirLeakAssignRequest,
    db: DbSession,
    current_user: LeakLifecycleWriter,
) -> CompressedAirLeakResponse:
    """Transition one leak from TAGGED to ASSIGNED."""

    try:
        return compressed_air_leak_lifecycle_service.assign(
            db,
            organization_id=current_user.organization_id,
            leak_id=leak_id,
            request=request,
            actor=current_user.email,
        )
    except CompressedAirLeakNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidCompressedAirLeakTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.patch(
    "/records/{leak_id}/close",
    response_model=CompressedAirLeakResponse,
)
def close_compressed_air_leak(
    leak_id: int,
    request: CompressedAirLeakCloseRequest,
    db: DbSession,
    current_user: LeakLifecycleWriter,
) -> CompressedAirLeakResponse:
    """Transition one leak from ASSIGNED to CLOSED."""

    try:
        return compressed_air_leak_lifecycle_service.close(
            db,
            organization_id=current_user.organization_id,
            leak_id=leak_id,
            request=request,
            actor=current_user.email,
        )
    except CompressedAirLeakNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidCompressedAirLeakTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/records/{leak_id}/history",
    response_model=tuple[CompressedAirLeakStatusHistoryResponse, ...],
)
def list_compressed_air_leak_history(
    leak_id: int,
    db: DbSession,
    current_user: LeakLifecycleReader,
) -> tuple[CompressedAirLeakStatusHistoryResponse, ...]:
    """List immutable lifecycle transitions for one leak."""

    try:
        return compressed_air_leak_lifecycle_service.list_status_history(
            db,
            organization_id=current_user.organization_id,
            leak_id=leak_id,
        )
    except CompressedAirLeakNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/records/{leak_id}/kpi-snapshots",
    response_model=CompressedAirLeakKpiSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_compressed_air_leak_kpi_snapshot(
    leak_id: int,
    request: CompressedAirLeakKpiSnapshotCreateRequest,
    db: DbSession,
    current_user: LeakLifecycleWriter,
) -> CompressedAirLeakKpiSnapshotResponse:
    """Capture one historical KPI snapshot for a leak."""

    try:
        return compressed_air_leak_lifecycle_service.create_kpi_snapshot(
            db,
            organization_id=current_user.organization_id,
            leak_id=leak_id,
            request=request,
            actor=current_user.email,
        )
    except CompressedAirLeakNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DuplicateCompressedAirLeakKpiSnapshotCodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/records/{leak_id}/kpi-snapshots",
    response_model=tuple[CompressedAirLeakKpiSnapshotResponse, ...],
)
def list_compressed_air_leak_kpi_snapshots(
    leak_id: int,
    db: DbSession,
    current_user: LeakLifecycleReader,
) -> tuple[CompressedAirLeakKpiSnapshotResponse, ...]:
    """List historical KPI snapshots for one leak."""

    try:
        return compressed_air_leak_lifecycle_service.list_kpi_snapshots(
            db,
            organization_id=current_user.organization_id,
            leak_id=leak_id,
        )
    except CompressedAirLeakNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
