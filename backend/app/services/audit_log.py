import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.compte_administratif import CompteAdministratif
from app.models.geodata_version import GeodataVersion
from app.models.user import User


async def record_compte_deletion(
    db: AsyncSession, actor: User, compte: CompteAdministratif
) -> None:
    """Persist an audit entry capturing the compte snapshot before delete.

    Called within the same transaction as the DELETE so the trace is
    guaranteed even when the compte row disappears via cascade.
    """
    snapshot = {
        "id": str(compte.id),
        "collectivite_type": compte.collectivite_type.value,
        "collectivite_id": str(compte.collectivite_id),
        "annee_exercice": compte.annee_exercice,
        "status": compte.status.value,
        "created_by": str(compte.created_by),
        "created_at": compte.created_at.isoformat() if compte.created_at else None,
    }
    entry = AuditLog(
        actor_user_id=actor.id,
        action="compte_administratif.deleted",
        target_type="compte_administratif",
        target_id=compte.id,
        payload=snapshot,
    )
    db.add(entry)
    await db.flush()


def _geodata_payload(version: GeodataVersion, **extra) -> dict:
    payload = {
        "result": "success",
        "features_count": version.features_count,
        "processed_size_bytes": version.processed_size_bytes,
    }
    payload.update(extra)
    return payload


async def record_geodata_uploaded(
    db: AsyncSession,
    actor: User,
    version: GeodataVersion,
    *,
    failure_reason: str | None = None,
) -> None:
    payload = _geodata_payload(version)
    if failure_reason:
        payload["result"] = "failure"
        payload["failure_reason"] = failure_reason
    db.add(
        AuditLog(
            actor_user_id=actor.id,
            action="geodata_version.uploaded",
            target_type="geodata_version",
            target_id=version.id,
            payload=payload,
        )
    )
    await db.flush()


async def record_geodata_activated(
    db: AsyncSession,
    actor: User,
    version: GeodataVersion,
    *,
    previous_active_id: uuid.UUID | None = None,
) -> None:
    payload = _geodata_payload(version)
    if previous_active_id is not None:
        payload["previous_active_id"] = str(previous_active_id)
    db.add(
        AuditLog(
            actor_user_id=actor.id,
            action="geodata_version.activated",
            target_type="geodata_version",
            target_id=version.id,
            payload=payload,
        )
    )
    await db.flush()


async def record_geodata_deleted(
    db: AsyncSession, actor: User, version: GeodataVersion
) -> None:
    db.add(
        AuditLog(
            actor_user_id=actor.id,
            action="geodata_version.deleted",
            target_type="geodata_version",
            target_id=version.id,
            payload=_geodata_payload(version),
        )
    )
    await db.flush()
