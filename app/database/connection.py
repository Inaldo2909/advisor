"""
Database Connection Module
Handles PostgreSQL database connections and initialization.
"""
import asyncpg
import os
from typing import Optional


_db_pool: Optional[asyncpg.Pool] = None


async def init_db():
    """Initialize database connection pool"""
    global _db_pool

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/code_advisor"
    )

    _db_pool = await asyncpg.create_pool(
        database_url,
        min_size=2,
        max_size=10,
        command_timeout=60
    )

    # Create table if it doesn't exist
    async with _db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id SERIAL PRIMARY KEY,
                code_snippet TEXT NOT NULL,
                suggestions JSONB NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)

        # Create index for faster queries
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_created_at
            ON analysis_history(created_at DESC)
        """)

    print("✓ Database initialized successfully")


async def close_db():
    """Close database connection pool"""
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        print("✓ Database connection closed")


async def get_db_connection():
    """Get a database connection from the pool"""
    global _db_pool
    if not _db_pool:
        await init_db()
    return await _db_pool.acquire()
