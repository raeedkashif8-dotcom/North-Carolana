"""App settings, read from environment variables or the git-ignored .env file."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Supabase Session pooler string (D-33). Empty means "no database configured yet".
    database_url: str = ""
    # Our tables live here, never in Supabase's API-exposed "public" schema (D-33).
    db_schema: str = "app"

    smtp_host: str = "localhost"
    smtp_port: int = 1025

    agents_dir: str = "agents"
    templates_dir: str = "templates"

    # ENV-2 only. The app refuses to start in production with this set (ENV-3).
    environment: str = "local"  # local | demo | production
    fast_clock: bool = False


def sqlalchemy_url(url: str) -> str:
    """Accept the string exactly as Supabase shows it; pick the psycopg driver ourselves."""
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def get_settings() -> Settings:
    s = Settings()
    s.database_url = sqlalchemy_url(s.database_url)
    if s.environment == "production" and s.fast_clock:
        raise RuntimeError("FAST_CLOCK must never be on in production (ENV-3).")
    return s
