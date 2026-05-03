from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> Path | None:
    """Remonte l'arborescence pour trouver le .env le plus proche."""
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        env_path = parent / ".env"
        if env_path.is_file():
            return env_path
    return None


class Settings(BaseSettings):
    DATABASE_URL: str
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    JWT_SECRET: str = "change-me-in-production-min-32-chars!!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    FIRST_ADMIN_EMAIL: str = "admin@pcqvp.mg"
    FIRST_ADMIN_PASSWORD: str = "changeme123"

    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@pcqvp.mg"
    MAIL_SERVER: str = "localhost"
    MAIL_PORT: int = 587
    FRONTEND_URL: str = "http://localhost:3000"
    COOKIE_SECURE: bool = False

    UPLOAD_DIR: str = "uploads/images"
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024
    ALLOWED_IMAGE_TYPES: list[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    ]

    GEODATA_MAX_UPLOAD_BYTES: int = 50 * 1024 * 1024
    GEODATA_MAX_VERSIONS: int = 50
    # Seuil Visvalingam-Whyatt en deg² : 0.0005 ≈ 6×6 km², simplifie sans détruire les frontières.
    GEODATA_SIMPLIFY_RATIO: float = 0.0005
    GEODATA_MIN_FEATURE_AREA_DEG2: float = 0.0001
    GEODATA_FEATURES_MIN_WARN: int = 20
    GEODATA_FEATURES_MAX_WARN: int = 30
    GEODATA_SYNC_TIMEOUT_SECONDS: float = 5.0
    GEODATA_RATE_LIMIT_UPLOADS_PER_HOUR: int = 10
    GEODATA_NAME_ALIASES: dict[str, str] = {
        "matsiatra ambony": "Haute Matsiatra",
    }
    GEODATA_COORDINATE_PRECISION: int = 4
    GEODATA_PUBLIC_CACHE_MAX_AGE: int = 3600
    GEODATA_REGION_CODE_PREFIX: str = "MG-"

    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
