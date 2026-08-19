from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024


async def save_college_image(upload: UploadFile) -> str:
    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only JPEG, PNG, WEBP, and GIF images are supported")

    image_bytes = await upload.read(MAX_IMAGE_SIZE + 1)
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image must be 10 MB or smaller")

    if settings.IMAGE_STORAGE_PROVIDER == "cloudinary":
        return _save_to_cloudinary(image_bytes)
    return _save_locally(image_bytes, upload.filename or "college-image")


async def save_ui_image(upload: UploadFile) -> str:
    return await save_college_image(upload)


def _save_to_cloudinary(image_bytes: bytes) -> str:
    if not all((settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET)):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cloudinary storage is not configured")

    import cloudinary
    import cloudinary.uploader

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )
    result = cloudinary.uploader.upload(image_bytes, folder="cutoffguide/colleges", resource_type="image")
    return result["secure_url"]


def _save_locally(image_bytes: bytes, original_name: str) -> str:
    extension = Path(original_name).suffix.lower() or ".jpg"
    if extension not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        extension = ".jpg"

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"college-{uuid4().hex}{extension}"
    (upload_dir / filename).write_bytes(image_bytes)
    return f"{settings.API_PUBLIC_URL}/uploads/{filename}"