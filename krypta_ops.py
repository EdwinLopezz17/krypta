import uuid
import threading
import pyperclip
import random
import string
from db     import get_connection
from crypto import encrypt, decrypt

def add_entry(service: str, username: str, password: str, key: bytes) -> str:

    entry_id          = str(uuid.uuid4())
    encrypted_payload, nonce = encrypt(password, key)

    conn = get_connection()
    with conn:
        conn.execute(
            """INSERT INTO passwords (uuid, service, username, encrypted_payload, nonce)
               VALUES (?, ?, ?, ?, ?)""",
            (entry_id, service.strip(), username.strip(), encrypted_payload, nonce),
        )
    conn.close()
    return entry_id

def list_entries(search: str = "") -> list[dict]:

    conn = get_connection()
    cur  = conn.cursor()
    if search:
        cur.execute(
            """SELECT uuid, service, username, updated_at
               FROM passwords
               WHERE service LIKE ?
               ORDER BY service COLLATE NOCASE""",
            (f"%{search}%",),
        )
    else:
        cur.execute(
            """SELECT uuid, service, username, updated_at
               FROM passwords
               ORDER BY service COLLATE NOCASE"""
        )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_password(entry_id: str, key: bytes) -> str | None:

    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "SELECT encrypted_payload, nonce FROM passwords WHERE uuid = ?",
        (entry_id,),
    )
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    return decrypt(row["encrypted_payload"], row["nonce"], key)

def update_entry(entry_id: str, service: str, username: str,
                 password: str, key: bytes) -> bool:

    encrypted_payload, nonce = encrypt(password, key)

    conn = get_connection()
    with conn:
        cur = conn.execute(
            """UPDATE passwords
               SET service = ?, username = ?, encrypted_payload = ?,
                   nonce = ?, updated_at = CURRENT_TIMESTAMP
               WHERE uuid = ?""",
            (service.strip(), username.strip(), encrypted_payload, nonce, entry_id),
        )
    affected = cur.rowcount
    conn.close()
    return affected > 0

def delete_entry(entry_id: str) -> bool:

    conn = get_connection()
    with conn:
        cur = conn.execute(
            "DELETE FROM passwords WHERE uuid = ?", (entry_id,)
        )
    affected = cur.rowcount
    conn.close()
    return affected > 0

_clipboard_timer: threading.Timer | None = None

def copy_to_clipboard(text: str, clear_after: int = 30) -> None:

    global _clipboard_timer

    if _clipboard_timer and _clipboard_timer.is_alive():
        _clipboard_timer.cancel()

    pyperclip.copy(text)

    def _clear():
        try:
            if pyperclip.paste() == text:
                pyperclip.copy("")
                print("\n  [Clipboard] Portapapeles limpiado automáticamente.")
        except Exception:
            pass

    _clipboard_timer = threading.Timer(clear_after, _clear)
    _clipboard_timer.daemon = True
    _clipboard_timer.start()
    print(f"  [Clipboard] Copiado. Se borrará en {clear_after}s.")


def generate_password(
    length: int = 20,
    use_upper: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:

    pool     = string.ascii_lowercase
    required = [random.choice(string.ascii_lowercase)]

    if use_upper:
        pool     += string.ascii_uppercase
        required.append(random.choice(string.ascii_uppercase))
    if use_digits:
        pool     += string.digits
        required.append(random.choice(string.digits))
    if use_symbols:
        symbols   = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        pool     += symbols
        required.append(random.choice(symbols))

    remaining = [random.choice(pool) for _ in range(length - len(required))]
    password  = required + remaining

    random.SystemRandom().shuffle(password)
    return "".join(password)

