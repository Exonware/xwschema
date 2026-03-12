#!/usr/bin/env python3
"""
#exonware/xwschema/tests/3.advance/test_performance.py
Performance benchmarks for xwschema.
Priority #4: Performance Excellence
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Jan-2025
"""

import pytest
import time
import asyncio
from exonware.xwschema import XWSchema
@pytest.mark.xwschema_advance
@pytest.mark.xwschema_performance

class TestSchemaValidationPerformance:
    """Performance tests for schema validation."""
    @pytest.mark.asyncio

    async def test_validation_performance(self):
        """Test schema validation performance."""
        schema_dict = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }
        schema = XWSchema(schema_dict)
        data = {"name": "Alice", "age": 30}
        # Test validation performance
        start = time.time()
        for _ in range(1000):
            is_valid, errors = await schema.validate(data)
        elapsed = time.time() - start
        # 1000 validations should complete in < 1 second
        assert elapsed < 1.0, f"Validation too slow: {elapsed:.3f}s for 1000 validations"
        assert is_valid is True
@pytest.mark.xwschema_advance
@pytest.mark.xwschema_performance

class TestSchemaGenerationPerformance:
    """Performance tests for schema generation."""

    def test_from_data_performance(self):
        """Test schema generation from data performance."""
        data = {
            "name": "Alice",
            "age": 30,
            "items": [{"id": 1, "value": "test"}]
        }
        # Test generation performance (from_data is async)
        import asyncio
        async def run():
            start = time.time()
            for _ in range(100):
                schema = await XWSchema.from_data(data)
            return time.time() - start
        elapsed = asyncio.run(run())
        assert elapsed < 1.0, f"Schema generation too slow: {elapsed:.3f}s for 100 generations"
    @pytest.mark.skip(reason="from_class not in current API; use from_data for schema generation")

    def test_from_class_performance(self):
        """Test schema generation from class performance (skipped: from_class not in API)."""
        pass
@pytest.mark.xwschema_advance
@pytest.mark.xwschema_performance

class TestFormatConversionPerformance:
    """Performance tests for format conversion."""
    @pytest.mark.asyncio

    async def test_json_to_openapi_conversion(self):
        """Test JSON to OpenAPI conversion performance via engine.convert_schema."""
        from exonware.xwschema.defs import SchemaFormat
        from exonware.xwschema.engine import XWSchemaEngine
        schema_dict = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }
        engine = XWSchemaEngine()
        start = time.time()
        for _ in range(100):
            openapi_spec = await engine.convert_schema(
                schema_dict, SchemaFormat.JSON_SCHEMA, SchemaFormat.OPENAPI
            )
        elapsed = time.time() - start
        assert elapsed < 2.0, f"Format conversion too slow: {elapsed:.3f}s for 100 conversions"
