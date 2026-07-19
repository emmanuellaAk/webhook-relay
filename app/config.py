from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://relay:relay@localhost:5433/relay"
    demo_webhook_secret: str = "changeme"
    demo_destination_url: str = "https://example.com/replace-me"

    model_config = {"env_file": ".env"}


settings = Settings()