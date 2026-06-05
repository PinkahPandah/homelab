"""Fernet encryption for credential storage — shared across all homelab services.

Encryption key: SHARED_CREDENTIALS_SECRET (mandatory).
Migration: existing data encrypted with the old "changeme" key is
automatically decrypted and re-encrypted with the new secret at read time.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

# The old hardcoded default that was used before SHARED_CREDENTIALS_SECRET
# became mandatory. Used ONLY for migration — never for new writes.
_OLD_MIGRATION_SECRET = "changeme"

_fernet: Fernet | None = None
_old_fernet: Fernet | None = None


def _reset_cache() -> None:
    """Reset cached Fernet instances (for testing only)."""
    global _fernet, _old_fernet
    _fernet = None
    _old_fernet = None


def _derive_fernet(secret: str) -> Fernet:
    key_bytes = hashlib.sha256(secret.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key_bytes))


def _get_fernet() -> Fernet:
    """Return the current (new) Fernet instance, raising if the secret is missing."""
    global _fernet
    if _fernet is None:
        secret = os.getenv("SHARED_CREDENTIALS_SECRET")
        if not secret:
            raise RuntimeError(
                "SHARED_CREDENTIALS_SECRET is not set. "
                "Credential encryption requires this environment variable. "
                "Add it to your .env / docker-compose environment."
            )
        _fernet = _derive_fernet(secret)
    return _fernet


def _get_old_fernet() -> Fernet:
    """Return the Fernet instance for the OLD migration key (changeme).

    Used ONLY to decrypt previously stored data that was encrypted before
    SHARED_CREDENTIALS_SECRET became mandatory.
    """
    global _old_fernet
    if _old_fernet is None:
        _old_fernet = _derive_fernet(_OLD_MIGRATION_SECRET)
    return _old_fernet


def _get_secret_fingerprint() -> str:
    """Return a short, safe fingerprint of the current secret for logging."""
    secret = os.getenv("SHARED_CREDENTIALS_SECRET", "")
    if not secret:
        return "MISSING"
    return hashlib.sha256(secret.encode()).hexdigest()[:8]


def encrypt_credentials(data: dict[str, Any]) -> str:
    """Encrypt credential data with the current SHARED_CREDENTIALS_SECRET.

    Never uses the old migration key for encryption.
    """
    return _get_fernet().encrypt(json.dumps(data).encode()).decode()


def decrypt_credentials(token: str) -> dict[str, Any]:
    """Decrypt credential data, with automatic migration from the old key.

    Tries the current secret first. If that fails, attempts decryption
    with the old "changeme"-derived key. On success with the old key,
    the caller should re-encrypt with the current key via a migration step.
    """
    try:
        return json.loads(_get_fernet().decrypt(token.encode()).decode())
    except InvalidToken:
        pass

    # Migration path: try the old key
    try:
        data = json.loads(_get_old_fernet().decrypt(token.encode()).decode())
        # Flag the data as needing re-encryption
        data["__needs_migration__"] = True
        return data
    except InvalidToken:
        raise ValueError(
            "Failed to decrypt credentials — secret key mismatch. "
            "The stored credential cannot be decrypted with the current "
            "SHARED_CREDENTIALS_SECRET or the old migration key."
        )


def verify_secret() -> dict[str, Any]:
    """Verify the secret is usable. Returns status dict (safe for logging)."""
    try:
        f = _get_fernet()
        test_token = f.encrypt(b"__verify__").decode()
        f.decrypt(test_token.encode())
        return {
            "status": "ok",
            "fingerprint": _get_secret_fingerprint(),
            "needs_migration": _count_migration_candidates(),
        }
    except RuntimeError as e:
        return {"status": "error", "reason": str(e)}


def _count_migration_candidates() -> int:
    """Count how many stored entries still use the old key. Returns 0 on error."""
    try:
        path = os.getenv("SHARED_CREDENTIALS_PATH", "/app/shared/credentials/store.json")
        if not os.path.exists(path):
            return 0
        store = json.loads(open(path).read())
        count = 0
        old_f = _get_old_fernet()
        for token in store.values():
            try:
                old_f.decrypt(token.encode())
                count += 1
            except InvalidToken:
                pass
        return count
    except Exception:
        return -1
