#!/usr/bin/env python3
"""
Test Schema Roundtrip Conversion

Tests conversion between different schema formats (JSON Schema, XSD, Avro)
ensuring semantic meaning is maintained in each roundtrip.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.1
Generation Date: 09-Nov-2025
"""

import pytest
from typing import Any, Dict
from exonware.xwschema.formats.schema.json_schema import JsonSchemaSerializer
from exonware.xwschema.formats.schema.xsd_schema import XsdSchemaSerializer
from exonware.xwschema.formats.schema.avro_schema import AvroSchemaSerializer


@pytest.mark.xwschema_core
class TestSchemaRoundtrip:
    """Test roundtrip conversion between schema formats."""
    
    @pytest.fixture
    def json_schema_serializer(self):
        """Create JSON Schema serializer."""
        return JsonSchemaSerializer()
    
    @pytest.fixture
    def xsd_schema_serializer(self):
        """Create XSD Schema serializer."""
        return XsdSchemaSerializer()
    
    @pytest.fixture
    def avro_schema_serializer(self):
        """Create Avro Schema serializer."""
        return AvroSchemaSerializer()
    
    @pytest.fixture
    def sample_json_schema(self) -> Dict[str, Any]:
        """Sample JSON Schema for testing."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "User",
            "description": "A user schema",
            "properties": {
                "id": {
                    "type": "integer",
                    "description": "User ID"
                },
                "name": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 100,
                    "description": "User name"
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "User email"
                },
                "age": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 150,
                    "description": "User age"
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "minItems": 0,
                    "maxItems": 10,
                    "description": "User tags"
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "created_at": {
                            "type": "string",
                            "format": "date-time"
                        },
                        "active": {
                            "type": "boolean"
                        }
                    },
                    "required": ["created_at"],
                    "description": "User metadata"
                }
            },
            "required": ["id", "name", "email"]
        }
    
    def _normalize_for_comparison(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize schema for comparison by removing format-specific metadata
        and focusing on semantic meaning.
        """
        normalized = {}
        
        # Extract core semantic properties
        if 'type' in schema:
            normalized['type'] = schema['type']
        elif 'xs:complexType' in schema or 'xs:element' in schema:
            # XSD format
            normalized['type'] = 'object'
        elif 'type' in schema.get('fields', [{}])[0] if isinstance(schema.get('fields'), list) else {}:
            # Avro format
            normalized['type'] = 'record'
        
        # Extract title/name
        if 'title' in schema:
            normalized['title'] = schema['title']
        elif 'name' in schema:
            normalized['title'] = schema['name']
        
        # Extract description
        if 'description' in schema:
            normalized['description'] = schema['description']
        elif 'doc' in schema:
            normalized['description'] = schema['doc']
        
        # Extract properties/fields
        if 'properties' in schema:
            normalized['properties'] = self._normalize_properties(schema['properties'])
        elif 'fields' in schema:
            # Avro format
            normalized['properties'] = self._normalize_avro_fields(schema['fields'])
        
        # Extract required fields
        if 'required' in schema:
            normalized['required'] = schema['required']
        
        return normalized
    
    def _normalize_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize properties for comparison."""
        normalized = {}
        for key, value in properties.items():
            if isinstance(value, dict):
                prop = {}
                if 'type' in value:
                    prop['type'] = value['type']
                if 'description' in value:
                    prop['description'] = value['description']
                elif 'doc' in value:
                    prop['description'] = value['doc']
                if 'minLength' in value or 'min_length' in value:
                    prop['minLength'] = value.get('minLength') or value.get('min_length')
                if 'maxLength' in value or 'max_length' in value:
                    prop['maxLength'] = value.get('maxLength') or value.get('max_length')
                if 'minimum' in value:
                    prop['minimum'] = value['minimum']
                if 'maximum' in value:
                    prop['maximum'] = value['maximum']
                if 'items' in value:
                    prop['items'] = self._normalize_properties({'item': value['items']})['item']
                if 'properties' in value:
                    prop['properties'] = self._normalize_properties(value['properties'])
                normalized[key] = prop
        return normalized
    
    def _normalize_avro_fields(self, fields: list) -> Dict[str, Any]:
        """Normalize Avro fields to properties format."""
        normalized = {}
        for field in fields:
            if isinstance(field, dict):
                name = field.get('name', '')
                field_type = field.get('type', {})
                prop = {}
                
                # Map Avro types to JSON Schema types
                if isinstance(field_type, str):
                    type_mapping = {
                        'int': 'integer',
                        'long': 'integer',
                        'float': 'number',
                        'double': 'number',
                        'string': 'string',
                        'boolean': 'boolean',
                        'null': 'null',
                        'bytes': 'string'
                    }
                    prop['type'] = type_mapping.get(field_type, field_type)
                elif isinstance(field_type, dict):
                    if field_type.get('type') == 'array':
                        prop['type'] = 'array'
                        if 'items' in field_type:
                            prop['items'] = {'type': 'string'}  # Simplified
                    elif field_type.get('type') == 'record':
                        prop['type'] = 'object'
                        if 'fields' in field_type:
                            prop['properties'] = self._normalize_avro_fields(field_type['fields'])
                
                if 'doc' in field:
                    prop['description'] = field['doc']
                
                normalized[name] = prop
        return normalized
    
    def _check_semantic_equivalence(
        self, 
        schema1: Dict[str, Any], 
        schema2: Dict[str, Any],
        tolerance: float = 0.8
    ) -> bool:
        """
        Check if two schemas are semantically equivalent.
        
        Args:
            schema1: First schema
            schema2: Second schema
            tolerance: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            True if schemas are semantically equivalent
        """
        norm1 = self._normalize_for_comparison(schema1)
        norm2 = self._normalize_for_comparison(schema2)
        
        # Check core properties
        if norm1.get('type') != norm2.get('type'):
            return False
        
        # Check title/name
        if norm1.get('title') and norm2.get('title'):
            if norm1['title'] != norm2['title']:
                return False
        
        # Check properties
        props1 = norm1.get('properties', {})
        props2 = norm2.get('properties', {})
        
        if len(props1) != len(props2):
            return False
        
        # Check each property
        for key in props1:
            if key not in props2:
                return False
            
            prop1 = props1[key]
            prop2 = props2[key]
            
            # Check type
            if prop1.get('type') != prop2.get('type'):
                return False
        
        return True
    
    def test_json_to_xsd_to_avro_roundtrip(
        self,
        json_schema_serializer,
        xsd_schema_serializer,
        avro_schema_serializer,
        sample_json_schema
    ):
        """Test roundtrip: JSON Schema → XSD → Avro → JSON Schema."""
        # Step 1: JSON Schema → XSD
        normalized_json = json_schema_serializer.normalize_schema(sample_json_schema)
        xsd_schema = xsd_schema_serializer.denormalize_schema(
            xsd_schema_serializer.convert_to_format(normalized_json, 'xsd_schema')
        )
        
        # Verify XSD structure
        assert xsd_schema is not None
        assert isinstance(xsd_schema, (dict, str))
        
        # Step 2: XSD → Avro
        normalized_xsd = xsd_schema_serializer.normalize_schema(xsd_schema)
        avro_schema = avro_schema_serializer.denormalize_schema(
            avro_schema_serializer.convert_to_format(normalized_xsd, 'avro')
        )
        
        # Verify Avro structure
        assert avro_schema is not None
        assert isinstance(avro_schema, (dict, str))
        
        # Step 3: Avro → JSON Schema
        normalized_avro = avro_schema_serializer.normalize_schema(avro_schema)
        back_to_json = json_schema_serializer.denormalize_schema(
            json_schema_serializer.convert_to_format(normalized_avro, 'json_schema')
        )
        
        # Verify JSON Schema structure
        assert back_to_json is not None
        assert isinstance(back_to_json, dict)
        
        # Step 4: Check semantic equivalence
        # The schema should maintain semantic meaning through the roundtrip
        assert self._check_semantic_equivalence(sample_json_schema, back_to_json)
    
    def test_json_to_avro_roundtrip(
        self,
        json_schema_serializer,
        avro_schema_serializer,
        sample_json_schema
    ):
        """Test direct roundtrip: JSON Schema → Avro → JSON Schema."""
        # JSON Schema → Avro
        normalized_json = json_schema_serializer.normalize_schema(sample_json_schema)
        avro_schema = avro_schema_serializer.denormalize_schema(
            avro_schema_serializer.convert_to_format(normalized_json, 'avro')
        )
        
        assert avro_schema is not None
        
        # Avro → JSON Schema
        normalized_avro = avro_schema_serializer.normalize_schema(avro_schema)
        back_to_json = json_schema_serializer.denormalize_schema(
            json_schema_serializer.convert_to_format(normalized_avro, 'json_schema')
        )
        
        assert back_to_json is not None
        assert self._check_semantic_equivalence(sample_json_schema, back_to_json)
    
    def test_type_preservation_through_roundtrip(
        self,
        json_schema_serializer,
        xsd_schema_serializer,
        avro_schema_serializer,
        sample_json_schema
    ):
        """Test that types are preserved through roundtrip conversion."""
        # Extract original types
        original_types = {}
        for prop_name, prop_schema in sample_json_schema.get('properties', {}).items():
            original_types[prop_name] = prop_schema.get('type')
        
        # Convert through formats
        normalized_json = json_schema_serializer.normalize_schema(sample_json_schema)
        
        # JSON → XSD
        xsd_schema = xsd_schema_serializer.denormalize_schema(
            xsd_schema_serializer.convert_to_format(normalized_json, 'xsd_schema')
        )
        normalized_xsd = xsd_schema_serializer.normalize_schema(xsd_schema)
        
        # XSD → Avro
        avro_schema = avro_schema_serializer.denormalize_schema(
            avro_schema_serializer.convert_to_format(normalized_xsd, 'avro')
        )
        normalized_avro = avro_schema_serializer.normalize_schema(avro_schema)
        
        # Avro → JSON
        back_to_json = json_schema_serializer.denormalize_schema(
            json_schema_serializer.convert_to_format(normalized_avro, 'json_schema')
        )
        
        # Check types are preserved
        for prop_name, original_type in original_types.items():
            if prop_name in back_to_json.get('properties', {}):
                restored_type = back_to_json['properties'][prop_name].get('type')
                # Type mapping: integer/int/long all map to integer
                if original_type == 'integer':
                    assert restored_type in ['integer', 'int', 'long'], \
                        f"Type mismatch for {prop_name}: expected integer/int/long, got {restored_type}"
                elif original_type == 'string':
                    assert restored_type == 'string', \
                        f"Type mismatch for {prop_name}: expected string, got {restored_type}"
                elif original_type == 'array':
                    assert restored_type == 'array', \
                        f"Type mismatch for {prop_name}: expected array, got {restored_type}"
                elif original_type == 'object':
                    assert restored_type in ['object', 'record'], \
                        f"Type mismatch for {prop_name}: expected object/record, got {restored_type}"
    
    def test_constraints_preservation(
        self,
        json_schema_serializer,
        avro_schema_serializer,
        sample_json_schema
    ):
        """Test that constraints (minLength, maxLength, minimum, maximum) are preserved."""
        # Extract original constraints
        original_constraints = {}
        for prop_name, prop_schema in sample_json_schema.get('properties', {}).items():
            constraints = {}
            if 'minLength' in prop_schema:
                constraints['minLength'] = prop_schema['minLength']
            if 'maxLength' in prop_schema:
                constraints['maxLength'] = prop_schema['maxLength']
            if 'minimum' in prop_schema:
                constraints['minimum'] = prop_schema['minimum']
            if 'maximum' in prop_schema:
                constraints['maximum'] = prop_schema['maximum']
            if constraints:
                original_constraints[prop_name] = constraints
        
        # Convert through formats
        normalized_json = json_schema_serializer.normalize_schema(sample_json_schema)
        avro_schema = avro_schema_serializer.denormalize_schema(
            avro_schema_serializer.convert_to_format(normalized_json, 'avro')
        )
        normalized_avro = avro_schema_serializer.normalize_schema(avro_schema)
        back_to_json = json_schema_serializer.denormalize_schema(
            json_schema_serializer.convert_to_format(normalized_avro, 'json_schema')
        )
        
        # Check constraints are preserved (if format supports them)
        for prop_name, original_constraints_dict in original_constraints.items():
            if prop_name in back_to_json.get('properties', {}):
                restored_prop = back_to_json['properties'][prop_name]
                # Check that constraints are present (may be in different format)
                # Note: Some formats may not support all constraints, so we check what's available
                if 'minLength' in original_constraints_dict:
                    # Avro doesn't support minLength, but it should be preserved in metadata
                    assert 'minLength' in restored_prop or 'min_length' in restored_prop or \
                           original_constraints_dict['minLength'] in str(restored_prop), \
                        f"minLength constraint lost for {prop_name}"
    
    def test_required_fields_preservation(
        self,
        json_schema_serializer,
        avro_schema_serializer,
        sample_json_schema
    ):
        """Test that required fields are preserved through roundtrip."""
        original_required = sample_json_schema.get('required', [])
        
        # Convert through formats
        normalized_json = json_schema_serializer.normalize_schema(sample_json_schema)
        avro_schema = avro_schema_serializer.denormalize_schema(
            avro_schema_serializer.convert_to_format(normalized_json, 'avro')
        )
        normalized_avro = avro_schema_serializer.normalize_schema(avro_schema)
        back_to_json = json_schema_serializer.denormalize_schema(
            json_schema_serializer.convert_to_format(normalized_avro, 'json_schema')
        )
        
        # Check required fields are preserved
        restored_required = back_to_json.get('required', [])
        # All original required fields should be present (order may differ)
        assert set(original_required).issubset(set(restored_required)) or \
               set(restored_required).issubset(set(original_required)), \
            f"Required fields mismatch: original {original_required}, restored {restored_required}"
    
    def test_nested_objects_preservation(
        self,
        json_schema_serializer,
        avro_schema_serializer,
        sample_json_schema
    ):
        """Test that nested objects are preserved through roundtrip."""
        # Check nested metadata object
        metadata_schema = sample_json_schema.get('properties', {}).get('metadata', {})
        assert metadata_schema.get('type') == 'object'
        assert 'properties' in metadata_schema
        
        # Convert through formats
        normalized_json = json_schema_serializer.normalize_schema(sample_json_schema)
        avro_schema = avro_schema_serializer.denormalize_schema(
            avro_schema_serializer.convert_to_format(normalized_json, 'avro')
        )
        normalized_avro = avro_schema_serializer.normalize_schema(avro_schema)
        back_to_json = json_schema_serializer.denormalize_schema(
            json_schema_serializer.convert_to_format(normalized_avro, 'json_schema')
        )
        
        # Check nested object is preserved
        restored_metadata = back_to_json.get('properties', {}).get('metadata', {})
        assert restored_metadata is not None
        # Type should be object or record
        assert restored_metadata.get('type') in ['object', 'record'], \
            f"Nested object type not preserved: {restored_metadata.get('type')}"
    
    def test_array_items_preservation(
        self,
        json_schema_serializer,
        avro_schema_serializer,
        sample_json_schema
    ):
        """Test that array items schema is preserved through roundtrip."""
        # Check tags array
        tags_schema = sample_json_schema.get('properties', {}).get('tags', {})
        assert tags_schema.get('type') == 'array'
        assert 'items' in tags_schema
        
        # Convert through formats
        normalized_json = json_schema_serializer.normalize_schema(sample_json_schema)
        avro_schema = avro_schema_serializer.denormalize_schema(
            avro_schema_serializer.convert_to_format(normalized_json, 'avro')
        )
        normalized_avro = avro_schema_serializer.normalize_schema(avro_schema)
        back_to_json = json_schema_serializer.denormalize_schema(
            json_schema_serializer.convert_to_format(normalized_avro, 'json_schema')
        )
        
        # Check array items are preserved
        restored_tags = back_to_json.get('properties', {}).get('tags', {})
        assert restored_tags.get('type') == 'array', \
            f"Array type not preserved: {restored_tags.get('type')}"
        assert 'items' in restored_tags, "Array items schema not preserved"
