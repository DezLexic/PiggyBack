from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from psycopg import Connection

from app.core.config import settings


def get_db(request: Request) -> Generator[Connection, None, None]:
    pool = getattr(request.app.state, "db_pool", None)
    if pool is None:
        if not settings.database_url:
            raise HTTPException(
                status_code=503,
                detail="Database not configured (set DATABASE_URL)",
            )
        raise HTTPException(status_code=503, detail="Database pool not available")

    with pool.connection() as conn:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise


DbConn = Annotated[Connection, Depends(get_db)]
