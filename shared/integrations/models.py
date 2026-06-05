"""Typed connector definitions — canonical metadata for all homelab integrations."""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CredentialField:
    key: str
    label: str
    secret: bool = True


@dataclass
class IntegrationDef:
    id: str
    display_name: str
    description: str
    category: str
    credential_fields: list[CredentialField] = field(default_factory=list)
    default_policy: str = "shared"
    doc_url: str | None = None
