import os
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ARGON2_TIME_COST = 2
ARGON2_MEMORY_COST = 65536
ARGON2_PARALLELISM = 2
ARGON2_HASH_LEN = 32

def derive_key(password: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        secret=password.encode("utf-8"),
        salt = salt,
        time_cost = ARGON2_TIME_COST,
        memory_cost = ARGON2_MEMORY_COST,
        parallelism = ARGON2_PARALLELISM,
        hash_len = ARGON2_HASH_LEN,
        type = Type.ID
    )

def generate_salt() -> bytes:
    return os.urandom(16)

def generate_nonce() -> bytes:
    return os.urandom(12)

def encrypt(plaintext: str, key: bytes) -> [bytes, bytes]:
    nonce = generate_nonce()
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return ct, nonce

def decrypt(ciphertext: bytes, nonce: bytes, key: bytes) -> str:
    aesgcm = AESGCM(key)
    pt = aesgcm.decrypt(nonce, ciphertext, None)
    return pt.decode("utf-8")

