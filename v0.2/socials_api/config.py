import os
from typing import Annotated, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None
    model_config = SettingsConfigDict(
        # use os.path & __file__ to grab absolute path
        env_file=os.path.join(os.path.dirname(__file__), ".env"),
        extra="ignore",
    )


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLLBACK: bool = False


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")


class TestConfig(GlobalConfig):
    DATABASE_URL: str = "sqlite:///test.db"
    DB_FORCE_ROLLBACK: bool = True

    model_config = SettingsConfigDict(env_prefix="TEST_")


# build minimal cache decorator for `get_config` function, since function returns are deterministic
def config_cache(func):
    # cache size shouldn't be a problem because this cache
    # will only be inserted with 3 possible keys: 'dev', 'prod', and 'test'
    cache = {}

    def inner(arg: str):
        if arg in cache.keys():
            return cache[arg]
        result = func(arg)
        cache[arg] = result
        return result

    return inner


# even though I could use lru_cache from functools for this
# building my own, for a minimal application like this, reinforces my learning
@config_cache
def get_config(env_state: str):
    if env_state is None:
        raise ValueError("ENV_STATE is not set in .env file")

    env_configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}

    if env_state not in env_configs:
        raise ValueError(
            f'Invalid ENV_STATE: {env_state}. Must be "dev", "prod", or "test"'
        )

    return env_configs[env_state]()


config: Annotated[GlobalConfig, "imported .env vars"] = get_config(
    BaseConfig().ENV_STATE
)
