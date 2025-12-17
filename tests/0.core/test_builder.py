#!/usr/bin/env python3
"""
Core tests for XWSchemaBuilder.

Tests the builder pattern for creating schemas with all properties.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.1
Generation Date: 09-Nov-2025
"""

import pytest
from exonware.xwschema.builder import XWSchemaBuilder


@pytest.mark.xwschema_core
class TestXWSchemaBuilder:
    """Test XWSchemaBuilder - schema builder implementation."""
    
    # ========================================================================
    # BASIC PROPERTY TESTS
    # ========================================================================
    
    def test_build_with_type_only(self):
        """Test building schema with type only."""
        schema = XWSchemaBuilder.build_schema_dict(type=str)
        assert schema is not None
        assert 'type' in schema
    
    def test_build_with_title(self):
        """Test building schema with title."""
        schema = XWSchemaBuilder.build_schema_dict(type=str, title='Test Schema')
        assert schema.get('title') == 'Test Schema'
    
    def test_build_with_description(self):
        """Test building schema with description."""
        schema = XWSchemaBuilder.build_schema_dict(type=str, description='A test schema')
        assert schema.get('description') == 'A test schema'
    
    def test_build_with_format(self):
        """Test building schema with format."""
        schema = XWSchemaBuilder.build_schema_dict(type=str, format='email')
        assert schema.get('format') == 'email'
    
    def test_build_with_enum(self):
        """Test building schema with enum."""
        schema = XWSchemaBuilder.build_schema_dict(type=str, enum=['red', 'green', 'blue'])
        assert 'enum' in schema
        assert schema['enum'] == ['red', 'green', 'blue']
    
    def test_build_with_default(self):
        """Test building schema with default value."""
        schema = XWSchemaBuilder.build_schema_dict(type=str, default='default_value')
        assert schema.get('default') == 'default_value'
    
    def test_build_with_nullable(self):
        """Test building schema with nullable."""
        schema = XWSchemaBuilder.build_schema_dict(type=str, nullable=True)
        assert schema.get('nullable') is True
    
    def test_build_with_deprecated(self):
        """Test building schema with deprecated."""
        schema = XWSchemaBuilder.build_schema_dict(type=str, deprecated=True)
        assert schema.get('deprecated') is True
    
    def test_build_with_confidential(self):
        """Test building schema with confidential."""
        schema = XWSchemaBuilder.build_schema_dict(type=str, confidential=True)
        # Confidential may be stored as 'x-confidential' or 'confidential'
        assert schema.get('confidential') is True or schema.get('x-confidential') is True
    
    # ========================================================================
    # STRING CONSTRAINT TESTS
    # ========================================================================
    
    def test_build_with_pattern(self):
        """Test building schema with pattern."""
        schema = XWSchemaBuilder.build_schema_dict(
            type=str,
            pattern=r'^[A-Za-z0-9]+$'
        )
        assert schema.get('pattern') == r'^[A-Za-z0-9]+$'
    
    def test_build_with_length_min(self):
        """Test building schema with length_min."""
        schema = XWSchemaBuilder.build_schema_dict(type=str, length_min=5)
        assert schema.get('minLength') == 5
    
    def test_build_with_length_max(self):
        """Test building schema with length_max."""
        schema = XWSchemaBuilder.build_schema_dict(type=str, length_max=10)
        assert schema.get('maxLength') == 10
    
    def test_build_with_strip_whitespace(self):
        """Test building schema with strip_whitespace."""
        schema = XWSchemaBuilder.build_schema_dict(type=str, strip_whitespace=True)
        assert schema.get('stripWhitespace') is True
    
    def test_build_with_to_upper(self):
        """Test building schema with to_upper."""
        schema = XWSchemaBuilder.build_schema_dict(type=str, to_upper=True)
        assert schema.get('toUpper') is True
    
    def test_build_with_to_lower(self):
        """Test building schema with to_lower."""
        schema = XWSchemaBuilder.build_schema_dict(type=str, to_lower=True)
        assert schema.get('toLower') is True
    
    # ========================================================================
    # NUMERIC CONSTRAINT TESTS
    # ========================================================================
    
    def test_build_with_value_min(self):
        """Test building schema with value_min."""
        schema = XWSchemaBuilder.build_schema_dict(type=int, value_min=0)
        assert schema.get('minimum') == 0
    
    def test_build_with_value_max(self):
        """Test building schema with value_max."""
        schema = XWSchemaBuilder.build_schema_dict(type=int, value_max=100)
        assert schema.get('maximum') == 100
    
    def test_build_with_value_min_exclusive(self):
        """Test building schema with value_min_exclusive."""
        schema = XWSchemaBuilder.build_schema_dict(type=int, value_min_exclusive=True)
        assert schema.get('exclusiveMinimum') is True
    
    def test_build_with_value_max_exclusive(self):
        """Test building schema with value_max_exclusive."""
        schema = XWSchemaBuilder.build_schema_dict(type=int, value_max_exclusive=True)
        assert schema.get('exclusiveMaximum') is True
    
    def test_build_with_value_multiple_of(self):
        """Test building schema with value_multiple_of."""
        schema = XWSchemaBuilder.build_schema_dict(type=int, value_multiple_of=5)
        assert schema.get('multipleOf') == 5
    
    # ========================================================================
    # ARRAY CONSTRAINT TESTS
    # ========================================================================
    
    def test_build_with_items(self):
        """Test building schema with items."""
        schema = XWSchemaBuilder.build_schema_dict(
            type=list,
            items={'type': 'string'}
        )
        assert 'items' in schema
        assert schema['items']['type'] == 'string'
    
    def test_build_with_items_min(self):
        """Test building schema with items_min."""
        schema = XWSchemaBuilder.build_schema_dict(type=list, items_min=1)
        assert schema.get('minItems') == 1
    
    def test_build_with_items_max(self):
        """Test building schema with items_max."""
        schema = XWSchemaBuilder.build_schema_dict(type=list, items_max=10)
        assert schema.get('maxItems') == 10
    
    def test_build_with_items_unique(self):
        """Test building schema with items_unique."""
        schema = XWSchemaBuilder.build_schema_dict(type=list, items_unique=True)
        assert schema.get('uniqueItems') is True
    
    # ========================================================================
    # OBJECT CONSTRAINT TESTS
    # ========================================================================
    
    def test_build_with_properties(self):
        """Test building schema with properties."""
        schema = XWSchemaBuilder.build_schema_dict(
            type=dict,
            properties={
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            }
        )
        assert 'properties' in schema
        assert 'name' in schema['properties']
        assert 'age' in schema['properties']
    
    def test_build_with_required(self):
        """Test building schema with required fields."""
        schema = XWSchemaBuilder.build_schema_dict(
            type=dict,
            required=['name']
        )
        assert 'required' in schema
        assert 'name' in schema['required']
    
    def test_build_with_properties_additional_false(self):
        """Test building schema with properties_additional=False."""
        schema = XWSchemaBuilder.build_schema_dict(
            type=dict,
            properties_additional=False
        )
        assert schema.get('additionalProperties') is False
    
    def test_build_with_properties_additional_schema(self):
        """Test building schema with properties_additional as schema."""
        schema = XWSchemaBuilder.build_schema_dict(
            type=dict,
            properties_additional={'type': 'string'}
        )
        assert 'additionalProperties' in schema
        assert isinstance(schema['additionalProperties'], dict)
    
    def test_build_with_properties_min(self):
        """Test building schema with properties_min."""
        schema = XWSchemaBuilder.build_schema_dict(type=dict, properties_min=1)
        assert schema.get('minProperties') == 1
    
    def test_build_with_properties_max(self):
        """Test building schema with properties_max."""
        schema = XWSchemaBuilder.build_schema_dict(type=dict, properties_max=10)
        assert schema.get('maxProperties') == 10
    
    # ========================================================================
    # LOGICAL CONSTRAINT TESTS
    # ========================================================================
    
    def test_build_with_schema_all_of(self):
        """Test building schema with schema_all_of."""
        schema = XWSchemaBuilder.build_schema_dict(
            type=dict,
            schema_all_of=[
                {'type': 'object'},
                {'required': ['name']}
            ]
        )
        assert 'allOf' in schema
        assert len(schema['allOf']) == 2
    
    def test_build_with_schema_any_of(self):
        """Test building schema with schema_any_of."""
        schema = XWSchemaBuilder.build_schema_dict(
            type=dict,
            schema_any_of=[
                {'type': 'string'},
                {'type': 'integer'}
            ]
        )
        assert 'anyOf' in schema
        assert len(schema['anyOf']) == 2
    
    def test_build_with_schema_one_of(self):
        """Test building schema with schema_one_of."""
        schema = XWSchemaBuilder.build_schema_dict(
            type=dict,
            schema_one_of=[
                {'type': 'string'},
                {'type': 'integer'}
            ]
        )
        assert 'oneOf' in schema
        assert len(schema['oneOf']) == 2
    
    def test_build_with_schema_not(self):
        """Test building schema with schema_not."""
        schema = XWSchemaBuilder.build_schema_dict(
            type=dict,
            schema_not={'type': 'null'}
        )
        assert 'not' in schema
    
    # ========================================================================
    # CONDITIONAL CONSTRAINT TESTS
    # ========================================================================
    
    def test_build_with_schema_if_then_else(self):
        """Test building schema with conditional constraints."""
        schema = XWSchemaBuilder.build_schema_dict(
            type=dict,
            schema_if={'properties': {'age': {'type': 'integer'}}},
            schema_then={'required': ['age']},
            schema_else={'required': []}
        )
        assert 'if' in schema
        assert 'then' in schema
        assert 'else' in schema
    
    # ========================================================================
    # COMPREHENSIVE TESTS
    # ========================================================================
    
    def test_build_complex_schema(self):
        """Test building complex schema with multiple properties."""
        schema = XWSchemaBuilder.build_schema_dict(
            type=dict,
            title='User Schema',
            description='Schema for user data',
            properties={
                'name': {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 100
                },
                'age': {
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 150
                },
                'email': {
                    'type': 'string',
                    'format': 'email'
                }
            },
            required=['name', 'email']
        )
        assert schema is not None
        assert schema.get('type') == 'object'
        assert 'properties' in schema
        assert 'required' in schema
        assert len(schema['required']) == 2

