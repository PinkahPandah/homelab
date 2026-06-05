"""JSON-file credential store — no database dependency."""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path

from shared.credentials.encryption import encrypt_credentials, decrypt_credentials

_lock = threading.Lock()


def _store_path() -> Path:
    return Path(os.getenv("SHARED_CREDENTIALS_PATH", "/app/shared/credentials/store.json"))


def _read() -> dict:
    path = _store_path()
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _write(data: dict) -> None:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def load_credentials(connector_name: str, user_id: str | None) -> dict | None:
    with _lock:
        store = _read()
        key = _store_key(connector_name, user_id)
        token = store.get(key)
        if not token:
            return None
        try:
            data = decrypt_credentials(token)
        except ValueError:
            return None

        if data.pop("__needs_migration__", False):
            store[key] = encrypt_credentials(data)
            _write(store)

        return data


def save_credentials(connector_name: str, user_id: str | None, data: dict) -> None:
    with _lock:
        store = _read()
        key = _store_key(connector_name, user_id)
        store[key] = encrypt_credentials(data)
        _write(store)


def delete_credentials(connector_name: str, user_id: str | None) -> bool:
    with _lock:
        store = _read()
        key = _store_key(connector_name, user_id)
        if key in store:
            del store[key]
            _write(store)
            return True
        return False


def _store_key(connector_name: str, user_id: str | None) -> str:
    uid = user_id or "__global__"
    return f"{connector_name}:{uid}"
