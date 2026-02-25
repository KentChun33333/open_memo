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

    # Paths — defaults match Docker layout (/app/content, /app/frontend/dist)
    # For local dev, override with OPENMEMO_CONTENT_DIR=./content
    content_dir: Path = Path("./content")
    frontend_dist: Path = Path("./frontend/dist")

    # Server
    port: int = 8080

    model_config = {"env_prefix": "OPENMEMO_", "env_file": ".env"}

    from pydantic import model_validator

    @model_validator(mode="after")
    def check_production_secrets(self):
        """Ensure default secrets are not used in production."""
        if not self.debug:
            if self.admin_password == "openmemo":
                raise ValueError(
                    "\n\n🚨 CRITICAL SECURITY ERROR 🚨\n"
                    "You are running OpenMemo in production (debug=False), "
                    "but you are using the default admin password ('openmemo').\n"
                    "This means ANYONE on the internet can log in as Admin.\n\n"
                    "HOW TO FIX:\n"
                    "Set the OPENMEMO_ADMIN_PASSWORD environment variable in your "
                    "deployment platform (like GCP Cloud Run, Railway, or Docker) "
                    "to a strong, unique password.\n"
                )
            if self.secret_key == "change-me-in-production-please":
                raise ValueError(
                    "\n\n🚨 CRITICAL SECURITY ERROR 🚨\n"
                    "You are running OpenMemo in production (debug=False), "
                    "but you are using the default secret_key.\n"
                    "This means attackers can forge login tokens and bypass authentication.\n\n"
                    "HOW TO FIX:\n"
                    "Generate a long random string (e.g. `openssl rand -hex 32`) and set it "
                    "as the OPENMEMO_SECRET_KEY environment variable in your deployment platform.\n"
                )
        return self


settings = Settings()
