from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
    "postgresql+asyncpg://danielbautista@127.0.0.1:5432/cashcow_dev"
    )

    secret_key: str

    frontend_origin: str = "http://localhost:5173"

    # Read values from backend/.env and replace here
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()