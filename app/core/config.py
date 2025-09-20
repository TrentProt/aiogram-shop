from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class APIKeyTG(BaseSettings):
    key: str

class DataBaseConfig(BaseSettings):
    url: AnyUrl
    echo: bool = True
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter='__',
        env_prefix='APP_CONFIG__',
        env_file='.env',
        extra='ignore'
    )
    api: APIKeyTG
    db: DataBaseConfig


settings = Settings()
