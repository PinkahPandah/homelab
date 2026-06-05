"""Access modes and default policies for connector credentials.

Admin overrides live in policies.json next to the credential store.
Changes take effect immediately without container restart.
"""

from __future__ import annotations

import json
import os
import threading
from enum import Enum
from pathlib import Path


class AccessMode(str, Enum):
    DISABLED = "disabled"
    SHARED = "shared"
    PERSONAL = "personal"
    OPTIONAL = "optional"


DEFAULT_POLICIES: dict[str, AccessMode] = {
    "docker":         AccessMode.DISABLED,
    "n8n":            AccessMode.DISABLED,
    "nexus":          AccessMode.DISABLED,
    "atlas":          AccessMode.SHARED,
    "crisis_score":   AccessMode.SHARED,
    "substack":       AccessMode.SHARED,
    "ntfy":           AccessMode.SHARED,
    "searxng":        AccessMode.SHARED,
    "uptimekuma":     AccessMode.SHARED,
    "homeassistant":  AccessMode.SHARED,
    "coingecko":      AccessMode.SHARED,
    "dawarich":       AccessMode.PERSONAL,
    "yamtrack":       AccessMode.PERSONAL,
    "lubelogger":     AccessMode.SHARED,
    "grafana":        AccessMode.SHARED,
    "booklore":       AccessMode.PERSONAL,
    "adventurelog":   AccessMode.PERSONAL,
    "vouchervault":   AccessMode.SHARED,
    "endurain":       AccessMode.PERSONAL,
    "sparkyfitness":  AccessMode.PERSONAL,
    "nextcloud":      AccessMode.PERSONAL,
    "mercato":        AccessMode.PERSONAL,
    "todoist":        AccessMode.PERSONAL,
    "crawl4ai":       AccessMode.SHARED,
    "crawl4ai_stealth": AccessMode.SHARED,
    "trivago":        AccessMode.SHARED,
    "ourgroceries":   AccessMode.SHARED,
    "yazio":          AccessMode.PERSONAL,
    "deepl":          AccessMode.SHARED,
    "openweathermap": AccessMode.SHARED,
    "tmdb":           AccessMode.SHARED,
    "opensky":        AccessMode.SHARED,
    "parcelsapp":     AccessMode.SHARED,
    "google_places": AccessMode.SHARED,
    "google_routes": AccessMode.SHARED,
    "foursquare": AccessMode.SHARED,
    "github":         AccessMode.PERSONAL,
    "notion":         AccessMode.PERSONAL,
    "hortusfox":      AccessMode.SHARED,
    "openwebui":      AccessMode.SHARED,
    "actualbudget":   AccessMode.PERSONAL,
    "ghostfolio":     AccessMode.PERSONAL,
    "karakeep":       AccessMode.PERSONAL,
    "paperless":      AccessMode.PERSONAL,
    "immich":         AccessMode.PERSONAL,
    "mealie":         AccessMode.PERSONAL,
    "grocy":          AccessMode.SHARED,
    "homebox":        AccessMode.SHARED
}


def _policies_path() -> Path:
    return (
        Path(os.getenv("SHARED_CREDENTIALS_PATH", "/app/shared/credentials/store.json")).parent
        / "policies.json"
    )


_override_mtime: float = 0
_overrides_cache: dict[str, str] | None = None
_policy_lock = threading.Lock()


def _read_overrides() -> dict[str, str]:
    global _override_mtime, _overrides_cache

    try:
        path = _policies_path()
        if not path.exists():
            _override_mtime = 0
            _overrides_cache = {}
            return {}
        mtime = path.stat().st_mtime
    except OSError:
        _override_mtime = 0
        _overrides_cache = {}
        return {}

    if _overrides_cache is not None and mtime == _override_mtime:
        return _overrides_cache

    try:
        raw = json.loads(path.read_text())
        _override_mtime = mtime
        if isinstance(raw, dict):
            _overrides_cache = raw
            return raw
    except Exception:
        pass

    _overrides_cache = {}
    return {}


def get_policy(connector_name: str) -> AccessMode:
    overrides = _read_overrides()
    if connector_name in overrides:
        try:
            return AccessMode(overrides[connector_name])
        except ValueError:
            pass
    return DEFAULT_POLICIES.get(connector_name, AccessMode.SHARED)


def list_policies() -> dict[str, str]:
    merged = {k: v.value for k, v in DEFAULT_POLICIES.items()}
    merged.update(_read_overrides())
    return merged


def set_policy(connector_name: str, mode: str | AccessMode) -> None:
    if isinstance(mode, AccessMode):
        mode = mode.value
    if mode not in {"disabled", "shared", "personal", "optional"}:
        raise ValueError(f"Invalid access mode: {mode}")

    with _policy_lock:
        overrides = _read_overrides()
        overrides[connector_name] = mode
        _write_overrides(overrides)


def delete_policy_override(connector_name: str) -> bool:
    with _policy_lock:
        overrides = _read_overrides()
        if connector_name in overrides:
            del overrides[connector_name]
            _write_overrides(overrides)
            return True
        return False


def _write_overrides(overrides: dict[str, str]) -> None:
    global _override_mtime, _overrides_cache
    path = _policies_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(overrides, indent=2))

    try:
        _override_mtime = path.stat().st_mtime
    except OSError:
        _override_mtime = 0
    _overrides_cache = overrides
