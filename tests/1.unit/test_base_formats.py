#!/usr/bin/env python3
"""
Unit tests for ASchemaSerialization base class features.

Tests common functionality across all format serializers:
- Reference detection
- Schema merging
- Schema flattening
- Schema comparison
- Metadata extraction
- Type mapping
- Property mapping

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.1
Generation Date: 09-Nov-2025
"""

import pytest
from exonware.xwschema.formats.schema.json_schema import JsonSchemaSerializer
from exonware.xwschema.formats.schema.avro_schema import AvroSchemaSerializer
from exonware.xwschema.formats.base import (
    SchemaPrimitiveType,
    SchemaComplexType,
    SchemaTypeMapper,
    SchemaPropertyMapper
)


@pytest.mark.xwschema_unit
class TestSchemaPrimitiveType:
    """Test SchemaPrimitiveType."""
    
    def test_all_primitives(self):
        """Test all_primitives() returns set of primitives."""
        primitives = SchemaPrimitiveType.all_primitives()
        assert isinstance(primitives, set)
        assert SchemaPrimitiveType.STRING in primitives
        assert SchemaPrimitiveType.INTEGER in primitives
        assert SchemaPrimitiveType.NUMBER in primitives
        assert SchemaPrimitiveType.BOOLEAN in primitives
    
    def test_primitive_constants(self):
        """Test primitive type constants."""
        assert SchemaPrimitiveType.NULL == 'null'
        assert SchemaPrimitiveType.BOOLEAN == 'boolean'
        assert SchemaPrimitiveType.INTEGER == 'integer'
        assert SchemaPrimitiveType.NUMBER == 'number'
        assert SchemaPrimitiveType.STRING == 'string'


@pytest.mark.xwschema_unit
class TestSchemaComplexType:
    """Test SchemaComplexType."""
    
    def test_all_complex(self):
        """Test all_complex() returns set of complex types."""
        complex_types = SchemaComplexType.all_complex()
        assert isinstance(complex_types, set)
        assert SchemaComplexType.OBJECT in complex_types
        assert SchemaComplexType.ARRAY in complex_types
        assert SchemaComplexType.ENUM in complex_types
    
    def test_complex_constants(self):
        """Test complex type constants."""
        assert SchemaComplexType.OBJECT == 'object'
        assert SchemaComplexType.ARRAY == 'array'
        assert SchemaComplexType.ENUM == 'enum'


@pytest.mark.xwschema_unit
class TestSchemaTypeMapper:
    """Test SchemaTypeMapper."""
    
    def test_map_type_json_to_avro(self):
        """Test mapping type from JSON Schema to Avro."""
        mapped = SchemaTypeMapper.map_type('integer', 'json_schema', 'avro')
        assert mapped == 'int'
    
    def test_map_type_avro_to_json(self):
        """Test mapping type from Avro to JSON Schema."""
        mapped = SchemaTypeMapper.map_type('int', 'avro', 'json_schema')
        assert mapped == 'integer'
    
    def test_map_type_unknown(self):
        """Test mapping unknown type returns as-is."""
        mapped = SchemaTypeMapper.map_type('unknown_type', 'json_schema', 'avro')
        assert mapped == 'unknown_type'
    
    def test_reverse_map_type(self):
        """Test reverse type mapping."""
        mapped = SchemaTypeMapper.reverse_map_type('integer', 'json_schema', 'avro')
        # Should map back to 'int'
        assert mapped in ['int', 'integer']


@pytest.mark.xwschema_unit
class TestSchemaPropertyMapper:
    """Test SchemaPropertyMapper."""
    
    def test_map_property_json_to_avro(self):
        """Test mapping property from JSON Schema to Avro."""
        mapped = SchemaPropertyMapper.map_property('properties', 'json_schema', 'avro')
        assert mapped == 'fields'
    
    def test_map_property_avro_to_json(self):
        """Test mapping property from Avro to JSON Schema."""
        mapped = SchemaPropertyMapper.map_property('fields', 'avro', 'json_schema')
        assert mapped == 'properties'
    
    def test_map_property_unknown(self):
        """Test mapping unknown property returns as-is."""
        mapped = SchemaPropertyMapper.map_property('unknown_prop', 'json_schema', 'avro')
        assert mapped == 'unknown_prop'
    
    def test_map_schema_json_to_avro(self):
        """Test mapping entire schema from JSON Schema to Avro."""
        json_schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'}
            },
            'description': 'Test schema'
        }
        mapped = SchemaPropertyMapper.map_schema(json_schema, 'json_schema', 'avro')
        assert mapped is not None
        # Properties should be mapped to fields
        assert 'fields' in mapped or 'properties' in mapped


