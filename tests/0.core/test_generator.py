#!/usr/bin/env python3
"""
Core tests for XWSchemaGenerator.

Tests schema generation functionality including:
- Generation from data
- Different generation modes
- Type inference
- Constraint inference
- Nested structure handling

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.1
Generation Date: 09-Nov-2025
"""

import pytest
from exonware.xwschema.generator import XWSchemaGenerator
from exonware.xwschema.defs import SchemaGenerationMode
from exonware.xwschema.config import GenerationConfig


@pytest.mark.xwschema_core
class TestXWSchemaGenerator:
    """Test XWSchemaGenerator - schema generation implementation."""
    
    @pytest.fixture
    def generator(self):
        """Create generator instance."""
        return XWSchemaGenerator()
    
    @pytest.fixture
    def generator_minimal(self):
        """Create generator with minimal mode."""
        config = GenerationConfig(mode=SchemaGenerationMode.MINIMAL)
        return XWSchemaGenerator(config)
    
    @pytest.fixture
    def generator_comprehensive(self):
        """Create generator with comprehensive mode."""
        config = GenerationConfig(mode=SchemaGenerationMode.COMPREHENSIVE)
        return XWSchemaGenerator(config)
    
    # ========================================================================
    # PRIMITIVE TYPE GENERATION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_generate_from_string(self, generator):
        """Test generation from string data."""
        schema = await generator.generate_from_data('test')
        assert schema is not None
        assert schema.get('type') == 'string'
    
    @pytest.mark.asyncio
    async def test_generate_from_integer(self, generator):
        """Test generation from integer data."""
        schema = await generator.generate_from_data(42)
        assert schema is not None
        assert schema.get('type') == 'integer'
    
    @pytest.mark.asyncio
    async def test_generate_from_float(self, generator):
        """Test generation from float data."""
        schema = await generator.generate_from_data(3.14)
        assert schema is not None
        assert schema.get('type') == 'number'
    
    @pytest.mark.asyncio
    async def test_generate_from_boolean(self, generator):
        """Test generation from boolean data."""
        schema = await generator.generate_from_data(True)
        assert schema is not None
        assert schema.get('type') == 'boolean'
    
    @pytest.mark.asyncio
    async def test_generate_from_none(self, generator):
        """Test generation from None data."""
        schema = await generator.generate_from_data(None)
        assert schema is not None
        assert schema.get('type') == 'null'
    
    # ========================================================================
    # ARRAY GENERATION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_generate_from_array_strings(self, generator):
        """Test generation from array of strings."""
        schema = await generator.generate_from_data(['a', 'b', 'c'])
        assert schema is not None
        assert schema.get('type') == 'array'
        assert 'items' in schema
        assert schema['items'].get('type') == 'string'
    
    @pytest.mark.asyncio
    async def test_generate_from_array_integers(self, generator):
        """Test generation from array of integers."""
        schema = await generator.generate_from_data([1, 2, 3])
        assert schema is not None
        assert schema.get('type') == 'array'
        assert schema['items'].get('type') == 'integer'
    
    @pytest.mark.asyncio
    async def test_generate_from_empty_array(self, generator):
        """Test generation from empty array."""
        schema = await generator.generate_from_data([])
        assert schema is not None
        assert schema.get('type') == 'array'
    
    @pytest.mark.asyncio
    async def test_generate_from_mixed_array(self, generator):
        """Test generation from array with mixed types."""
        schema = await generator.generate_from_data([1, 'a', True])
        assert schema is not None
        assert schema.get('type') == 'array'
        # Should handle mixed types (may use oneOf or anyOf)
    
    # ========================================================================
    # OBJECT GENERATION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_generate_from_simple_object(self, generator):
        """Test generation from simple object."""
        data = {'name': 'Alice', 'age': 30}
        schema = await generator.generate_from_data(data)
        assert schema is not None
        assert schema.get('type') == 'object'
        assert 'properties' in schema
        assert 'name' in schema['properties']
        assert 'age' in schema['properties']
    
    @pytest.mark.asyncio
    async def test_generate_from_empty_object(self, generator):
        """Test generation from empty object."""
        schema = await generator.generate_from_data({})
        assert schema is not None
        assert schema.get('type') == 'object'
    
    @pytest.mark.asyncio
    async def test_generate_from_nested_object(self, generator):
        """Test generation from nested object."""
        data = {
            'user': {
                'name': 'Alice',
                'age': 30
            }
        }
        schema = await generator.generate_from_data(data)
        assert schema is not None
        assert schema.get('type') == 'object'
        assert 'user' in schema['properties']
        assert schema['properties']['user'].get('type') == 'object'
    
    @pytest.mark.asyncio
    async def test_generate_from_object_with_array(self, generator):
        """Test generation from object with array property."""
        data = {
            'name': 'Alice',
            'tags': ['a', 'b', 'c']
        }
        schema = await generator.generate_from_data(data)
        assert schema is not None
        assert 'tags' in schema['properties']
        assert schema['properties']['tags'].get('type') == 'array'
    
    # ========================================================================
    # GENERATION MODE TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_generate_minimal_mode(self, generator_minimal):
        """Test generation in minimal mode."""
        data = {'name': 'Alice', 'age': 30}
        schema = await generator_minimal.generate_from_data(data)
        assert schema is not None
        assert schema.get('type') == 'object'
        # Minimal mode should have basic structure only
    
    @pytest.mark.asyncio
    async def test_generate_comprehensive_mode(self, generator_comprehensive):
        """Test generation in comprehensive mode."""
        data = {'name': 'Alice', 'age': 30}
        schema = await generator_comprehensive.generate_from_data(data)
        assert schema is not None
        assert schema.get('type') == 'object'
        # Comprehensive mode should have more details
    
    @pytest.mark.asyncio
    async def test_generate_infer_mode(self, generator):
        """Test generation in infer mode."""
        data = {'name': 'Alice', 'age': 30}
        schema = await generator.generate_from_data(data, mode=SchemaGenerationMode.INFER)
        assert schema is not None
    
    @pytest.mark.asyncio
    async def test_generate_strict_mode(self, generator):
        """Test generation in strict mode."""
        data = {'name': 'Alice', 'age': 30}
        schema = await generator.generate_from_data(data, mode=SchemaGenerationMode.STRICT)
        assert schema is not None
    
    # ========================================================================
    # CONSTRAINT INFERENCE TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_generate_with_length_constraints(self, generator):
        """Test generation infers length constraints from data."""
        data = ['a', 'b', 'c']
        schema = await generator.generate_from_data(data)
        assert schema is not None
        # May infer minItems/maxItems from array length
    
    @pytest.mark.asyncio
    async def test_generate_with_numeric_constraints(self, generator):
        """Test generation infers numeric constraints from data."""
        data = [1, 2, 3, 4, 5]
        schema = await generator.generate_from_data(data)
        assert schema is not None
        # May infer min/max from numeric values
    
    # ========================================================================
    # COMPLEX STRUCTURE TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_generate_deeply_nested(self, generator):
        """Test generation from deeply nested structure."""
        data = {
            'level1': {
                'level2': {
                    'level3': {
                        'value': 'test'
                    }
                }
            }
        }
        schema = await generator.generate_from_data(data)
        assert schema is not None
        assert schema.get('type') == 'object'
    
    @pytest.mark.asyncio
    async def test_generate_with_multiple_samples(self, generator):
        """Test generation from multiple data samples."""
        # Generator should handle multiple samples for better inference
        data1 = {'name': 'Alice', 'age': 30}
        schema1 = await generator.generate_from_data(data1)
        
        data2 = {'name': 'Bob', 'age': 25}
        schema2 = await generator.generate_from_data(data2)
        
        assert schema1 is not None
        assert schema2 is not None
    
    # ========================================================================
    # EDGE CASES
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_generate_from_zero_length_string(self, generator):
        """Test generation from zero-length string."""
        schema = await generator.generate_from_data('')
        assert schema is not None
        assert schema.get('type') == 'string'
    
    @pytest.mark.asyncio
    async def test_generate_from_zero(self, generator):
        """Test generation from zero."""
        schema = await generator.generate_from_data(0)
        assert schema is not None
        assert schema.get('type') == 'integer'
    
    @pytest.mark.asyncio
    async def test_generate_from_false(self, generator):
        """Test generation from False."""
        schema = await generator.generate_from_data(False)
        assert schema is not None
        assert schema.get('type') == 'boolean'

