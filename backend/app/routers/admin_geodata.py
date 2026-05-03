"""Endpoints administration des versions geodata."""

from __future__ import annotations

import asyncio
import tempfile
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import async_session, get_db
from app.core.rate_limit import limiter
from app.core.security import get_current_admin_user
from app.models.geodata_version import GeodataVersion
from app.models.user import User
from app.schemas.geodata import (
    GeodataActivateResponse,
    GeodataAuthor,
    GeodataJobAccepted,
    GeodataJobStatus,
    GeodataUploadResponse,
    GeodataVersionDetail,
    GeodataVersionList,
    GeodataVersionListItem,
)
from app.services import audit_log as audit_service
from app.services import geodata_jobs, geodata_service
from app.services.geodata_pipeline import PipelineResult, run_pipeline


def _err(code: str, message: str) -> dict:
    return {"code": code, "message": message}

router = APIRouter(
    prefix="/api/admin/geodata/regions",
    tags=["admin-geodata"],
)

settings = get_settings()
ALLOWED_EXTENSIONS = {".geojson", ".json"}
ALLOWED_MIME = {
    "application/json",
    "application/geo+json",
    "text/json",
    "application/octet-stream",
}


def _ext(filename: str) -> str:
    return Path(filename or "").suffix.lower()


async def _hydrate_list_item(
    db: AsyncSession, version: GeodataVersion
) -> GeodataVersionListItem:
    author_user = await db.get(User, version.created_by_user_id)
    author = (
        GeodataAuthor(id=author_user.id, email=author_user.email)
        if author_user
        else GeodataAuthor(id=version.created_by_user_id, email="unknown@unknown")
    )
    return GeodataVersionListItem(
        id=version.id,
        created_at=version.created_at,
        created_by=author,
        original_filename=version.original_filename,
        original_size_bytes=version.original_size_bytes,
        processed_size_bytes=version.processed_size_bytes,
        features_count=version.features_count,
        is_active=version.is_active,
        has_warnings=bool(version.warnings),
        notes=version.notes,
    )


async def _hydrate_detail(
    db: AsyncSession, version: GeodataVersion
) -> GeodataVersionDetail:
    base = await _hydrate_list_item(db, version)
    return GeodataVersionDetail(
        **base.model_dump(),
        region_names=list(version.region_names or []),
        warnings=list(version.warnings or []),
        geojson_processed=version.geojson_processed,
    )


def _run_pipeline_blocking(
    file_path: str, known_region_names: set[str] | None = None
) -> PipelineResult:
    return run_pipeline(
        file_path,
        aliases=settings.GEODATA_NAME_ALIASES,
        region_code_prefix=settings.GEODATA_REGION_CODE_PREFIX,
        simplify_ratio=settings.GEODATA_SIMPLIFY_RATIO,
        min_feature_area_deg2=settings.GEODATA_MIN_FEATURE_AREA_DEG2,
        coordinate_precision=settings.GEODATA_COORDINATE_PRECISION,
        expected_min=settings.GEODATA_FEATURES_MIN_WARN,
        expected_max=settings.GEODATA_FEATURES_MAX_WARN,
        known_region_names_normalized=known_region_names,
    )


async def _process_async(
    job_id: uuid.UUID,
    file_path: str,
    user_id: uuid.UUID,
    original_filename: str,
    original_size: int,
    notes: str | None,
    known_region_names: set[str] | None = None,
):
    await geodata_jobs.update_status(job_id, status="running")
    try:
        loop = asyncio.get_event_loop()
        pipeline_result = await loop.run_in_executor(
            None, _run_pipeline_blocking, file_path, known_region_names
        )
        if not pipeline_result.features:
            await geodata_jobs.update_status(
                job_id, status="failed", error_message="Aucune feature exploitable"
            )
            return
        async with async_session() as db:
            user = await db.get(User, user_id)
            if user is None:
                await geodata_jobs.update_status(
                    job_id,
                    status="failed",
                    error_message="Utilisateur introuvable",
                )
                return
            version = await geodata_service.create_version(
                db,
                user,
                pipeline_result,
                original_filename=original_filename,
                original_size=original_size,
                notes=notes,
                max_versions=settings.GEODATA_MAX_VERSIONS,
            )
            await audit_service.record_geodata_uploaded(db, user, version)
            await db.commit()
            await geodata_jobs.update_status(
                job_id, status="done", version_id=version.id
            )
    except Exception as exc:  # noqa: BLE001
        await geodata_jobs.update_status(
            job_id, status="failed", error_message=str(exc)
        )
    finally:
        Path(file_path).unlink(missing_ok=True)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
