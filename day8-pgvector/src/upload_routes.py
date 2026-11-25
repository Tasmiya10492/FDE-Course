"""Secure document upload routes."""

import os
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from src.access_control import require_permission
from src.config import PROJECT_ROOT

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
MAX_UPLOAD_BYTES = 1 * 1024 * 1024
CHUNK_SIZE = 64 * 1024

ALLOWED_CONTENT_TYPES = {
    ".txt": {"text/plain"},
    ".md": {"text/plain", "text/markdown"},
}

UploadUser = Annotated[
    dict,
    Depends(require_permission("documents:upload")),
]


@router.post("/upload", status_code=201)
async def upload_document(
    user: UploadUser,
    file: Annotated[UploadFile, File()],
):
    """Accept a small text document from an authorized HR administrator."""
    del user  # Authorization is enforced by the dependency.

    original_name = file.filename or ""
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Only .txt and .md files are allowed.",
        )

    content_type = (file.content_type or "").split(";")[0].strip().lower()

    if content_type not in ALLOWED_CONTENT_TYPES[extension]:
        raise HTTPException(
            status_code=415,
            detail="The uploaded file content type is not allowed.",
        )

    content = bytearray()

    try:
        while True:
            chunk = await file.read(CHUNK_SIZE)

            if not chunk:
                break

            if len(content) + len(chunk) > MAX_UPLOAD_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail="The uploaded file exceeds the 1 MiB limit.",
                )

            content.extend(chunk)

        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        try:
            decoded_content = content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file must contain valid UTF-8 text.",
            ) from None

        if "\x00" in decoded_content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file contains invalid text data.",
            )

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        UPLOAD_DIR.chmod(0o700)

        generated_name = f"{uuid4().hex}{extension}"
        destination = UPLOAD_DIR / generated_name

        file_descriptor = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )

        with os.fdopen(file_descriptor, "wb") as output:
            output.write(content)

        return {
            "filename": generated_name,
            "size_bytes": len(content),
            "content_type": content_type,
            "message": "Document uploaded successfully.",
        }

    finally:
        await file.close()
