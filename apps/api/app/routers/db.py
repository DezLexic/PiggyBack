from typing import Any

import psycopg
from fastapi import APIRouter, Response

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health/db")
def health_db(response: Response) -> dict[str, Any]:
    if not settings.database_url:
        response.status_code = 503
        return {"status": "unavailable", "detail": "DATABASE_URL not configured"}

    try:
        with psycopg.connect(settings.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
    except psycopg.Error as exc:
        response.status_code = 503
        return {"status": "error", "detail": str(exc)}

    return {"status": "ok", "database": "connected"}
