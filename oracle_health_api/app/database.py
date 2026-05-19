import logging

import oracledb

from app.config import settings

logger = logging.getLogger(__name__)

_pool: oracledb.AsyncConnectionPool | None = None


async def create_pool() -> None:
    global _pool
    _pool = await oracledb.create_pool_async(
        user=settings.oracle_user,
        password=settings.oracle_password,
        dsn=settings.oracle_dsn,
        min=settings.oracle_pool_min,
        max=settings.oracle_pool_max,
    )
    logger.info("Oracle connection pool created (dsn=%s)", settings.oracle_dsn)


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Oracle connection pool closed")


async def check_connection() -> tuple[bool, str]:
    """Return (is_healthy, detail_message)."""
    if _pool is None:
        return False, "Connection pool is not initialised"
    try:
        async with _pool.acquire() as conn:
            await conn.ping()
        return True, "Oracle connection is healthy"
    except oracledb.DatabaseError as exc:
        logger.error("Oracle health check failed: %s", exc)
        return False, str(exc)
