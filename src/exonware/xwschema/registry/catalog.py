#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/registry/catalog.py
Schema Catalog (DDL-like API)
Local schema catalog with CREATE/ALTER/DROP equivalent operations.
Persists to a JSON file for use by xwstorage and xwquery for schema-on-write.
Versioned schema entries; optional compatibility checks via registry.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field
from exonware.xwsystem import get_logger, get_serializer, JsonSerializer
logger = get_logger(__name__)
# Reuse xwsystem JsonSerializer (flyweight) for catalog persistence and performance
_json = get_serializer(JsonSerializer)


def _deep_merge(base: dict[str, Any], updates: dict[str, Any]) -> None:
    """Merge updates into base in-place; nested dicts are merged recursively."""
    for k, v in updates.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v
@dataclass


class SchemaCatalogEntry:
    """Single schema entry in the catalog."""
    name: str
    definition: dict[str, Any]
    version: int = 1
    schema_type: str = "JSON"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "definition": self.definition,
            "version": self.version,
            "schema_type": self.schema_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }
    @classmethod

    def from_dict(cls, data: dict[str, Any]) -> "SchemaCatalogEntry":
        return cls(
            name=data["name"],
            definition=data["definition"],
            version=data.get("version", 1),
            schema_type=data.get("schema_type", "JSON"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            metadata=data.get("metadata", {}),
        )


class SchemaCatalog:
    """
    DDL-like schema catalog: create_schema, alter_schema, drop_schema.
    Persists to a local JSON file; usable by xwstorage/xwquery for schema-on-write.
    """

    def __init__(self, catalog_path: str | Path):
        self._path = Path(catalog_path)
        self._cache: dict[str, SchemaCatalogEntry] = {}
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        if self._path.exists():
            try:
                data = _json.load_file(self._path)
                if not isinstance(data, dict):
                    data = {}
                self._cache = {
                    k: SchemaCatalogEntry.from_dict(v)
                    for k, v in data.get("schemas", {}).items()
                }
            except Exception as e:
                logger.warning("Schema catalog load failed: %s", e)
                self._cache = {}
        self._loaded = True

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schemas": {k: v.to_dict() for k, v in self._cache.items()},
        }
        _json.save_file(data, self._path)

    def create_schema(self, name: str, definition: dict[str, Any], schema_type: str = "JSON") -> SchemaCatalogEntry:
        """Create a new schema (CREATE equivalent)."""
        from datetime import datetime, timezone
        self._load()
        if name in self._cache:
            raise ValueError(f"Schema already exists: {name}")
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        entry = SchemaCatalogEntry(
            name=name,
            definition=definition,
            version=1,
            schema_type=schema_type,
            created_at=now,
            updated_at=now,
        )
        self._cache[name] = entry
        self._save()
        logger.debug("Created schema %s", name)
        return entry

    def alter_schema(self, name: str, changes: dict[str, Any]) -> SchemaCatalogEntry:
        """Alter an existing schema (ALTER equivalent). Updates definition and bumps version."""
        from datetime import datetime, timezone
        self._load()
        if name not in self._cache:
            raise ValueError(f"Schema not found: {name}")
        entry = self._cache[name]
        # Apply changes: deep-merge definition so nested keys (e.g. properties) are merged
        defn = dict(entry.definition)
        for key, value in changes.items():
            if key == "definition" and isinstance(value, dict):
                _deep_merge(defn, value)
            elif key != "definition":
                entry.metadata[key] = value
        entry.definition = defn
        entry.version += 1
        entry.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self._save()
        logger.debug("Altered schema %s to version %s", name, entry.version)
        return entry

    def drop_schema(self, name: str) -> None:
        """Drop a schema (DROP equivalent)."""
        self._load()
        if name not in self._cache:
            raise ValueError(f"Schema not found: {name}")
        del self._cache[name]
        self._save()
        logger.debug("Dropped schema %s", name)

    def get_schema(self, name: str) -> Optional[SchemaCatalogEntry]:
        """Get schema by name."""
        self._load()
        return self._cache.get(name)

    def get_schema_version(self, name: str) -> Optional[int]:
        """Return current version of schema, or None if not found."""
        entry = self.get_schema(name)
        return entry.version if entry else None

    def list_schemas(self) -> list[str]:
        """List all schema names."""
        self._load()
        return list(self._cache.keys())


def apply_migration(
    catalog: SchemaCatalog,
    name: str,
    definition_updates: dict[str, Any],
) -> SchemaCatalogEntry:
    """
    Apply a migration by merging definition_updates into the schema's definition.
    Uses alter_schema under the hood; bumps version and persists. Use for
    schema evolution (add/change properties, required, etc.) in one step.
    """
    return catalog.alter_schema(name, {"definition": definition_updates})


def diff_schema_definitions(
    old_def: dict[str, Any],
    new_def: dict[str, Any],
    prefix: str = "",
) -> list[tuple[str, str, Any, Any]]:
    """
    Compare two schema definition dicts; return list of (path, change_type, old_val, new_val).
    change_type is "added", "removed", or "changed". Path is dot-separated (e.g. "properties.email.type").
    Useful for migration tooling and audit.
    """
    result: list[tuple[str, str, Any, Any]] = []
    def path_str(p: str, k: str) -> str:
        return f"{p}.{k}" if p else k
    if not isinstance(old_def, dict) or not isinstance(new_def, dict):
        if old_def != new_def:
            result.append((prefix or ".", "changed", old_def, new_def))
        return result
    all_keys = set(old_def) | set(new_def)
    for k in sorted(all_keys):
        p = path_str(prefix, k)
        old_val = old_def.get(k)
        new_val = new_def.get(k)
        if k not in old_def:
            result.append((p, "added", None, new_val))
        elif k not in new_def:
            result.append((p, "removed", old_val, None))
        elif isinstance(old_val, dict) and isinstance(new_val, dict):
            result.extend(diff_schema_definitions(old_val, new_val, prefix=p))
        elif old_val != new_val:
            result.append((p, "changed", old_val, new_val))
    return result
