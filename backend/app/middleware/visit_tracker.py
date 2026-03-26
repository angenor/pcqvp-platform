import re
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.database import async_session
from app.models.visit_log import VisitLog

BOT_PATTERNS = re.compile(
    r"(bot|crawl|spider|slurp|baiduspider|yandex|googlebot|bingbot)",
    re.IGNORECASE,
)

PUBLIC_ROUTE_PATTERNS = [
    (re.compile(r"^/api/public/"), None),
    (re.compile(r"^/api/search"), None),
    (re.compile(r"^/provinces/([^/]+)$"), "province"),
    (re.compile(r"^/regions/([^/]+)$"), "region"),
    (re.compile(r"^/communes/([^/]+)$"), "commune"),
    (re.compile(r"^/collectivite/([^/]+)$"), "compte"),
    (re.compile(r"^/$"), "home"),
]

DOWNLOAD_PATTERN = re.compile(r"/api/.*/(export|download)")


def _classify_page(path: str) -> tuple[str | None, str | None, str | None]:
    """Returns (page_type, collectivite_type, collectivite_id)."""
    for pattern, page_type in PUBLIC_ROUTE_PATTERNS:
        match = pattern.match(path)
        if match:
            coll_id = match.group(1) if match.lastindex else None
            geo_types = ("province", "region", "commune")
            coll_type = page_type if page_type in geo_types else None
            return page_type, coll_type, coll_id
    return None, None, None


def _detect_download_format(path: str) -> str | None:
    if ".xlsx" in path or "format=xlsx" in path:
        return "xlsx"
    if ".docx" in path or "format=docx" in path:
        return "docx"
    return None


class VisitTrackerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        path = request.url.path
        user_agent = request.headers.get("user-agent", "")

        if BOT_PATTERNS.search(user_agent):
            return response

        # Skip admin/auth routes
        if path.startswith("/api/admin") or path.startswith("/api/auth"):
            return response
        if path == "/health":
            return response

        # Determine event type
        is_download = bool(DOWNLOAD_PATTERN.search(path))
        event_type = "download" if is_download else "page_view"

        page_type, collectivite_type, collectivite_id = _classify_page(path)
        download_format = _detect_download_format(path) if is_download else None

        # Skip unclassified routes for page_views
        if event_type == "page_view" and page_type is None:
            return response

        # Log in background
        ip = request.client.host if request.client else None

        async def _log_visit():
            async with async_session() as session:
                log = VisitLog(
                    event_type=event_type,
                    path=path[:500],
                    page_type=page_type,
                    collectivite_type=collectivite_type,
                    collectivite_id=collectivite_id if collectivite_id else None,
                    download_format=download_format,
                    user_agent=user_agent[:500] if user_agent else None,
                    ip_address=ip,
                )
                session.add(log)
                await session.commit()

        # Use background task
        import asyncio
        asyncio.ensure_future(_log_visit())

        return response