@pytest.mark.xwschema_unit
class TestASchemaSerializationCommon:
    """Test common ASchemaSerialization methods."""
    
    @pytest.fixture
    def json_serializer(self):
        """Create JSON Schema serializer."""
        return JsonSchemaSerializer()
    
    @pytest.fixture
    def avro_serializer(self):
        """Create Avro Schema serializer."""
        return AvroSchemaSerializer()
    
    # ========================================================================
    # REFERENCE DETECTION TESTS
    # ========================================================================
    
    def test_detect_references_json_schema(self, json_serializer):
        """Test detecting references in JSON Schema."""
        schema = {
            'type': 'object',
            'properties': {
                'user': {'$ref': '#/definitions/User'}
            },
            'definitions': {
                'User': {'type': 'object'}
            }
        }
        refs = json_serializer.detect_references(schema)
        assert len(refs) > 0
        assert any(ref['type'] == '$ref' for ref in refs)
    
    def test_detect_references_no_refs(self, json_serializer):
        """Test detecting references when none exist."""
        schema = {'type': 'string'}
        refs = json_serializer.detect_references(schema)
        assert len(refs) == 0
    
    # ========================================================================
    # SCHEMA MERGING TESTS
    # ========================================================================
    
    def test_merge_schemas_allof(self, json_serializer):
        """Test merging schemas with allOf strategy."""
        schemas = [
            {'type': 'object', 'properties': {'name': {'type': 'string'}}},
            {'required': ['name']}
        ]
        merged = json_serializer.merge_schemas(schemas, strategy='allOf')
        assert 'allOf' in merged
        assert len(merged['allOf']) == 2
    
    def test_merge_schemas_deep(self, json_serializer):
        """Test merging schemas with deep strategy."""
        schemas = [
            {'type': 'object', 'properties': {'name': {'type': 'string'}}},
            {'properties': {'age': {'type': 'integer'}}}
        ]
        merged = json_serializer.merge_schemas(schemas, strategy='deep')
        assert 'properties' in merged
        assert 'name' in merged['properties']
        assert 'age' in merged['properties']
    
    def test_merge_schemas_shallow(self, json_serializer):
        """Test merging schemas with shallow strategy."""
        schemas = [
            {'type': 'object', 'properties': {'name': {'type': 'string'}}},
            {'type': 'object', 'properties': {'age': {'type': 'integer'}}}
        ]
        merged = json_serializer.merge_schemas(schemas, strategy='shallow')
        # Last schema wins
        assert 'age' in merged.get('properties', {})
    
    # ========================================================================
    # SCHEMA FLATTENING TESTS
    # ========================================================================
    
    def test_flatten_schema_with_refs(self, json_serializer):
        """Test flattening schema with references."""
        schema = {
            'type': 'object',
            'properties': {
                'user': {'$ref': '#/definitions/User'}
            },
            'definitions': {
                'User': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'}
                    }
                }
            }
        }
        flattened = json_serializer.flatten_schema(schema)
        assert flattened is not None
        # References should be inlined
        assert 'definitions' not in flattened or len(flattened.get('definitions', {})) == 0
    
    def test_flatten_schema_no_refs(self, json_serializer):
        """Test flattening schema without references."""
        schema = {'type': 'string'}
        flattened = json_serializer.flatten_schema(schema)
        assert flattened == schema
    
    # ========================================================================
    # SCHEMA GENERATION TESTS
    # ========================================================================
    
    def test_generate_from_data_string(self, json_serializer):
        """Test generating schema from string data."""
        schema = json_serializer.generate_from_data('test')
        assert schema is not None
        assert schema.get('type') == 'string'
    
    def test_generate_from_data_object(self, json_serializer):
        """Test generating schema from object data."""
        data = {'name': 'Alice', 'age': 30}
        schema = json_serializer.generate_from_data(data)
        assert schema is not None
        assert schema.get('type') == 'object'
        assert 'properties' in schema
    
    def test_generate_from_data_array(self, json_serializer):
        """Test generating schema from array data."""
        schema = json_serializer.generate_from_data(['a', 'b', 'c'])
        assert schema is not None
        assert schema.get('type') == 'array'
        assert 'items' in schema
    
    # ========================================================================
    # SCHEMA COMPARISON TESTS
    # ========================================================================
    
    def test_compare_schemas_identical(self, json_serializer):
        """Test comparing identical schemas."""
        schema1 = {'type': 'string'}
        schema2 = {'type': 'string'}
        comparison = json_serializer.compare_schemas(schema1, schema2)
        assert comparison['identical'] is True
    
    def test_compare_schemas_different(self, json_serializer):
        """Test comparing different schemas."""
        schema1 = {'type': 'string'}
        schema2 = {'type': 'integer'}
        comparison = json_serializer.compare_schemas(schema1, schema2)
        assert comparison['identical'] is False
        assert len(comparison['modified']) > 0
    
    def test_compare_schemas_with_added_properties(self, json_serializer):
        """Test comparing schemas with added properties."""
        schema1 = {'type': 'string'}
        schema2 = {'type': 'string', 'title': 'Test'}
        comparison = json_serializer.compare_schemas(schema1, schema2)
        assert comparison['identical'] is False
        assert len(comparison['added']) > 0
    
    def test_is_compatible_same_type(self, json_serializer):
        """Test compatibility check for same types."""
        schema1 = {'type': 'string'}
        schema2 = {'type': 'string'}
        assert json_serializer.is_compatible(schema1, schema2) is True
    
    def test_is_compatible_different_type(self, json_serializer):
        """Test compatibility check for different types."""
        schema1 = {'type': 'string'}
        schema2 = {'type': 'integer'}
        assert json_serializer.is_compatible(schema1, schema2) is False
    
    # ========================================================================
    # METADATA EXTRACTION TESTS
    # ========================================================================
    
    def test_extract_metadata(self, json_serializer):
        """Test extracting metadata from schema."""
        schema = {
            'type': 'string',
            'title': 'Test',
            'description': 'A test schema',
            'default': 'default_value',
            'example': 'example_value'
        }
        metadata = json_serializer.extract_metadata(schema)
        assert 'title' in metadata
        assert 'description' in metadata
        assert 'default' in metadata
        assert 'example' in metadata
    
    def test_preserve_metadata(self, json_serializer):
        """Test preserving metadata during conversion."""
        source = {
            'type': 'string',
            'title': 'Source',
            'description': 'Source schema'
        }
        target = {'type': 'string'}
        preserved = json_serializer.preserve_metadata(source, target)
        assert preserved['title'] == 'Source'
        assert preserved['description'] == 'Source schema'
    
    def test_merge_metadata(self, json_serializer):
        """Test merging metadata from multiple schemas."""
        schemas = [
            {'type': 'string', 'title': 'Schema 1'},
            {'type': 'string', 'description': 'Schema 2'}
        ]
        merged = json_serializer.merge_metadata(schemas)
        assert 'title' in merged
        assert 'description' in merged
    
    # ========================================================================
    # TYPE MAPPING TESTS
    # ========================================================================
    
    def test_map_type_to(self, json_serializer):
        """Test map_type_to method."""
        mapped = json_serializer.map_type_to('integer', 'avro')
        assert mapped == 'int'
    
    def test_map_type_from(self, json_serializer):
        """Test map_type_from method."""
        mapped = json_serializer.map_type_from('integer', 'avro')
        assert mapped in ['int', 'integer']
    
    def test_is_primitive_type(self, json_serializer):
        """Test is_primitive_type method."""
        assert json_serializer.is_primitive_type('string') is True
        assert json_serializer.is_primitive_type('integer') is True
        assert json_serializer.is_primitive_type('object') is False
    
    def test_is_complex_type(self, json_serializer):
        """Test is_complex_type method."""
        assert json_serializer.is_complex_type('object') is True
        assert json_serializer.is_complex_type('array') is True
        assert json_serializer.is_complex_type('string') is False
    
    # ========================================================================
    # PROPERTY EXTRACTION TESTS
    # ========================================================================
    
    def test_extract_definitions(self, json_serializer):
        """Test extracting definitions from schema."""
        schema = {
            'type': 'object',
            'definitions': {
                'User': {'type': 'object'},
                'Product': {'type': 'object'}
            }
        }
        definitions = json_serializer.extract_definitions(schema)
        assert 'User' in definitions
        assert 'Product' in definitions
    
    def test_extract_properties(self, json_serializer):
        """Test extracting properties from schema."""
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            }
        }
        properties = json_serializer.extract_properties(schema)
        assert 'name' in properties
        assert 'age' in properties
    
    def test_extract_types(self, json_serializer):
        """Test extracting types from schema."""
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'},
                'tags': {
                    'type': 'array',
                    'items': {'type': 'string'}
                }
            }
        }
        types = json_serializer.extract_types(schema)
        assert 'string' in types
        assert 'integer' in types
        assert 'array' in types
        assert 'object' in types
    
    # ========================================================================
    # SCHEMA VALIDATION TESTS
    # ========================================================================
    
    def test_validate_schema_structure(self, json_serializer):
        """Test validating schema structure."""
        schema = {'type': 'string'}
        # Should not raise
        json_serializer.validate_schema_structure(schema)
    
    def test_validate_schema_structure_invalid(self, json_serializer):
        """Test validating invalid schema structure raises error."""
        schema = 123  # Not a dict or string
        with pytest.raises(Exception):
            json_serializer.validate_schema_structure(schema)
    
    def test_validate_schema(self, json_serializer):
        """Test validate_schema method."""
        schema = {'type': 'string'}
        is_valid, errors = json_serializer.validate_schema(schema)
        assert is_valid
        assert len(errors) == 0

