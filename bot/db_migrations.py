import logging
from pathlib import Path

from typing import Any
import asyncpg

logger = logging.getLogger(__name__)

MIGRATIONS_PATH = Path(__file__).resolve().parent.parent / "migrations"

async def apply_migrations(pool: Any) -> None:
    """Apply SQL migrations from the migrations directory."""
    async with pool.acquire() as conn:
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY)"
        )
        current = await conn.fetchval(
            "SELECT COALESCE(MAX(version), 0) FROM schema_version"
        )
        for sql_file in sorted(MIGRATIONS_PATH.glob("*.sql")):
            version = int(sql_file.stem.split("_")[0])
            if version > current:
                logger.info("Applying migration %s", sql_file.name)
                await conn.execute(sql_file.read_text())
                await conn.execute(
                    "INSERT INTO schema_version(version) VALUES($1)", version
                )

        
    return None
