#!/usr/bin/env python3
"""
Core tests for XWSchemaValidator.

Tests schema validation functionality including:
- Type validation
- Constraint validation
- Required fields
- Nested validation
- Error reporting

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.1
Generation Date: 09-Nov-2025
"""

import pytest
from exonware.xwschema.validator import XWSchemaValidator
from exonware.xwschema.defs import ValidationMode
from exonware.xwschema.errors import XWSchemaValidationError


@pytest.mark.xwschema_core
class TestXWSchemaValidator:
    """Test XWSchemaValidator - validation implementation."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return XWSchemaValidator()
    
    @pytest.fixture
    def validator_strict(self):
        """Create strict validator."""
        return XWSchemaValidator(ValidationMode.STRICT)
    
    @pytest.fixture
    def validator_loose(self):
        """Create loose validator."""
        return XWSchemaValidator(ValidationMode.LOOSE)
    
    # ========================================================================
    # TYPE VALIDATION TESTS
    # ========================================================================
    
    def test_validate_string_type(self, validator):
        """Test validation of string type."""
        schema = {'type': 'string'}
        is_valid, errors = validator.validate_schema('test', schema)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_string_type_invalid(self, validator):
        """Test validation of string type with invalid data."""
        schema = {'type': 'string'}
        is_valid, errors = validator.validate_schema(123, schema)
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_integer_type(self, validator):
        """Test validation of integer type."""
        schema = {'type': 'integer'}
        is_valid, errors = validator.validate_schema(42, schema)
        assert is_valid
    
    def test_validate_integer_type_invalid(self, validator):
        """Test validation of integer type with invalid data."""
        schema = {'type': 'integer'}
        is_valid, errors = validator.validate_schema('not a number', schema)
        assert not is_valid
    
    def test_validate_number_type(self, validator):
        """Test validation of number type."""
        schema = {'type': 'number'}
        is_valid, errors = validator.validate_schema(3.14, schema)
        assert is_valid
    
    def test_validate_boolean_type(self, validator):
        """Test validation of boolean type."""
        schema = {'type': 'boolean'}
        is_valid, errors = validator.validate_schema(True, schema)
        assert is_valid
    
    def test_validate_array_type(self, validator):
        """Test validation of array type."""
        schema = {'type': 'array'}
        is_valid, errors = validator.validate_schema([1, 2, 3], schema)
        assert is_valid
    
    def test_validate_object_type(self, validator):
        """Test validation of object type."""
        schema = {'type': 'object'}
        is_valid, errors = validator.validate_schema({'key': 'value'}, schema)
        assert is_valid
    
    def test_validate_null_type(self, validator):
        """Test validation of null type."""
        schema = {'type': 'null'}
        is_valid, errors = validator.validate_schema(None, schema)
        assert is_valid
    
    # ========================================================================
    # CONSTRAINT VALIDATION TESTS
    # ========================================================================
    
    def test_validate_min_length(self, validator):
        """Test validation with minLength constraint."""
        schema = {'type': 'string', 'minLength': 5}
        is_valid, errors = validator.validate_schema('hello', schema)
        assert is_valid
        
        is_valid, errors = validator.validate_schema('hi', schema)
        assert not is_valid
    
    def test_validate_max_length(self, validator):
        """Test validation with maxLength constraint."""
        schema = {'type': 'string', 'maxLength': 5}
        is_valid, errors = validator.validate_schema('hello', schema)
        assert is_valid
        
        is_valid, errors = validator.validate_schema('hello world', schema)
        assert not is_valid
    
    def test_validate_pattern(self, validator):
        """Test validation with pattern constraint."""
        schema = {'type': 'string', 'pattern': r'^[A-Za-z0-9]+$'}
        is_valid, errors = validator.validate_schema('abc123', schema)
        assert is_valid
        
        is_valid, errors = validator.validate_schema('abc-123', schema)
        assert not is_valid
    
    def test_validate_minimum(self, validator):
        """Test validation with minimum constraint."""
        schema = {'type': 'integer', 'minimum': 0}
        is_valid, errors = validator.validate_schema(5, schema)
        assert is_valid
        
        is_valid, errors = validator.validate_schema(-1, schema)
        assert not is_valid
    
    def test_validate_maximum(self, validator):
        """Test validation with maximum constraint."""
        schema = {'type': 'integer', 'maximum': 100}
        is_valid, errors = validator.validate_schema(50, schema)
        assert is_valid
        
        is_valid, errors = validator.validate_schema(101, schema)
        assert not is_valid
    
    def test_validate_multiple_of(self, validator):
        """Test validation with multipleOf constraint."""
        schema = {'type': 'integer', 'multipleOf': 5}
        is_valid, errors = validator.validate_schema(10, schema)
        assert is_valid
        
        is_valid, errors = validator.validate_schema(7, schema)
        assert not is_valid
    
    # ========================================================================
    # REQUIRED FIELDS TESTS
    # ========================================================================
    
    def test_validate_required_fields_present(self, validator):
        """Test validation with required fields present."""
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            },
            'required': ['name']
        }
        data = {'name': 'Alice', 'age': 30}
        is_valid, errors = validator.validate_schema(data, schema)
        assert is_valid
    
    def test_validate_required_fields_missing(self, validator):
        """Test validation with required fields missing."""
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            },
            'required': ['name']
        }
        data = {'age': 30}  # Missing 'name'
        is_valid, errors = validator.validate_schema(data, schema)
        assert not is_valid
        assert any('required' in error.lower() or 'name' in error.lower() for error in errors)
    
    # ========================================================================
    # ARRAY VALIDATION TESTS
    # ========================================================================
    
    def test_validate_array_items(self, validator):
        """Test validation of array with items schema."""
        schema = {
            'type': 'array',
            'items': {'type': 'string'}
        }
        is_valid, errors = validator.validate_schema(['a', 'b', 'c'], schema)
        assert is_valid
    
    def test_validate_array_items_invalid(self, validator):
        """Test validation of array with invalid items."""
        schema = {
            'type': 'array',
            'items': {'type': 'string'}
        }
        is_valid, errors = validator.validate_schema([1, 2, 3], schema)
        assert not is_valid
    
    def test_validate_array_min_items(self, validator):
        """Test validation with minItems constraint."""
        schema = {
            'type': 'array',
            'items': {'type': 'string'},
            'minItems': 2
        }
        is_valid, errors = validator.validate_schema(['a', 'b'], schema)
        assert is_valid
        
        is_valid, errors = validator.validate_schema(['a'], schema)
        assert not is_valid
    
    def test_validate_array_max_items(self, validator):
        """Test validation with maxItems constraint."""
        schema = {
            'type': 'array',
            'items': {'type': 'string'},
            'maxItems': 2
        }
        is_valid, errors = validator.validate_schema(['a', 'b'], schema)
        assert is_valid
        
        is_valid, errors = validator.validate_schema(['a', 'b', 'c'], schema)
        assert not is_valid
    
    def test_validate_array_unique_items(self, validator):
        """Test validation with uniqueItems constraint."""
        schema = {
            'type': 'array',
            'items': {'type': 'string'},
            'uniqueItems': True
        }
        is_valid, errors = validator.validate_schema(['a', 'b', 'c'], schema)
        assert is_valid
        
        is_valid, errors = validator.validate_schema(['a', 'a', 'b'], schema)
        assert not is_valid
    
    # ========================================================================
    # OBJECT VALIDATION TESTS
    # ========================================================================
    
    def test_validate_object_properties(self, validator):
        """Test validation of object with properties."""
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            }
        }
        data = {'name': 'Alice', 'age': 30}
        is_valid, errors = validator.validate_schema(data, schema)
        assert is_valid
    
    def test_validate_object_additional_properties_false(self, validator):
        """Test validation with additionalProperties: false."""
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'}
            },
            'additionalProperties': False
        }
        data = {'name': 'Alice'}
        is_valid, errors = validator.validate_schema(data, schema)
        assert is_valid
        
        data = {'name': 'Alice', 'extra': 'value'}
        is_valid, errors = validator.validate_schema(data, schema)
        assert not is_valid
    
    def test_validate_object_min_properties(self, validator):
        """Test validation with minProperties constraint."""
        schema = {
            'type': 'object',
            'minProperties': 2
        }
        data = {'a': 1, 'b': 2}
        is_valid, errors = validator.validate_schema(data, schema)
        assert is_valid
        
        data = {'a': 1}
        is_valid, errors = validator.validate_schema(data, schema)
        assert not is_valid
    
    def test_validate_object_max_properties(self, validator):
        """Test validation with maxProperties constraint."""
        schema = {
            'type': 'object',
            'maxProperties': 2
        }
        data = {'a': 1, 'b': 2}
        is_valid, errors = validator.validate_schema(data, schema)
        assert is_valid
        
        data = {'a': 1, 'b': 2, 'c': 3}
        is_valid, errors = validator.validate_schema(data, schema)
        assert not is_valid
    
    # ========================================================================
    # ENUM VALIDATION TESTS
    # ========================================================================
    
    def test_validate_enum_valid(self, validator):
        """Test validation with enum - valid value."""
        schema = {
            'type': 'string',
            'enum': ['red', 'green', 'blue']
        }
        is_valid, errors = validator.validate_schema('red', schema)
        assert is_valid
    
    def test_validate_enum_invalid(self, validator):
        """Test validation with enum - invalid value."""
        schema = {
            'type': 'string',
            'enum': ['red', 'green', 'blue']
        }
        is_valid, errors = validator.validate_schema('yellow', schema)
        assert not is_valid
    
    # ========================================================================
    # NESTED VALIDATION TESTS
    # ========================================================================
    
    def test_validate_nested_object(self, validator):
        """Test validation of nested object."""
        schema = {
            'type': 'object',
            'properties': {
                'user': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'}
                    }
                }
            }
        }
        data = {'user': {'name': 'Alice'}}
        is_valid, errors = validator.validate_schema(data, schema)
        assert is_valid
    
    def test_validate_nested_array(self, validator):
        """Test validation of nested array."""
        schema = {
            'type': 'object',
            'properties': {
                'tags': {
                    'type': 'array',
                    'items': {'type': 'string'}
                }
            }
        }
        data = {'tags': ['a', 'b', 'c']}
        is_valid, errors = validator.validate_schema(data, schema)
        assert is_valid
    
    # ========================================================================
    # NULLABLE TESTS
    # ========================================================================
    
    def test_validate_nullable_true(self, validator):
        """Test validation with nullable: true."""
        schema = {
            'type': 'string',
            'nullable': True
        }
        is_valid, errors = validator.validate_schema('test', schema)
        assert is_valid
        
        is_valid, errors = validator.validate_schema(None, schema)
        assert is_valid
    
    def test_validate_nullable_false(self, validator):
        """Test validation with nullable: false."""
        schema = {
            'type': 'string',
            'nullable': False
        }
        is_valid, errors = validator.validate_schema('test', schema)
        assert is_valid
        
        is_valid, errors = validator.validate_schema(None, schema)
        assert not is_valid
    
    # ========================================================================
    # ERROR HANDLING TESTS
    # ========================================================================
    
    def test_validate_invalid_schema_structure(self, validator):
        """Test validation with invalid schema structure."""
        schema = 'not a dict'
        data = {'test': 'value'}
        # Should handle gracefully
        is_valid, errors = validator.validate_schema(data, schema)
        # Either returns False or handles gracefully
        assert isinstance(is_valid, bool)
    
    def test_validate_missing_type(self, validator):
        """Test validation with schema missing type."""
        schema = {'properties': {'name': {'type': 'string'}}}
        data = {'name': 'Alice'}
        # Should handle gracefully
        is_valid, errors = validator.validate_schema(data, schema)
        assert isinstance(is_valid, bool)

