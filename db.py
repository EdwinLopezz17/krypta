import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH  = DATA_DIR / "krypta.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS master (
                id          INTEGER PRIMARY KEY CHECK (id = 1),
                hash        TEXT NOT NULL,
                salt        BLOB NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS passwords (
                uuid              TEXT PRIMARY KEY,
                service           TEXT NOT NULL,
                username          TEXT,
                encrypted_payload BLOB NOT NULL,
                nonce             BLOB NOT NULL,
                updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    conn.close()
    print(f"[OK] Base de datos inicializada en: {DB_PATH}")


def db_status() -> dict:
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row["name"] for row in cur.fetchall()]

    cur.execute("SELECT COUNT(*) as n FROM passwords")
    count = cur.fetchone()["n"]

    cur.execute("SELECT COUNT(*) as n FROM master")
    has_master = cur.fetchone()["n"] == 1

    conn.close()
    return {
        "path":       str(DB_PATH),
        "tables":     tables,
        "entries":    count,
        "has_master": has_master,
    }


if __name__ == "__main__":
    init_db()
    status = db_status()
    print(f"  Tablas:        {status['tables']}")
    print(f"  Entradas:      {status['entries']}")
    print(f"  Clave maestra: {'configurada' if status['has_master'] else 'no configurada'}")

   