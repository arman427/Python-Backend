from dataclasses import dataclass
from functools import lru_cache
from os import environ


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str


@lru_cache
def get_settings() -> Settings:
    return Settings(DATABASE_URL=environ["DATABASE_URL"])
