from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://relay:relay@localhost:5433/relay"
    demo_webhook_secret: str = "changeme"
    demo_destination_url: str = "https://example.com/replace-me"

    model_config = {"env_file": ".env"}


settings = Settings()


# Render (and some hosts) provide DATABASE_URL as postgresql://
# but the async app needs postgresql+asyncpg://
if settings.database_url.startswith("postgresql://"):
    settings.database_url = settings.database_url.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )


# Render provides DATABASE_URL as postgresql://, but the async app
# needs the asyncpg driver. Normalize it here.
if settings.database_url.startswith("postgresql://"):
    settings.database_url = settings.database_url.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )
