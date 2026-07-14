from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://relay:relay@localhost:5433/relay"

    model_config = {"env_file": ".env"}

    demo_webhook_secret: str = "ljkhug5yftdr098swerestrdytfuygiuh34567oijpouoy98t7f"


settings = Settings()