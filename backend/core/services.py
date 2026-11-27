from __future__ import annotations

import hashlib
import logging
import os
import uuid
from pathlib import Path

import requests
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from .choices import HistoryAction
from .models import OperationHistory

logger = logging.getLogger("core.services")

ALLOWED_EXTENSIONS = {
    "mp4",
    "mov",
    "mkv",
    "avi",
    "webm",
    "mp3",
    "wav",
    "flac",
    "aac",
    "m4a",
    "ogg",
    "m4b",
}

ALLOWED_MIME_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-matroska",
    "video/x-msvideo",
    "video/avi",
    "video/webm",
    "video/mpeg",
    "video/x-m4v",
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/flac",
    "audio/x-flac",
    "audio/aac",
    "audio/mp4",
    "audio/x-m4a",
    "audio/m4a",
    "audio/ogg",
    "audio/x-ogg",
    "application/ogg",
    "audio/x-matroska",
}

EXTENSION_MIME_PREFIXES = {
    "mp4": ("video/", "audio/"),
    "mov": ("video/",),
    "mkv": ("video/", "audio/"),
    "avi": ("video/",),
    "webm": ("video/", "audio/"),
    "mp3": ("audio/",),
    "wav": ("audio/",),
    "flac": ("audio/",),
    "aac": ("audio/",),
    "m4a": ("audio/", "video/"),
    "ogg": ("audio/", "application/ogg"),
    "m4b": ("audio/",),
}

class UploadValidationError(serializers.ValidationError):

def get_extension(filename: str) -> str:
    return Path(filename or "").suffix.lower().lstrip(".")

def detect_mime(path: str) -> str:
    try:
        import magic

        return magic.from_file(path, mime=True) or ""
    except Exception:
        logger.warning("python-magic niedostępny, fallback na mimetypes", exc_info=True)
        import mimetypes

        return mimetypes.guess_type(path)[0] or ""

def validate_upload_extension(filename: str) -> str:
    ext = get_extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise UploadValidationError(
            {"file": [f"Niedozwolone rozszerzenie pliku: '.{ext}'."]}
        )
    return ext

def max_upload_size_bytes() -> int:
    return int(settings.MAX_UPLOAD_SIZE_MB) * 1024 * 1024

def validate_upload_size(size_bytes: int) -> None:
    if size_bytes <= 0:
        raise UploadValidationError({"file": ["Plik jest pusty."]})
    if size_bytes > max_upload_size_bytes():
        raise UploadValidationError(
            {
                "file": [
                    f"Plik przekracza limit {settings.MAX_UPLOAD_SIZE_MB} MB."
                ]
            }
        )

def validate_upload_mime(path: str, ext: str) -> str:
    mime = detect_mime(path)
    if mime not in ALLOWED_MIME_TYPES:
        raise UploadValidationError(
            {"file": [f"Niedozwolony typ MIME: '{mime}'."]}
        )
    prefixes = EXTENSION_MIME_PREFIXES.get(ext, ())
    if prefixes and not any(mime.startswith(p) for p in prefixes):
        raise UploadValidationError(
            {"file": [f"Typ MIME '{mime}' nie pasuje do rozszerzenia '.{ext}'."]}
        )
    return mime

def compute_sha256(path: str, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()

def build_storage_path(user_id, ext: str) -> str:
    return f"uploads/{user_id}/{uuid.uuid4().hex}.{ext}"

def absolute_media_path(relative_path: str) -> str:
    media_root = os.path.realpath(settings.MEDIA_ROOT)
    candidate = os.path.realpath(os.path.join(media_root, relative_path))
    if candidate != media_root and not candidate.startswith(media_root + os.sep):
        raise ValueError("Ścieżka poza MEDIA_ROOT.")
    return candidate

def build_output_dir(user_id, job_id) -> str:
    return f"outputs/{user_id}/{job_id}/"

def record_history(
    *,
    user,
    action: str,
    job=None,
    source_file=None,
    details: dict | None = None,
) -> OperationHistory:
    return OperationHistory.objects.create(
        user=user,
        action=action,
        job=job,
        source_file=source_file,
        details=details or {},
    )

class FastAPIError(Exception):

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code

class FastAPIClient:

    def __init__(self, base_url: str | None = None, token: str | None = None, timeout: int | None = None):
        self.base_url = (base_url or settings.FASTAPI_URL).rstrip("/")
        self.token = token if token is not None else settings.INTERNAL_TOKEN
        self.timeout = timeout or settings.INTERNAL_HTTP_TIMEOUT_S

    def _headers(self) -> dict:
        return {"X-Internal-Token": self.token, "Content-Type": "application/json"}

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def process(self, payload: dict) -> dict:
        resp = requests.post(
            self._url("/internal/process"),
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        if resp.status_code not in (200, 202):
            raise FastAPIError(
                f"FastAPI /internal/process zwróciło {resp.status_code}: {resp.text[:500]}",
                status_code=resp.status_code,
            )
        return resp.json()

    def job_status(self, job_id: str) -> dict:
        resp = requests.get(
            self._url(f"/internal/jobs/{job_id}/status"),
            headers=self._headers(),
            timeout=self.timeout,
        )
        if resp.status_code == 404:
            raise FastAPIError("usługa obliczeniowa niedostępna", status_code=404)
        if resp.status_code != 200:
            raise FastAPIError(
                f"FastAPI status zwróciło {resp.status_code}: {resp.text[:500]}",
                status_code=resp.status_code,
            )
        return resp.json()

    def cancel(self, job_id: str) -> dict:
        resp = requests.post(
            self._url(f"/internal/jobs/{job_id}/cancel"),
            headers=self._headers(),
            timeout=self.timeout,
        )
        if resp.status_code == 404:
            raise FastAPIError("usługa obliczeniowa niedostępna", status_code=404)
        if resp.status_code != 200:
            raise FastAPIError(
                f"FastAPI cancel zwróciło {resp.status_code}: {resp.text[:500]}",
                status_code=resp.status_code,
            )
        return resp.json()

    def inspect(self, path: str) -> dict:
        resp = requests.get(
            self._url("/internal/inspect"),
            params={"path": path},
            headers=self._headers(),
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise FastAPIError(
                f"FastAPI inspect zwróciło {resp.status_code}: {resp.text[:500]}",
                status_code=resp.status_code,
            )
        return resp.json()

def now():
    return timezone.now()
