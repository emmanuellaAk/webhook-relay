from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://relay:relay@localhost:5433/relay"

    model_config = {"env_file": ".env"}

    demo_webhook_secret: str = "ljkhug5yftdr098swerestrdytfuygiuh34567oijpouoy98t7f"

    demo_destination_url: str = "https://webhook.site/4cfd6297-eecb-43e9-aec1-c480e19abb5d"

settings = Settings()