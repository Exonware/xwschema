#!/usr/bin/env python3
"""
Unit tests for xwschema Schema Registry (ConfluentSchemaRegistry, etc.).
Verifies schema string normalization uses xwsystem get_serializer(JsonSerializer)
(reuse and production consistency with catalog, xwstorage, xwdata).
"""

import pytest
from exonware.xwsystem import get_serializer, JsonSerializer
@pytest.mark.xwschema_unit
@pytest.mark.xwschema_registry


class TestSchemaRegistryJsonReuse:
    """Schema registry uses xwsystem JsonSerializer for normalization."""

    def test_json_ser_roundtrip(self):
        """_json_ser() from schema_registry round-trips schema dict (xwsystem JSON)."""
        from exonware.xwschema.registry.schema_registry import _json_ser
        j = _json_ser()
        data = {"type": "string", "format": "date-time"}
        raw = j.dumps(data)
        s = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        loaded = j.loads(s)
        assert loaded == data

    def test_json_ser_same_as_xwsystem_flyweight(self):
        """Schema registry _json_ser() is the same flyweight as get_serializer(JsonSerializer)."""
        from exonware.xwschema.registry.schema_registry import _json_ser
        j_registry = _json_ser()
        j_xwsystem = get_serializer(JsonSerializer)
        # Same instance (flyweight)
        assert j_registry is j_xwsystem

    def test_schema_info_dataclass(self):
        """SchemaInfo can be constructed (production use)."""
        from exonware.xwschema.registry.schema_registry import SchemaInfo
        info = SchemaInfo(id=1, version=2, subject="users", schema='{"type":"string"}')
        assert info.id == 1
        assert info.version == 2
        assert info.subject == "users"
        assert info.schema_type == "AVRO"
@pytest.mark.xwschema_unit
@pytest.mark.xwschema_registry


class TestConfluentSchemaRegistryCache:
    """ConfluentSchemaRegistry optional xwsystem cache (reuse, production)."""

    def test_init_without_cache(self):
        """cache_size=0 means no cache (default)."""
        from exonware.xwschema.registry.schema_registry import ConfluentSchemaRegistry
        r = ConfluentSchemaRegistry("http://localhost:8081", cache_size=0)
        assert r._cache is None

    def test_init_with_cache_uses_xwsystem(self):
        """cache_size > 0 uses xwsystem create_cache (get/put contract)."""
        from exonware.xwschema.registry.schema_registry import ConfluentSchemaRegistry
        r = ConfluentSchemaRegistry("http://localhost:8081", cache_size=100)
        assert r._cache is not None
        # xwsystem cache contract: get(key, default), put(key, value)
        r._cache.put("subject:test", None)
        assert r._cache.get("subject:test") is None
        r._cache.put("id:1", "placeholder")
        assert r._cache.get("id:1") == "placeholder"
