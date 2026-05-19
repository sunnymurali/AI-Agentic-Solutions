from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    oracle_user: str
    oracle_password: str
    oracle_dsn: str  # e.g. "host:port/service_name" or a TNS alias
    oracle_pool_min: int = 1
    oracle_pool_max: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
