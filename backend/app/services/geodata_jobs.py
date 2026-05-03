"""Registre in-memory des jobs asynchrones de pipeline geodata."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from typing import Literal

JobStatusValue = Literal["pending", "running", "done", "failed"]
JOB_TTL_SECONDS = 30 * 60


@dataclass(frozen=True)
class GeodataJob:
    id: uuid.UUID
    status: JobStatusValue
    submitted_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    version_id: uuid.UUID | None = None
    error_message: str | None = None


_jobs: dict[uuid.UUID, GeodataJob] = {}
_lock = asyncio.Lock()


async def create_job() -> GeodataJob:
    async with _lock:
        await _purge_expired_locked()
        job = GeodataJob(
            id=uuid.uuid4(),
            status="pending",
            submitted_at=datetime.now(UTC),
        )
        _jobs[job.id] = job
        return job


async def update_status(
    job_id: uuid.UUID,
    *,
    status: JobStatusValue,
    version_id: uuid.UUID | None = None,
    error_message: str | None = None,
) -> GeodataJob | None:
    async with _lock:
        existing = _jobs.get(job_id)
        if existing is None:
            return None
        now = datetime.now(UTC)
        started_at = existing.started_at
        completed_at = existing.completed_at
        if status == "running" and started_at is None:
            started_at = now
        if status in ("done", "failed"):
            completed_at = now
        updated = replace(
            existing,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            version_id=version_id if version_id is not None else existing.version_id,
            error_message=error_message
            if error_message is not None
            else existing.error_message,
        )
        _jobs[job_id] = updated
        return updated


async def get_job(job_id: uuid.UUID) -> GeodataJob | None:
    async with _lock:
        await _purge_expired_locked()
        return _jobs.get(job_id)


async def _purge_expired_locked() -> None:
    cutoff = datetime.now(UTC) - timedelta(seconds=JOB_TTL_SECONDS)
    expired = [
        jid
        for jid, job in _jobs.items()
        if job.completed_at is not None and job.completed_at < cutoff
    ]
    for jid in expired:
        _jobs.pop(jid, None)


async def purge_expired() -> None:
    async with _lock:
        await _purge_expired_locked()


async def reset_for_tests() -> None:
    async with _lock:
        _jobs.clear()
