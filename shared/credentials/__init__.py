"""Shared credential resolution — single source of truth for all homelab services.

Resolution chain:
  1. User-specific credentials (from store)
  2. Global/shared credentials (user_id=None in store)
  3. Environment variable fallback

Types of errors returned (not raised):
  - connector_blocked: DISABLED connector, not the owner
  - personal_missing: PERSONAL connector, user hasn't set up credentials
  - not_configured: no credentials found anywhere

Usage:
    from shared.credentials import resolve_credentials, save_credentials

    creds = resolve_credentials("todoist", user_id="abc", is_owner=True)
    if isinstance(creds, dict):
        api_key = creds["api_key"]
    else:
        print(creds["error"])
"""

from __future__ import annotations

from typing import Any

from shared.credentials.encryption import encrypt_credentials, decrypt_credentials, verify_secret
from shared.credentials.fallback import load_from_env
from shared.credentials.policies import AccessMode, get_policy
from shared.credentials.store import (
    load_credentials,
    save_credentials as _save_credentials_store,
    delete_credentials,
)


class CredentialError(Exception):
    pass


def resolve_credentials(
    connector_name: str,
    *,
    user_id: str | None = None,
    is_owner: bool = False,
) -> dict[str, Any]:
    """Resolve credentials for a connector request.

    Returns a credentials dict on success. Raises CredentialError if no
    credentials are available or the user lacks permission.
    """
    policy = get_policy(connector_name)

    if policy == AccessMode.DISABLED:
        if not is_owner:
            if user_id is not None:
                raise CredentialError(f"{connector_name} is only available for the owner.")
            env = load_from_env(connector_name)
            if env:
                return env
            raise CredentialError(f"{connector_name} is disabled.")

    if policy == AccessMode.PERSONAL:
        if user_id:
            user_creds = load_credentials(connector_name, user_id)
            if user_creds:
                return user_creds
        if is_owner:
            env = load_from_env(connector_name)
            if env:
                return env
        raise CredentialError(
            f"No credentials configured for {connector_name}. "
            f"Please add them in Settings → Credentials."
        )

    if policy == AccessMode.SHARED:
        global_creds = load_credentials(connector_name, None)
        if global_creds:
            return global_creds
        env = load_from_env(connector_name)
        if env:
            return env
        raise CredentialError(f"No shared credentials configured for {connector_name} (admin).")

    if policy == AccessMode.OPTIONAL:
        if user_id:
            user_creds = load_credentials(connector_name, user_id)
            if user_creds:
                return user_creds
        global_creds = load_credentials(connector_name, None)
        if global_creds:
            return global_creds
        env = load_from_env(connector_name)
        if env:
            return env
        raise CredentialError(f"No credentials configured for {connector_name}.")

    env = load_from_env(connector_name)
    if env:
        return env
    raise CredentialError(f"No credentials found for {connector_name}.")


def save(connector_name: str, data: dict, *, user_id: str | None = None) -> None:
    _save_credentials_store(connector_name, user_id, data)


def remove(connector_name: str, *, user_id: str | None = None) -> bool:
    return delete_credentials(connector_name, user_id)


def credential_status(connector_name: str, *, user_id: str | None = None) -> dict[str, Any]:
    """Return credential metadata WITHOUT raw secret values.

    Safe for API status responses and UI listing. Returns:
        connector_name, has_user_credentials, has_global_credentials,
        has_env_fallback, policy, user_id.
    Never returns api_key, token, or any other credential value.
    """
    policy = get_policy(connector_name)
    status = {
        "connector_name": connector_name,
        "policy": policy.value if hasattr(policy, "value") else str(policy),
        "has_user_credentials": False,
        "has_global_credentials": False,
        "has_env_fallback": False,
    }

    if user_id:
        user_creds = load_credentials(connector_name, user_id)
        status["has_user_credentials"] = user_creds is not None

    global_creds = load_credentials(connector_name, None)
    status["has_global_credentials"] = global_creds is not None

    env_creds = load_from_env(connector_name)
    status["has_env_fallback"] = env_creds is not None

    return status


def list_store_keys() -> set[str]:
    """Return all keys currently in the credential store.

    Safe — keys are connector_name:user_id strings, not credential values.
    """
    from shared.credentials.store import _read as read_store

    return set(read_store().keys())
