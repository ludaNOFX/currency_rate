import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Base(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    PROJ_ENV: str = Field(..., env="PROJ_ENV")  # type: ignore
    # Application
    DEBUG: bool = True
    TITLE: str = "TOKEN AUTH APP"
    GLOBAL_PREFIX_URL: str
    LOG_DIR: str = "logs"

    @property
    def URL(self) -> str:
        return "https://www.cbr-xml-daily.ru/daily_json.js"

    @property
    def BASE_DIR(self) -> Path:
        return Path().resolve()


class Local(Base):
    GLOBAL_PREFIX_URL: str = "/api"
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file="local.env")


class Test(Base):
    GLOBAL_PREFIX_URL: str = "/api/test"
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file="test.env")


class Production(Base):
    GLOBAL_PREFIX_URL: str = "/api"
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file="prod.env")


config_map = {
    "local": Local,
    "test": Test,
    "prod": Production,
}

env_variable = os.environ.get("PROJ_ENV")

if env_variable is None:
    raise ValueError("Not found 'PROJ_ENV' enviroment variable")

env_variable = env_variable.lower()
if env_variable not in config_map:
    raise ValueError(
        f"Incorrect 'PROJ_ENV' enviroment variable, must be in {list(config_map.keys())}"
    )

try:
    settings: Base = config_map[env_variable]()
except ValueError as e:
    print(f"Error on validate configuration from *.env: {e}")
    raise
