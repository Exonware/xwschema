#!/usr/bin/env python3
"""
Unit tests for xwschema Schema Catalog (DDL-like API).
Tests SchemaCatalog and SchemaCatalogEntry: create_schema, alter_schema,
drop_schema, get_schema, list_schemas, persistence, and integration
with schema-on-write use cases.
Company: eXonware.com
"""

import pytest
import tempfile
from pathlib import Path
from exonware.xwsystem import get_serializer, JsonSerializer
from exonware.xwschema.registry.catalog import (
    SchemaCatalog,
    SchemaCatalogEntry,
    apply_migration,
    diff_schema_definitions,
)
@pytest.mark.xwschema_unit
@pytest.mark.xwschema_registry


class TestSchemaCatalogEntry:
    """Test SchemaCatalogEntry dataclass."""

    def test_from_dict_minimal(self):
        """Entry from dict with required fields only."""
        data = {"name": "users", "definition": {"type": "object"}}
        entry = SchemaCatalogEntry.from_dict(data)
        assert entry.name == "users"
        assert entry.definition == {"type": "object"}
        assert entry.version == 1
        assert entry.schema_type == "JSON"

    def test_from_dict_full(self):
        """Entry from dict with all fields."""
        data = {
            "name": "orders",
            "definition": {"type": "object", "properties": {"id": {"type": "string"}}},
            "version": 3,
            "schema_type": "AVRO",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-02T00:00:00Z",
            "metadata": {"owner": "team-a"},
        }
        entry = SchemaCatalogEntry.from_dict(data)
        assert entry.name == "orders"
        assert entry.version == 3
        assert entry.schema_type == "AVRO"
        assert entry.metadata == {"owner": "team-a"}

    def test_to_dict_roundtrip(self):
        """to_dict then from_dict preserves data."""
        entry = SchemaCatalogEntry(
            name="test",
            definition={"type": "string"},
            version=2,
            schema_type="JSON",
            metadata={"k": "v"},
        )
        data = entry.to_dict()
        back = SchemaCatalogEntry.from_dict(data)
        assert back.name == entry.name
        assert back.definition == entry.definition
        assert back.version == entry.version
        assert back.metadata == entry.metadata
@pytest.mark.xwschema_unit
@pytest.mark.xwschema_registry


class TestSchemaCatalog:
    """Test SchemaCatalog DDL-like API and persistence."""
    @pytest.fixture

    def catalog_path(self, tmp_path):
        """Temporary catalog file path."""
        return tmp_path / "schema_catalog.json"
    @pytest.fixture

    def catalog(self, catalog_path):
        """SchemaCatalog instance with temp path."""
        return SchemaCatalog(catalog_path)

    def test_create_schema(self, catalog):
        """create_schema adds entry and persists."""
        defn = {"type": "object", "properties": {"name": {"type": "string"}}}
        entry = catalog.create_schema("users", defn)
        assert entry.name == "users"
        assert entry.definition == defn
        assert entry.version == 1
        assert entry.created_at is not None
        assert catalog.get_schema("users") is not None
        assert "users" in catalog.list_schemas()

    def test_create_schema_duplicate_raises(self, catalog):
        """create_schema with existing name raises."""
        catalog.create_schema("users", {"type": "object"})
        with pytest.raises(ValueError, match="already exists"):
            catalog.create_schema("users", {"type": "string"})

    def test_alter_schema(self, catalog):
        """alter_schema updates definition and bumps version."""
        catalog.create_schema("users", {"type": "object", "properties": {"a": {}}})
        entry = catalog.alter_schema("users", {"definition": {"properties": {"b": {}}}})
        assert entry.version == 2
        assert "a" in entry.definition.get("properties", {})
        assert "b" in entry.definition.get("properties", {})

    def test_alter_schema_not_found_raises(self, catalog):
        """alter_schema for missing schema raises."""
        with pytest.raises(ValueError, match="not found"):
            catalog.alter_schema("missing", {"definition": {}})

    def test_drop_schema(self, catalog):
        """drop_schema removes entry and persists."""
        catalog.create_schema("users", {"type": "object"})
        catalog.drop_schema("users")
        assert catalog.get_schema("users") is None
        assert "users" not in catalog.list_schemas()

    def test_drop_schema_not_found_raises(self, catalog):
        """drop_schema for missing schema raises."""
        with pytest.raises(ValueError, match="not found"):
            catalog.drop_schema("missing")

    def test_get_schema_none_for_missing(self, catalog):
        """get_schema returns None for missing name."""
        assert catalog.get_schema("nonexistent") is None

    def test_get_schema_version(self, catalog):
        """get_schema_version returns version or None."""
        assert catalog.get_schema_version("missing") is None
        catalog.create_schema("v1", {"type": "object"})
        assert catalog.get_schema_version("v1") == 1
        catalog.alter_schema("v1", {"definition": {"properties": {"x": {}}}})
        assert catalog.get_schema_version("v1") == 2

    def test_list_schemas_empty(self, catalog):
        """list_schemas returns empty list for new catalog."""
        assert catalog.list_schemas() == []

    def test_persistence_across_instances(self, catalog_path):
        """Catalog persists to file; new instance loads same data."""
        c1 = SchemaCatalog(catalog_path)
        c1.create_schema("users", {"type": "object"})
        c1.create_schema("orders", {"type": "array"})
        c2 = SchemaCatalog(catalog_path)
        assert set(c2.list_schemas()) == {"users", "orders"}
        assert c2.get_schema("users").definition == {"type": "object"}

    def test_catalog_file_readable_by_xwsystem_json_serializer(self, catalog_path):
        """Reuse: catalog file is written/read with xwsystem JsonSerializer (same stack)."""
        c = SchemaCatalog(catalog_path)
        c.create_schema("test", {"type": "object", "properties": {"name": {"type": "string"}}})
        serializer = get_serializer(JsonSerializer)
        data = serializer.load_file(catalog_path)
        assert "schemas" in data and "test" in data["schemas"]
        assert data["schemas"]["test"]["definition"]["type"] == "object"
        assert data["schemas"]["test"]["version"] == 1

    def test_schema_type_parameter(self, catalog):
        """create_schema accepts schema_type."""
        entry = catalog.create_schema("evt", {"type": "record"}, schema_type="AVRO")
        assert entry.schema_type == "AVRO"
