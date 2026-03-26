import uuid
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.security import require_role
from app.models.user import User

router = APIRouter(prefix="/api/admin/upload", tags=["upload"])
settings = get_settings()


def _get_upload_dir() -> Path:
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def _validate_content_type(content_type: str | None) -> str:
    if not content_type or content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "success": 0,
                "detail": "Type de fichier non autorisé. "
                "Types acceptés : jpeg, png, webp, gif",
            },
        )
    return content_type


def _get_extension(content_type: str) -> str:
    extensions = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    return extensions.get(content_type, ".bin")


class ImageByUrlRequest(BaseModel):
    url: str


@router.post("/image")
async def upload_image(
    image: UploadFile,
    current_user: User = Depends(require_role("admin", "editor")),
):
    _validate_content_type(image.content_type)

    content = await image.read()
    if len(content) > settings.MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail={
                "success": 0,
                "detail": "Le fichier dépasse la taille maximale autorisée (5 MB)",
            },
        )

    ext = _get_extension(image.content_type)
    filename = f"{uuid.uuid4()}{ext}"
    upload_dir = _get_upload_dir()
    file_path = upload_dir / filename
    file_path.write_bytes(content)

    return {
        "success": 1,
        "file": {"url": f"/uploads/images/{filename}"},
    }


@router.post("/image-by-url")
async def upload_image_by_url(
    data: ImageByUrlRequest,
    current_user: User = Depends(require_role("admin", "editor")),
):
    try:
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            resp = await http_client.get(data.url)
            resp.raise_for_status()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail={
                "success": 0,
                "detail": "Impossible de télécharger l'image",
            },
        )

    content_type = resp.headers.get("content-type", "").split(";")[0].strip()
    _validate_content_type(content_type)

    content = resp.content
    if len(content) > settings.MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail={
                "success": 0,
                "detail": "Le fichier dépasse la taille maximale autorisée (5 MB)",
            },
        )

    ext = _get_extension(content_type)
    filename = f"{uuid.uuid4()}{ext}"
    upload_dir = _get_upload_dir()
    file_path = upload_dir / filename
    file_path.write_bytes(content)

    return {
        "success": 1,
        "file": {"url": f"/uploads/images/{filename}"},
    }