@limiter.limit(f"{settings.GEODATA_RATE_LIMIT_UPLOADS_PER_HOUR}/hour")
async def upload_version(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    notes: str | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    if _ext(file.filename or "") not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=_err(
                "INVALID_EXTENSION",
                "Extension non autorisée (utilisez .geojson ou .json)",
            ),
        )
    if file.content_type and file.content_type not in ALLOWED_MIME:
        raise HTTPException(
            status_code=400,
            detail=_err(
                "INVALID_MIME", f"MIME non autorisé : {file.content_type}"
            ),
        )

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".geojson")
    total = 0
    try:
        while chunk := await file.read(1024 * 1024):
            total += len(chunk)
            if total > settings.GEODATA_MAX_UPLOAD_BYTES:
                tmp.close()
                Path(tmp.name).unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail=_err(
                        "TOO_LARGE",
                        "Fichier trop volumineux (max "
                        f"{settings.GEODATA_MAX_UPLOAD_BYTES} octets)",
                    ),
                )
            tmp.write(chunk)
        tmp.close()
    except HTTPException:
        raise
    except Exception:
        tmp.close()
        Path(tmp.name).unlink(missing_ok=True)
        raise

    original_size = total
    original_filename = file.filename or "upload.geojson"

    known_names = await geodata_service.get_known_region_names_normalized(db)

    try:
        loop = asyncio.get_event_loop()
        pipeline_result = await asyncio.wait_for(
            loop.run_in_executor(
                None, _run_pipeline_blocking, tmp.name, known_names
            ),
            timeout=settings.GEODATA_SYNC_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        job = await geodata_jobs.create_job()
        background_tasks.add_task(
            _process_async,
            job.id,
            tmp.name,
            current_user.id,
            original_filename,
            original_size,
            notes,
            known_names,
        )
        return JSONResponse(
            status_code=202,
            content=GeodataJobAccepted(
                job_id=job.id,
                status="pending",
                submitted_at=job.submitted_at,
            ).model_dump(mode="json"),
        )
    except Exception as exc:  # noqa: BLE001
        Path(tmp.name).unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail=_err("INVALID_GEOJSON", f"GeoJSON invalide : {exc}"),
        )

    Path(tmp.name).unlink(missing_ok=True)

    if not pipeline_result.features:
        raise HTTPException(
            status_code=400,
            detail=_err(
                "NO_FEATURES",
                "Aucune feature region exploitable (admin_level=4 requis)",
            ),
        )

    version = await geodata_service.create_version(
        db,
        current_user,
        pipeline_result,
        original_filename=original_filename,
        original_size=original_size,
        notes=notes,
        max_versions=settings.GEODATA_MAX_VERSIONS,
    )
    await audit_service.record_geodata_uploaded(db, current_user, version)
    await db.commit()
    await db.refresh(version)

    return GeodataUploadResponse(
        version_id=version.id,
        uploaded_at=version.created_at,
        original_filename=version.original_filename,
        original_size_bytes=version.original_size_bytes,
        processed_size_bytes=version.processed_size_bytes,
        features_count=version.features_count,
        region_names=list(version.region_names or []),
        warnings=list(version.warnings or []),
        notes=version.notes,
    )


@router.get("/jobs/{job_id}", response_model=GeodataJobStatus)
async def get_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_admin_user),
):
    job = await geodata_jobs.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job inconnu ou expiré")
    return GeodataJobStatus(
        job_id=job.id,
        status=job.status,
        submitted_at=job.submitted_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        version_id=job.version_id,
        error_message=job.error_message,
    )


@router.get("/versions", response_model=GeodataVersionList)
async def list_versions(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    limit = max(1, min(limit, 50))
    offset = max(0, offset)
    versions, total = await geodata_service.list_versions(
        db, limit=limit, offset=offset
    )
    items = [await _hydrate_list_item(db, v) for v in versions]
    return GeodataVersionList(items=items, total=total)


@router.get("/versions/{version_id}", response_model=GeodataVersionDetail)
async def get_version(
    version_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    version = await geodata_service.get_version(db, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Version inconnue")
    return await _hydrate_detail(db, version)


@router.delete("/versions/{version_id}", status_code=204)
async def delete_version(
    version_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    version = await geodata_service.get_version(db, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Version inconnue")
    if version.is_active:
        raise HTTPException(
            status_code=409, detail="Impossible de supprimer la version active"
        )
    snapshot = version
    await geodata_service.delete_version(db, version_id)
    await audit_service.record_geodata_deleted(db, current_user, snapshot)
    await db.commit()
    return JSONResponse(status_code=204, content=None)


@router.post("/versions/{version_id}/activate", response_model=GeodataActivateResponse)
async def activate_version(
    version_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    previous = await geodata_service.get_active_version(db)
    previous_id = previous.id if previous else None
    activated = await geodata_service.activate_version(db, version_id)
    await audit_service.record_geodata_activated(
        db, current_user, activated, previous_active_id=previous_id
    )
    await db.commit()
    await db.refresh(activated)
    detail = await _hydrate_detail(db, activated)
    return GeodataActivateResponse(**detail.model_dump())
