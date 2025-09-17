from typing import List

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseModel):
    host: str
    port: int
    database: str
    username: str
    password: str


class DBPoolSettings(BaseModel):
    pool_size: int
    max_overflow: int
    pool_timeout: int
    pool_recycle: int
    pool_pre_ping: bool


class ConnectionSettings(BaseModel):
    connect_timeout: int


class AuthSettings(BaseModel):
    access_token_expires_minutes: int
    refresh_token_expires_minutes: int

    secret_key: str
    algorithm: str

    TOKEN_REQUEST_PATH_EXCLUDE: List[str]
    TOKEN_REQUEST_PATH_EXCLUDE_PATTERN: List[str]


class AppSettings(BaseModel):
    debug: bool


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
    )
    app: AppSettings
    postgres: PostgresSettings
    db_pool_conf: DBPoolSettings
    connection: ConnectionSettings
    auth: AuthSettings


settings = Config()  # type: ignore[call-arg]
