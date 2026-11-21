from pathlib import Path
from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    bot_token: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_db: str
    database_url: str = f"postgresql+asyncpg://{{postgres_user}}:{{postgres_password}}@{{postgres_host}}:{{postgres_port}}/{{postgres_db}}"
    admin_ids: list[int] = Field(default_factory=list)
    manager_chat_id: int
    alert_chat_id: int
    timezone: str = "Europe/Kyiv"
    cashback_percent: int = Field(ge=0, le=100, default=5)
    review_delay_min: int = Field(ge=0, default=90)
    hot_window_discount_percent: int = Field(ge=0, le=100, default=10)

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


settings = Settings()