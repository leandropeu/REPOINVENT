from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    secret_key: str
    access_token_expire_minutes: int = 120
    database_url: str = "sqlite:///./data/repoinvent.db"
    cors_origins: str = "http://127.0.0.1:5173"
    trusted_hosts: str = "127.0.0.1,localhost"
    secure_headers_enabled: bool = True
    force_https: bool = False
    login_rate_limit_max_attempts: int = 10
    login_rate_limit_window_seconds: int = 300
    min_secret_key_length: int = 32
    enforce_strong_secret_key: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def trusted_hosts_list(self) -> list[str]:
        return [h.strip() for h in self.trusted_hosts.split(",") if h.strip()]


settings = Settings()
