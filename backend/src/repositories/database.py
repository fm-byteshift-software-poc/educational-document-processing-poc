import aiosqlite
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

_db_path: str = "./backend/poc.db"


async def init_db(db_path: str) -> None:
    """Creates database tables if they do not already exist."""
    global _db_path
    _db_path = db_path

    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(_db_path) as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL REFERENCES tenants(id),
                filename TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                mime_type TEXT NOT NULL CHECK(mime_type IN ('application/pdf','text/plain')),
                uploaded_at TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('uploaded','processing','completed','failed'))
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS presentation_jobs (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL REFERENCES tenants(id),
                document_id TEXT NOT NULL REFERENCES documents(id),
                created_at TEXT NOT NULL,
                processing_status TEXT NOT NULL CHECK(processing_status IN ('queued','processing','completed','failed')),
                error_message TEXT
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS presentations (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL REFERENCES tenants(id),
                job_id TEXT NOT NULL REFERENCES presentation_jobs(id),
                source_document_id TEXT NOT NULL REFERENCES documents(id),
                presentation_version INTEGER NOT NULL DEFAULT 1,
                title TEXT NOT NULL,
                slides TEXT NOT NULL,
                generated_at TEXT NOT NULL
            )
        """)
        await conn.commit()


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Yields an async SQLite connection with row_factory enabled for dict-like access."""
    Path(_db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = await aiosqlite.connect(_db_path)
    conn.row_factory = aiosqlite.Row
    try:
        yield conn
    finally:
        await conn.close()