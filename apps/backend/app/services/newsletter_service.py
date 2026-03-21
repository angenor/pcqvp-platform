import csv
import io
import secrets
from datetime import UTC, datetime

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.newsletter import NewsletterSubscriber, SubscriberStatus

settings = get_settings()

serializer = URLSafeTimedSerializer(settings.JWT_SECRET)

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=bool(settings.MAIL_USERNAME),
    SUPPRESS_SEND=not bool(settings.MAIL_USERNAME),
)


def generate_confirm_token(email: str) -> str:
    return serializer.dumps(email, salt="newsletter-confirm")


def verify_confirm_token(token: str, max_age: int = 86400) -> str | None:
    try:
        return serializer.loads(token, salt="newsletter-confirm", max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None


async def subscribe(
    db: AsyncSession,
    email: str,
    background_tasks: BackgroundTasks,
) -> str:
    email = email.lower().strip()

    result = await db.execute(
        select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
    )
    existing = result.scalar_one_or_none()

    if existing:
        if existing.status == SubscriberStatus.actif:
            return "Vous etes deja inscrit a la newsletter."
        elif existing.status == SubscriberStatus.desinscrit:
            existing.status = SubscriberStatus.en_attente
            existing.unsubscribe_token = secrets.token_urlsafe(32)
            existing.unsubscribed_at = None
            await db.commit()
        # For en_attente, resend confirmation

        confirm_token = generate_confirm_token(email)
        background_tasks.add_task(_send_confirmation_email, email, confirm_token)
        return "Un email de confirmation a ete envoye."

    subscriber = NewsletterSubscriber(
        email=email,
        status=SubscriberStatus.en_attente,
        unsubscribe_token=secrets.token_urlsafe(32),
    )
    db.add(subscriber)
    await db.commit()

    confirm_token = generate_confirm_token(email)
    background_tasks.add_task(_send_confirmation_email, email, confirm_token)

    return "Un email de confirmation a ete envoye."


async def confirm(db: AsyncSession, token: str) -> bool:
    email = verify_confirm_token(token)
    if not email:
        return False

    result = await db.execute(
        select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
    )
    subscriber = result.scalar_one_or_none()
    if not subscriber:
        return False

    if subscriber.status == SubscriberStatus.actif:
        return True

    subscriber.status = SubscriberStatus.actif
    subscriber.confirmed_at = datetime.now(UTC)
    await db.commit()
    return True


async def unsubscribe(db: AsyncSession, token: str) -> bool:
    result = await db.execute(
        select(NewsletterSubscriber).where(
            NewsletterSubscriber.unsubscribe_token == token
        )
    )
    subscriber = result.scalar_one_or_none()
    if not subscriber:
        return False

    subscriber.status = SubscriberStatus.desinscrit
    subscriber.unsubscribed_at = datetime.now(UTC)
    await db.commit()
    return True


# Admin functions

async def list_subscribers(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 50,
    status: str | None = None,
    search: str | None = None,
) -> dict:
    query = select(NewsletterSubscriber)

    if status:
        query = query.where(NewsletterSubscriber.status == status)
    if search:
        query = query.where(NewsletterSubscriber.email.ilike(f"%{search}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = (
        query.order_by(NewsletterSubscriber.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [
            {
                "id": str(s.id),
                "email": s.email,
                "status": s.status.value if hasattr(s.status, 'value') else s.status,
                "confirmed_at": s.confirmed_at,
                "unsubscribed_at": s.unsubscribed_at,
                "created_at": s.created_at,
            }
            for s in items
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


async def export_csv(db: AsyncSession) -> str:
    result = await db.execute(
        select(NewsletterSubscriber)
        .where(NewsletterSubscriber.status == SubscriberStatus.actif)
        .order_by(NewsletterSubscriber.email)
    )
    subscribers = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["email", "status", "confirmed_at", "created_at"])
    for s in subscribers:
        writer.writerow([
            s.email,
            s.status.value if hasattr(s.status, 'value') else s.status,
            s.confirmed_at.isoformat() if s.confirmed_at else "",
            s.created_at.isoformat() if s.created_at else "",
        ])

    return output.getvalue()


async def delete_subscriber(db: AsyncSession, subscriber_id: str) -> bool:
    result = await db.execute(
        select(NewsletterSubscriber).where(
            NewsletterSubscriber.id == subscriber_id
        )
    )
    subscriber = result.scalar_one_or_none()
    if not subscriber:
        return False

    await db.delete(subscriber)
    await db.commit()
    return True


async def _send_confirmation_email(email: str, token: str) -> None:
    confirm_url = f"{settings.FRONTEND_URL}/api/newsletter/confirm?token={token}"

    message = MessageSchema(
        subject="Confirmez votre inscription a la newsletter PCQVP",
        recipients=[email],
        body=f"""
        <h2>Confirmation d'inscription</h2>
        <p>Merci de votre interet pour la newsletter PCQVP Madagascar.</p>
        <p>Cliquez sur le lien ci-dessous pour confirmer votre inscription :</p>
        <p><a href="{confirm_url}">Confirmer mon inscription</a></p>
        <p>Ce lien expire dans 24 heures.</p>
        <p>Si vous n'avez pas demande cette inscription, ignorez cet email.</p>
        """,
        subtype=MessageType.html,
    )

    fm = FastMail(mail_config)
    await fm.send_message(message)
