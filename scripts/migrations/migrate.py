from pathlib import Path
import hashlib
import os
from dataclasses import dataclass
from typing import List

# TODO: For testing only, remove later.
import sys
from pathlib import Path
sys.path.append("/Users/saranshpandya/gitprojects/inferproject/llamaAuth/")
from schemas.packet import PostgresConfig, Migration

import psycopg2
from psycopg2.extensions import connection as PGConnection

from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(f"{Path(__file__).name, __name__ } ")


BASE_DIR = Path(__file__).resolve().parent
MIGRATIONS_DIR = BASE_DIR / "migrations"

MIGRATION_TABLE = "user_store"
ADVISORY_LOCK_ID = 8844221100332211


def load_postgres_config() -> PostgresConfig:
    try:
        return PostgresConfig(
            host=os.environ["POSTGRES_HOST"],
            port=int(os.environ.get("POSTGRES_PORT", 5432)),
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            dbname=os.environ["DBNAME"],
            sslmode=os.environ.get("POSTGRES_SSLMODE", "prefer"),
        )
    except KeyError as e:
        raise RuntimeError(f"Missing required environment variable: {e.args[0]}")


def get_connection() -> PGConnection:
    postgres_config = load_postgres_config()
    conn = psycopg2.connect(
        host=postgres_config.host,
        port=postgres_config.port,
        user=postgres_config.user,
        password=postgres_config.password,
        dbname=postgres_config.dbname,
        sslmode=postgres_config.sslmode,
    )
    conn.autocommit = False
    return conn


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_migrations() -> List[Migration]:
    if not MIGRATIONS_DIR.exists():
        raise RuntimeError(f"Migrations directory not found: {MIGRATIONS_DIR}")

    migrations: List[Migration] = []

    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        body = path.read_text(encoding="utf-8")
        checksum = sha256_hex(body.encode("utf-8"))
        migrations.append(Migration(path.name, body, checksum))

    if not migrations:
        raise RuntimeError("No migration files found")

    return migrations


def ensure_migration_table(conn: PGConnection) -> None:
    with conn.cursor() as cur:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {MIGRATION_TABLE} (
                id BIGSERIAL PRIMARY KEY,
                filename TEXT NOT NULL UNIQUE,
                checksum CHAR(64) NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
    conn.commit()


def acquire_lock(conn: PGConnection) -> None:
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_lock(%s);", (ADVISORY_LOCK_ID,))
    conn.commit()


def release_lock(conn: PGConnection) -> None:
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_unlock(%s);", (ADVISORY_LOCK_ID,))
    conn.commit()


def fetch_applied(conn: PGConnection) -> dict:
    with conn.cursor() as cur:
        cur.execute(f"SELECT filename, checksum FROM {MIGRATION_TABLE};")
        return dict(cur.fetchall())


def apply_migration(conn: PGConnection, migration: Migration) -> None:
    with conn.cursor() as cur:
        cur.execute(migration.body)
        cur.execute(
            f"INSERT INTO {MIGRATION_TABLE} (filename, checksum) VALUES (%s, %s);",
            (migration.filename, migration.checksum),
        )
    conn.commit()


def run_migrations() -> None:
    migrations = load_migrations()
    conn = get_connection()

    try:
        ensure_migration_table(conn)
        acquire_lock(conn)

        applied = fetch_applied(conn)

        for m in migrations:
            if m.filename in applied:
                if applied[m.filename] != m.checksum:
                    raise RuntimeError(
                        f"Checksum mismatch for applied migration: {m.filename}\n"
                        f"Never edit applied migrations."
                    )
                # print(f"{m.filename} (already applied)")
                logger.debug(f"{m.filename} (already applied)")
                continue

            # print(f"Applying {m.filename}")
            logger.debug(f"Applying {m.filename}")
            apply_migration(conn, m)
            # print(f"Applied {m.filename}")
            logger.debug(f"Applied {m.filename}")

    finally:
        try:
            release_lock(conn)
        finally:
            conn.close()


if __name__ == "__main__":
    run_migrations()

