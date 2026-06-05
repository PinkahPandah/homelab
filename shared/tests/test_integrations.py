"""Tests for shared.integrations catalog."""
from shared.integrations import get, get_category, get_default_policy, get_fields, list_all
from shared.integrations.models import CredentialField, IntegrationDef


def test_all_connectors_have_unique_ids():
    conns = list_all()
    ids = [c.id for c in conns]
    assert len(ids) == len(set(ids)), f"Duplicate IDs: {[x for x in ids if ids.count(x) > 1]}"


def test_all_connectors_have_required_fields():
    for c in list_all():
        assert c.id, f"{c} missing id"
        assert c.display_name, f"{c.id} missing display_name"
        assert c.description, f"{c.id} missing description"
        assert c.category, f"{c.id} missing category"
        assert c.default_policy in (
            "shared", "personal", "optional", "disabled"
        ), f"{c.id} bad policy: {c.default_policy}"


def test_credential_fields_have_valid_structure():
    for c in list_all():
        seen_keys = set()
        for f in c.credential_fields:
            assert f.key, f"{c.id} field missing key"
            assert f.label, f"{c.id}.{f.key} missing label"
            assert isinstance(f.secret, bool), f"{c.id}.{f.key} secret not bool"
            assert f.key not in seen_keys, f"{c.id} duplicate field key: {f.key}"
            seen_keys.add(f.key)


def test_get_returns_correct_connector():
    assert get("todoist") is not None
    assert get("todoist").id == "todoist"
    assert get("nonexistent") is None


def test_get_category_returns_correct_value():
    assert get_category("mealie") == "productivity"
    assert get_category("immich") == "media"
    assert get_category("atlas") == "knowledge"
    assert get_category("nonexistent") is None


def test_get_default_policy():
    assert get_default_policy("todoist") == "personal"
    assert get_default_policy("n8n") == "disabled"
    assert get_default_policy("nonexistent") is None


def test_get_fields_returns_empty_for_connectors_without_credentials():
    assert get_fields("docker") == []
    assert get_fields("substack") == []


def test_get_fields_returns_correct_keys():
    fields = get_fields("mealie")
    keys = {f.key for f in fields}
    assert "url" in keys
    assert "api_key" in keys


def test_category_consistency():
    known = {
        "todoist": "productivity",
        "mealie": "productivity",
        "immich": "media",
        "atlas": "knowledge",
        "grafana": "monitoring",
        "actualbudget": "finance",
        "dawarich": "tracking",
        "n8n": "automation",
        "lubelogger": "vehicle",
    }
    for cid, exp in known.items():
        assert get_category(cid) == exp, f"{cid} should be {exp}"


def test_disabled_connectors():
    disabled = [c.id for c in list_all() if c.default_policy == "disabled"]
    assert "n8n" in disabled
    assert "docker" in disabled
    assert "nexus" in disabled


def test_every_connector_is_an_integration_def():
    for c in list_all():
        assert isinstance(c, IntegrationDef)


def test_list_all_returns_copy():
    a = list_all()
    b = list_all()
    assert a is not b
    assert len(a) == len(b)
