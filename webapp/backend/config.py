"""Application configuration via environment variables."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "OpenMemo"
    debug: bool = False

    # Auth
    secret_key: str = "change-me-in-production-please"
    admin_username: str = "admin"
    admin_password: str = "openmemo"  # Change in .env
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Paths
    content_dir: Path = Path(__file__).parent.parent / "content"
    frontend_dist: Path = Path(__file__).parent.parent / "frontend" / "dist"

    # Server
    port: int = 8080

    model_config = {"env_prefix": "OPENMEMO_", "env_file": ".env"}


settings = Settings()
