#!/usr/bin/env python3
"""
#exonware/xwschema/tests/1.unit/engine_tests/test_format_conversion.py
Unit tests for XWSchemaEngine format conversion functionality.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

import pytest
from exonware.xwschema.engine import XWSchemaEngine
from exonware.xwschema.defs import SchemaFormat
@pytest.mark.xwschema_unit


class TestFormatConversion:
    """Test format conversion functionality."""
    @pytest.mark.asyncio

    async def test_convert_same_format_returns_unchanged(self):
        """Test that converting to same format returns schema unchanged."""
        engine = XWSchemaEngine()
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        result = await engine.convert_schema(schema, SchemaFormat.JSON_SCHEMA, SchemaFormat.JSON_SCHEMA)
        assert result == schema
    @pytest.mark.asyncio

    async def test_convert_json_schema_to_openapi(self):
        """Test converting JSON Schema to OpenAPI format."""
        engine = XWSchemaEngine()
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        result = await engine.convert_schema(schema, SchemaFormat.JSON_SCHEMA, SchemaFormat.OPENAPI)
        assert "openapi" in result
        assert "components" in result
        assert "schemas" in result["components"]
        assert "Schema" in result["components"]["schemas"]
    @pytest.mark.asyncio

    async def test_convert_json_schema_to_swagger(self):
        """Test converting JSON Schema to Swagger format."""
        engine = XWSchemaEngine()
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        result = await engine.convert_schema(schema, SchemaFormat.JSON_SCHEMA, SchemaFormat.SWAGGER)
        assert "swagger" in result
        assert "definitions" in result
        assert "Schema" in result["definitions"]
    @pytest.mark.asyncio

    async def test_convert_json_schema_to_graphql(self):
        """Test converting JSON Schema to GraphQL format."""
        engine = XWSchemaEngine()
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}}
        result = await engine.convert_schema(schema, SchemaFormat.JSON_SCHEMA, SchemaFormat.GRAPHQL)
        assert "type" in result
        assert result["type"] == "graphql"
        assert "types" in result
    @pytest.mark.asyncio

    async def test_convert_json_schema_to_protobuf(self):
        """Test converting JSON Schema to Protobuf format."""
        engine = XWSchemaEngine()
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}}
        result = await engine.convert_schema(schema, SchemaFormat.JSON_SCHEMA, SchemaFormat.PROTOBUF)
        assert "type" in result
        assert result["type"] == "protobuf"
        assert "messages" in result
        assert "syntax" in result
    @pytest.mark.asyncio

    async def test_convert_json_schema_to_avro(self):
        """Test converting JSON Schema to Avro format."""
        engine = XWSchemaEngine()
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}}
        result = await engine.convert_schema(schema, SchemaFormat.JSON_SCHEMA, SchemaFormat.AVRO)
        assert "type" in result
        assert result["type"] == "record"
        assert "fields" in result
    @pytest.mark.asyncio

    async def test_convert_openapi_to_json_schema(self):
        """Test converting OpenAPI to JSON Schema."""
        engine = XWSchemaEngine()
        openapi_schema = {
            "openapi": "3.0.0",
            "components": {
                "schemas": {
                    "User": {"type": "object", "properties": {"name": {"type": "string"}}}
                }
            }
        }
        result = await engine.convert_schema(openapi_schema, SchemaFormat.OPENAPI, SchemaFormat.JSON_SCHEMA)
        # Should extract the schema from OpenAPI structure
        assert "type" in result or "properties" in result
    @pytest.mark.asyncio

    async def test_convert_preserves_schema_structure(self):
        """Test that conversion preserves basic schema structure."""
        engine = XWSchemaEngine()
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
        result = await engine.convert_schema(schema, SchemaFormat.JSON_SCHEMA, SchemaFormat.GRAPHQL)
        # Should have converted to GraphQL format
        assert "type" in result
        assert result["type"] == "graphql"
@pytest.mark.xwschema_unit


class TestFormatConversionEdgeCases:
    """Test format conversion edge cases."""
    @pytest.mark.asyncio

    async def test_convert_empty_schema(self):
        """Test converting empty schema."""
        engine = XWSchemaEngine()
        schema = {}
        result = await engine.convert_schema(schema, SchemaFormat.JSON_SCHEMA, SchemaFormat.OPENAPI)
        assert isinstance(result, dict)
    @pytest.mark.asyncio

    async def test_convert_complex_nested_schema(self):
        """Test converting complex nested schema."""
        engine = XWSchemaEngine()
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "profile": {
                            "type": "object",
                            "properties": {"email": {"type": "string"}}
                        }
                    }
                }
            }
        }
        result = await engine.convert_schema(schema, SchemaFormat.JSON_SCHEMA, SchemaFormat.GRAPHQL)
        assert isinstance(result, dict)
        assert "type" in result
@pytest.mark.xwschema_unit


class TestSchemaFormatConverterCache:
    """SchemaFormatConverter uses xwsystem create_cache when cache_size > 0 (reuse, production)."""

    def test_converter_with_cache_size_uses_xwsystem_cache(self):
        """cache_size > 0 uses xwsystem create_cache."""
        from exonware.xwschema.operations.format_conversion import SchemaFormatConverter
        c = SchemaFormatConverter(enable_caching=True, cache_size=100)
        assert c._cache is not None
        c._cache.put("k1", "v1")
        assert c._cache.get("k1") == "v1"

    def test_converter_without_cache_or_zero_size(self):
        """cache_size=0 or enable_caching=False: no xwsystem cache."""
        from exonware.xwschema.operations.format_conversion import SchemaFormatConverter
        c0 = SchemaFormatConverter(enable_caching=True, cache_size=0)
        assert c0._cache is None
        c1 = SchemaFormatConverter(enable_caching=False, cache_size=100)
        assert c1._cache is None
    @pytest.mark.asyncio

    async def test_converter_cache_hit_returns_same_result(self):
        """Second convert with same input returns cached result (xwsystem cache when cache_size > 0)."""
        from exonware.xwschema.operations.format_conversion import SchemaFormatConverter
        conv = SchemaFormatConverter(enable_caching=True, cache_size=100)
        schema = {"type": "object", "properties": {"x": {"type": "string"}}}
        r1 = await conv.convert(schema, SchemaFormat.JSON_SCHEMA, SchemaFormat.OPENAPI)
        r2 = await conv.convert(schema, SchemaFormat.JSON_SCHEMA, SchemaFormat.OPENAPI)
        assert r1 == r2
        assert "openapi" in r1
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
