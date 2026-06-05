"""Shared integrations catalog — canonical metadata for all homelab connectors.

Usage:
    from shared.integrations import list_all, get, get_category, get_fields, get_default_policy

    for conn in list_all():
        print(conn.display_name, conn.category)

    mealie = get("mealie")
    if mealie:
        for field in mealie.credential_fields:
            print(f"  {field.key}: {field.label} (secret={field.secret})")
"""

from shared.integrations.connectors import (
    ALL,
    get,
    get_category,
    get_default_policy,
    get_fields,
    list_all,
)
from shared.integrations.models import CredentialField, IntegrationDef

__all__ = [
    "ALL",
    "CredentialField",
    "IntegrationDef",
    "get",
    "get_category",
    "get_default_policy",
    "get_fields",
    "list_all",
]
