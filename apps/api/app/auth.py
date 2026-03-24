from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException
from psycopg import Connection

from app.core.config import settings
from app.db.deps import get_db
from app.repos import api_keys as api_keys_repo


def require_api_key(
    conn: Annotated[Connection, Depends(get_db)],
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="X-API-Key header required")
    # Admin bypass — no DB lookup needed
    if settings.admin_api_key and x_api_key == settings.admin_api_key:
        return
    # Verify against stored keys
    if api_keys_repo.verify_api_key(conn, x_api_key) is None:
        raise HTTPException(status_code=401, detail="Invalid API key")


RequireApiKey = Annotated[None, Depends(require_api_key)]