@pytest.mark.xwschema_unit
@pytest.mark.xwschema_registry


class TestApplyMigration:
    """Test apply_migration helper (schema evolution)."""

    def test_apply_migration_merges_and_bumps_version(self, tmp_path):
        """apply_migration merges definition_updates and bumps version."""
        catalog = SchemaCatalog(tmp_path / "catalog.json")
        catalog.create_schema("users", {"type": "object", "properties": {"name": {"type": "string"}}})
        entry = apply_migration(catalog, "users", {"properties": {"email": {"type": "string"}}, "required": ["name"]})
        assert entry.version == 2
        assert "name" in entry.definition.get("properties", {})
        assert "email" in entry.definition.get("properties", {})
        assert "name" in entry.definition.get("required", [])

    def test_apply_migration_not_found_raises(self, tmp_path):
        """apply_migration for missing schema raises."""
        catalog = SchemaCatalog(tmp_path / "catalog.json")
        with pytest.raises(ValueError, match="not found"):
            apply_migration(catalog, "missing", {"properties": {}})
@pytest.mark.xwschema_unit
@pytest.mark.xwschema_registry


class TestDiffSchemaDefinitions:
    """Test diff_schema_definitions for migration/audit."""

    def test_no_change(self):
        """Identical defs yield no diff."""
        d = {"type": "object", "properties": {"a": {"type": "string"}}}
        assert diff_schema_definitions(d, d) == []

    def test_added_key(self):
        """New key in new_def is 'added'."""
        old = {"type": "object"}
        new = {"type": "object", "properties": {"x": {"type": "string"}}}
        diff = diff_schema_definitions(old, new)
        assert any(r[1] == "added" and r[0] == "properties" for r in diff)
        assert next(r for r in diff if r[0] == "properties" and r[1] == "added")[3] == {"x": {"type": "string"}}

    def test_removed_key(self):
        """Missing key in new_def is 'removed'."""
        old = {"type": "object", "required": ["name"]}
        new = {"type": "object"}
        diff = diff_schema_definitions(old, new)
        assert any(r[1] == "removed" and r[0] == "required" for r in diff)

    def test_changed_value(self):
        """Changed value is 'changed' (dotted path for nested)."""
        old = {"type": "object", "properties": {"age": {"type": "integer"}}}
        new = {"type": "object", "properties": {"age": {"type": "number"}}}
        diff = diff_schema_definitions(old, new)
        assert any(r[1] == "changed" and "age" in r[0] for r in diff)
        row = next(r for r in diff if r[1] == "changed" and "age" in r[0])
        assert row[2] == "integer" and row[3] == "number"

    def test_nested_diff(self):
        """Nested dicts produce dotted paths."""
        old = {"properties": {"user": {"type": "object", "properties": {"name": {"type": "string"}}}}}
        new = {"properties": {"user": {"type": "object", "properties": {"name": {"type": "string"}, "email": {"type": "string"}}}}}
        diff = diff_schema_definitions(old, new)
        paths = [r[0] for r in diff]
        assert any("properties.user.properties.email" in p for p in paths)
        assert any(r[1] == "added" for r in diff)
