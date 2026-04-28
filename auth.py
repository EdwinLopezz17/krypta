import hmac
import hashlib

from db import get_connection
from crypto import derive_key, generate_salt

def _hash_key(derived_key: bytes) -> str:
    return hashlib.sha256(derived_key).hexdigest()

def master_exists() -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as n FROM master")
    n =cur.fetchone()["n"]
    conn.close()
    return n == 1

def register_master(password: str) -> bytes:
    salt = generate_salt()
    derived_key = derive_key(password, salt)
    key_hash = _hash_key(derived_key)

    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT INTO master (id, hash, salt) VALUES (1, ?, ?)",
            (key_hash, salt),
        )
    conn.close()
    print("[OK] Contraseña maestra registrada.")
    return derived_key

def login(password: str) -> bytes | None:
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT hash, salt FROM master WHERE id = 1")
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    stored_hash = row["hash"]
    salt        = row["salt"]
    derived_key = derive_key(password, salt)
    candidate   = _hash_key(derived_key)

    if hmac.compare_digest(stored_hash, candidate):
        return derived_key
    return None

