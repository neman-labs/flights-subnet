import ast
from contextlib import suppress
from os import getenv


def get_env(name: str, default=None, *, required=True, is_list=False):
    value = getenv(name, default)

    if value is None and required:
        raise ValueError(f"Environment variable {name} is not set and has no default value")

    with suppress(Exception):
        value = ast.literal_eval(value)

    if is_list and isinstance(value, str):
        value = value.split(",")

    return value


POSTGRES_USER = get_env("POSTGRES_USER")
POSTGRES_PASSWORD = get_env("POSTGRES_PASSWORD")
POSTGRES_DB = get_env("POSTGRES_DB")
POSTGRES_HOST = get_env("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = get_env("POSTGRES_PORT", 5432)
REDIS_URL = get_env("REDIS_URL", "127.0.0.1")
REDIS_PORT = get_env("REDIS_PORT", 6379)
