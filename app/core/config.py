from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "tw-dividend-mvp"
    app_env: str = "dev"
    database_url: str = "sqlite:///./tw_dividend.db"
    request_timeout: int = 20
    user_agent: str = "tw-dividend-mvp/0.2"
    auto_fetch_on_miss: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    enable_scheduler: bool = False
    admin_token: str | None = None
    scheduler_stocks_hour: int = 6
    scheduler_stocks_minute: int = 0

    scheduler_dividends_hour: int = 6
    scheduler_dividends_minute: int = 10

settings = Settings()