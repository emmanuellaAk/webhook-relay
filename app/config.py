from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://relay:relay@localhost:5432/relay"

    model_config = {"env_file": ".env"}


settings = Settings()