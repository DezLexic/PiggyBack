from __future__ import annotations

from psycopg_pool import ConnectionPool


def create_pool(dsn: str) -> ConnectionPool:
    return ConnectionPool(
        conninfo=dsn,
        min_size=1,
        max_size=10,
        open=False,
    )
