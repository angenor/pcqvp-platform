from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.compte_administratif import CompteAdministratif
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
