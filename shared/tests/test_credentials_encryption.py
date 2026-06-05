"""Tests for shared.credentials encryption, migration, and API safety."""
import json
from pathlib import Path

import pytest
from shared.credentials import credential_status, save, remove
from shared.credentials.encryption import (
    _derive_fernet,
    _get_secret_fingerprint,
    _reset_cache,
    decrypt_credentials,
    encrypt_credentials,
    verify_secret,
)


def _encrypt_with_key(data: dict, secret: str) -> str:
    f = _derive_fernet(secret)
    return f.encrypt(json.dumps(data).encode()).decode()


def _decrypt_with_key(token: str, secret: str) -> dict:
    f = _derive_fernet(secret)
    return json.loads(f.decrypt(token.encode()).decode())


@pytest.fixture(autouse=True)
def _reset_fernet_between_tests():
    _reset_cache()
    yield
    _reset_cache()


@pytest.fixture
def store_env(monkeypatch, tmp_path):
    store_path = tmp_path / "store.json"
    monkeypatch.setenv("SHARED_CREDENTIALS_PATH", str(store_path))
    monkeypatch.setenv("SHARED_CREDENTIALS_SECRET", "test-secret-42")
    return store_path


def test_encrypt_decrypt_roundtrip(store_env):
    data = {"api_key": "abc123"}
    token = encrypt_credentials(data)
    assert decrypt_credentials(token) == data


def test_missing_secret_raises_on_encrypt(monkeypatch):
    monkeypatch.delenv("SHARED_CREDENTIALS_SECRET", raising=False)
    _reset_cache()
    with pytest.raises(RuntimeError, match="SHARED_CREDENTIALS_SECRET"):
        encrypt_credentials({"x": "y"})


def test_missing_secret_raises_on_decrypt(monkeypatch):
    monkeypatch.delenv("SHARED_CREDENTIALS_SECRET", raising=False)
    _reset_cache()
    with pytest.raises(RuntimeError, match="SHARED_CREDENTIALS_SECRET"):
        decrypt_credentials("fake-token")


def test_decrypt_with_old_key_migrates(store_env):
    old_token = _encrypt_with_key({"api_key": "old"}, "changeme")
    result = decrypt_credentials(old_token)
    assert result["api_key"] == "old"
    assert result["__needs_migration__"] is True


def test_decrypt_bad_token_raises(store_env):
    with pytest.raises(ValueError, match="secret key mismatch"):
        decrypt_credentials("garbage")


def test_store_auto_migrates_on_load(store_env):
    old_token = _encrypt_with_key({"api_key": "old"}, "changeme")
    store_env.write_text(json.dumps({"tc:__global__": old_token}))

    from shared.credentials.store import load_credentials

    result = load_credentials("tc", None)
    assert result == {"api_key": "old"}

    stored = json.loads(store_env.read_text())
    assert _decrypt_with_key(stored["tc:__global__"], "test-secret-42") == {
        "api_key": "old"
    }


def test_credential_status_no_raw_values(store_env):
    save("tc", {"api_key": "sec", "token": "xyz"}, user_id=None)
    s = credential_status("tc", user_id=None)
    assert "api_key" not in s
    assert "token" not in s
    assert "sec" not in json.dumps(s).lower()
    assert s["has_global_credentials"] is True


def test_credential_status_unconfigured(store_env):
    s = credential_status("unknown", user_id="u1")
    assert s["has_user_credentials"] is False
    assert s["has_env_fallback"] is False


def test_verify_secret_ok(store_env):
    store_env.write_text("{}")
    r = verify_secret()
    assert r["status"] == "ok"
    assert r["needs_migration"] == 0


def test_verify_secret_missing(monkeypatch):
    monkeypatch.delenv("SHARED_CREDENTIALS_SECRET", raising=False)
    _reset_cache()
    r = verify_secret()
    assert r["status"] == "error"


def test_verify_secret_counts_migration_candidates(store_env):
    store_env.write_text(
        json.dumps({"tc:__global__": _encrypt_with_key({"x": "y"}, "changeme")})
    )
    r = verify_secret()
    assert r["needs_migration"] == 1


def test_save_load_uses_new_secret(store_env):
    save("tc", {"api_key": "fresh"}, user_id=None)
    from shared.credentials.store import load_credentials

    assert load_credentials("tc", None) == {"api_key": "fresh"}


def test_delete_removes_entry(store_env):
    save("tc", {"x": "y"}, user_id="u1")
    assert remove("tc", user_id="u1") is True
    from shared.credentials.store import load_credentials

    assert load_credentials("tc", "u1") is None


def test_fingerprint_is_safe(store_env):
    fp = _get_secret_fingerprint()
    assert len(fp) == 8
    assert "test-secret-42" not in fp
