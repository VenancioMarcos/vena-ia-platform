import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePath
from uuid import uuid4

from fastapi import UploadFile

from app.modules.cad.ingestion_schemas import CadJobState

MAX_STEP_UPLOAD_BYTES = 15 * 1024 * 1024
STREAM_CHUNK_BYTES = 64 * 1024
_STEP_SIGNATURE = b"ISO-10303-21;"
_SCHEMA_PATTERN = re.compile(rb"FILE_SCHEMA\s*\(\s*\(\s*'([^']+)'", re.IGNORECASE)


class InvalidCadUploadError(ValueError):
    pass


class InvalidStepContentError(ValueError):
    pass


class CadUploadTooLargeError(ValueError):
    pass


class CadIngestionJobNotFoundError(LookupError):
    pass


@dataclass(frozen=True)
class CadIngestionJob:
    job_id: str
    owner_user_id: str
    filename: str
    size_bytes: int
    schema_type: str
    status: CadJobState
    path: Path
    error_detail: str | None = None


class CadIngestionGateway:
    """Process-local STEP sandbox. Files disappear when the gateway is closed."""

    def __init__(
        self,
        root: Path | None = None,
        *,
        max_size_bytes: int = MAX_STEP_UPLOAD_BYTES,
    ) -> None:
        if max_size_bytes <= 0:
            raise ValueError("max_size_bytes must be positive")
        self._owned_root = root is None
        self._root = (
            Path(tempfile.mkdtemp(prefix="vena-ia-cad-ingestion-"))
            if root is None
            else root
        ).resolve()
        self._root.mkdir(parents=True, exist_ok=True)
        self._max_size_bytes = max_size_bytes
        self._jobs: dict[str, CadIngestionJob] = {}

    async def dispatch(self, upload: UploadFile, owner_user_id: str) -> CadIngestionJob:
        filename = PurePath(upload.filename or "").name
        if not filename or Path(filename).suffix.lower() not in {".step", ".stp"}:
            raise InvalidCadUploadError("Use a .step or .stp file")

        first_chunk = await upload.read(STREAM_CHUNK_BYTES)
        if _STEP_SIGNATURE not in first_chunk:
            raise InvalidStepContentError("Missing ISO-10303-21 STEP signature")

        job_id = str(uuid4())
        destination = (self._root / f"{job_id}.step").resolve()
        if destination.parent != self._root:
            raise InvalidCadUploadError("Invalid sandbox destination")

        size_bytes = 0
        try:
            descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "wb") as target:
                chunk = first_chunk
                while chunk:
                    size_bytes += len(chunk)
                    if size_bytes > self._max_size_bytes:
                        raise CadUploadTooLargeError(
                            f"STEP file exceeds {self._max_size_bytes} bytes"
                        )
                    target.write(chunk)
                    chunk = await upload.read(STREAM_CHUNK_BYTES)
        except Exception:
            destination.unlink(missing_ok=True)
            raise

        schema_match = _SCHEMA_PATTERN.search(first_chunk)
        schema_type = (
            schema_match.group(1).decode("ascii", errors="replace")
            if schema_match
            else "UNKNOWN"
        )
        job = CadIngestionJob(
            job_id=job_id,
            owner_user_id=owner_user_id,
            filename=filename,
            size_bytes=size_bytes,
            schema_type=schema_type,
            status="QUEUED",
            path=destination,
        )
        self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str, owner_user_id: str) -> CadIngestionJob:
        job = self._jobs.get(job_id)
        if job is None or job.owner_user_id != owner_user_id:
            raise CadIngestionJobNotFoundError("CAD ingestion job not found")
        return job

    def close(self) -> None:
        self._jobs.clear()
        if self._owned_root:
            shutil.rmtree(self._root, ignore_errors=True)


def build_cad_ingestion_gateway() -> CadIngestionGateway:
    return CadIngestionGateway()
