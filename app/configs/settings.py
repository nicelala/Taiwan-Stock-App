from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "tw-dividend-mvp"
    app_env: str = "dev"
    database_url: str = "sqlite:///./tw_dividend.db"
    request_timeout: int = 20
    retry_count: int = 2
    user_agent: str = "tw-dividend-mvp/0.1"
    enable_scheduler: bool = False
    auto_fetch_on_miss: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()