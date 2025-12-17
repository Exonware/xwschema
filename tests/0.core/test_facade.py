#!/usr/bin/env python3
"""
Core tests for XWSchema facade.

Tests the main user-facing API including:
- Multi-type constructor
- Factory methods
- Validation
- Serialization
- File I/O
- Method chaining

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.1
Generation Date: 09-Nov-2025
"""

import pytest
import tempfile
import json
from pathlib import Path
from typing import Any, Dict
from exonware.xwschema import XWSchema
from exonware.xwschema.defs import SchemaFormat, ValidationMode, SchemaGenerationMode
from exonware.xwschema.errors import XWSchemaError, XWSchemaValidationError
from exonware.xwschema.config import XWSchemaConfig


@pytest.mark.xwschema_core
class TestXWSchemaFacade:
    """Test XWSchema facade - main user API."""
    
    # ========================================================================
    # CONSTRUCTOR TESTS
    # ========================================================================
    
    def test_init_from_dict(self):
        """Test initialization from native dict."""
        schema_dict = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            }
        }
        schema = XWSchema(schema_dict)
        assert schema is not None
        assert schema.to_native()['type'] == 'object'
    
    def test_init_from_dict_with_metadata(self):
        """Test initialization from dict with metadata."""
        schema_dict = {'type': 'string'}
        metadata = {'author': 'test', 'version': '1.0'}
        schema = XWSchema(schema_dict, metadata=metadata)
        assert schema is not None
    
    def test_init_from_dict_with_config(self):
        """Test initialization from dict with config."""
        schema_dict = {'type': 'string'}
        config = XWSchemaConfig()
        schema = XWSchema(schema_dict, config=config)
        assert schema is not None
    
    def test_init_from_file_path(self):
        """Test initialization from file path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'type': 'string'}, f)
            temp_path = f.name
        
        try:
            schema = XWSchema(temp_path)
            assert schema is not None
        finally:
            Path(temp_path).unlink()
    
    def test_init_from_path_object(self):
        """Test initialization from Path object."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'type': 'string'}, f)
            temp_path = Path(f.name)
        
        try:
            schema = XWSchema(temp_path)
            assert schema is not None
        finally:
            temp_path.unlink()
    
    def test_init_from_xwschema_copy(self):
        """Test initialization from another XWSchema (copy)."""
        original = XWSchema({'type': 'string'})
        copy = XWSchema(original)
        assert copy is not None
        assert copy.to_native() == original.to_native()
    
    def test_init_invalid_type(self):
        """Test initialization with invalid type raises error."""
        with pytest.raises(XWSchemaError):
            XWSchema(123)  # Invalid type
    
    def test_init_empty_dict(self):
        """Test initialization with empty dict."""
        schema = XWSchema({})
        assert schema is not None
    
    def test_init_complex_schema(self):
        """Test initialization with complex nested schema."""
        schema_dict = {
            'type': 'object',
            'properties': {
                'user': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'tags': {
                            'type': 'array',
                            'items': {'type': 'string'}
                        }
                    }
                }
            }
        }
        schema = XWSchema(schema_dict)
        assert schema is not None
        assert schema.to_native()['type'] == 'object'
    
    # ========================================================================
    # FACTORY METHOD TESTS
    # ========================================================================
    
    def test_create_simple_string_schema(self):
        """Test create() with simple string schema."""
        schema = XWSchema.create(type=str, length_min=5, length_max=10)
        assert schema is not None
        native = schema.to_native()
        assert native.get('type') in ['string', str]
    
    def test_create_with_pattern(self):
        """Test create() with pattern constraint."""
        schema = XWSchema.create(
            type=str,
            pattern=r'^[A-Za-z0-9]+$'
        )
        assert schema is not None
    
    def test_create_with_enum(self):
        """Test create() with enum."""
        schema = XWSchema.create(
            type=str,
            enum=['red', 'green', 'blue']
        )
        assert schema is not None
        native = schema.to_native()
        assert 'enum' in native or native.get('type') == 'string'
    
    def test_create_object_schema(self):
        """Test create() with object schema."""
        schema = XWSchema.create(
            type=dict,
            properties={
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            },
            required=['name']
        )
        assert schema is not None
    
    def test_create_array_schema(self):
        """Test create() with array schema."""
        schema = XWSchema.create(
            type=list,
            items={'type': 'string'},
            items_min=1,
            items_max=10
        )
        assert schema is not None
    
    def test_create_with_numeric_constraints(self):
        """Test create() with numeric constraints."""
        schema = XWSchema.create(
            type=int,
            value_min=0,
            value_max=100,
            value_multiple_of=5
        )
        assert schema is not None
    
    def test_create_with_logical_constraints(self):
        """Test create() with logical constraints (allOf)."""
        schema = XWSchema.create(
            type=dict,
            schema_all_of=[
                {'type': 'object'},
                {'required': ['name']}
            ]
        )
        assert schema is not None
    
    def test_create_with_conditional_constraints(self):
        """Test create() with conditional constraints (if/then/else)."""
        schema = XWSchema.create(
            type=dict,
            schema_if={'properties': {'age': {'type': 'integer'}}},
            schema_then={'required': ['age']},
            schema_else={'required': []}
        )
        assert schema is not None
    
    def test_create_with_metadata(self):
        """Test create() with metadata."""
        schema = XWSchema.create(
            type=str,
            title='Test Schema',
            description='A test schema',
            example='test'
        )
        assert schema is not None
    
    def test_from_native(self):
        """Test from_native() class method."""
        schema_dict = {'type': 'string'}
        schema = XWSchema.from_native(schema_dict)
        assert schema is not None
        assert schema.to_native() == schema_dict
    
    def test_from_native_with_config(self):
        """Test from_native() with config."""
        schema_dict = {'type': 'string'}
        config = XWSchemaConfig()
        schema = XWSchema.from_native(schema_dict, config=config)
        assert schema is not None
    
    # ========================================================================
    # VALIDATION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_validate_valid_data(self):
        """Test validate() with valid data."""
        schema = XWSchema({'type': 'string'})
        is_valid, errors = await schema.validate('test')
        assert is_valid
        assert len(errors) == 0
    
    @pytest.mark.asyncio
    async def test_validate_invalid_data(self):
        """Test validate() with invalid data."""
        schema = XWSchema({'type': 'string'})
        is_valid, errors = await schema.validate(123)
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_sync_valid_data(self):
        """Test validate_sync() with valid data."""
        schema = XWSchema({'type': 'string'})
        is_valid, errors = schema.validate_sync('test')
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_sync_invalid_data(self):
        """Test validate_sync() with invalid data."""
        schema = XWSchema({'type': 'string'})
        is_valid, errors = schema.validate_sync(123)
        assert not is_valid
        assert len(errors) > 0
    
    @pytest.mark.asyncio
    async def test_validate_object_with_required(self):
        """Test validate() with object schema and required fields."""
        schema = XWSchema({
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            },
            'required': ['name']
        })
        
        # Valid - has required field
        is_valid, errors = await schema.validate({'name': 'Alice'})
        assert is_valid
        
        # Invalid - missing required field
        is_valid, errors = await schema.validate({'age': 30})
        assert not is_valid
    
    @pytest.mark.asyncio
    async def test_validate_array_with_items(self):
        """Test validate() with array schema and items."""
        schema = XWSchema({
            'type': 'array',
            'items': {'type': 'string'}
        })
        
        # Valid
        is_valid, errors = await schema.validate(['a', 'b', 'c'])
        assert is_valid
        
        # Invalid - wrong item type
        is_valid, errors = await schema.validate([1, 2, 3])
        assert not is_valid
    
    @pytest.mark.asyncio
    async def test_validate_with_enum(self):
        """Test validate() with enum constraint."""
        schema = XWSchema({
            'type': 'string',
            'enum': ['red', 'green', 'blue']
        })
        
        # Valid
        is_valid, errors = await schema.validate('red')
        assert is_valid
        
        # Invalid - not in enum
        is_valid, errors = await schema.validate('yellow')
        assert not is_valid
    
    @pytest.mark.asyncio
    async def test_validate_with_pattern(self):
        """Test validate() with pattern constraint."""
        schema = XWSchema({
            'type': 'string',
            'pattern': r'^[A-Za-z0-9]+$'
        })
        
        # Valid
        is_valid, errors = await schema.validate('abc123')
        assert is_valid
        
        # Invalid - doesn't match pattern
        is_valid, errors = await schema.validate('abc-123')
        assert not is_valid
    
    @pytest.mark.asyncio
    async def test_validate_with_min_max(self):
        """Test validate() with min/max constraints."""
        schema = XWSchema({
            'type': 'integer',
            'minimum': 0,
            'maximum': 100
        })
        
        # Valid
        is_valid, errors = await schema.validate(50)
        assert is_valid
        
        # Invalid - below minimum
        is_valid, errors = await schema.validate(-1)
        assert not is_valid
        
        # Invalid - above maximum
        is_valid, errors = await schema.validate(101)
        assert not is_valid
    
    # ========================================================================
    # SERIALIZATION TESTS
    # ========================================================================
    
    def test_to_native(self):
        """Test to_native() method."""
        schema_dict = {'type': 'string', 'title': 'Test'}
        schema = XWSchema(schema_dict)
        native = schema.to_native()
        assert native['type'] == 'string'
        assert native['title'] == 'Test'
    
    @pytest.mark.asyncio
    async def test_serialize_to_json(self):
        """Test serialize() to JSON format."""
        schema = XWSchema({'type': 'string'})
        result = await schema.serialize('json')
        assert isinstance(result, str)
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed['type'] == 'string'
    
    @pytest.mark.asyncio
    async def test_serialize_to_yaml(self):
        """Test serialize() to YAML format."""
        schema = XWSchema({'type': 'string'})
        result = await schema.serialize('yaml')
        assert isinstance(result, str)
        assert 'string' in result or 'type' in result
    
    # ========================================================================
    # FILE I/O TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_save_and_load_json(self):
        """Test save() and load() with JSON format."""
        schema_dict = {'type': 'string', 'title': 'Test'}
        schema = XWSchema(schema_dict)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # Save
            saved = await schema.save(temp_path, format='json')
            assert saved is not None
            
            # Load (use classmethod)
            loaded = await XWSchema.load(path=temp_path, format=SchemaFormat.JSON_SCHEMA)
            assert loaded is not None
            assert loaded.to_native()['type'] == 'string'
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    @pytest.mark.asyncio
    async def test_load_from_file(self):
        """Test load() class method."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'type': 'string'}, f)
            temp_path = Path(f.name)
        
        try:
            schema = await XWSchema.load(temp_path)
            assert schema is not None
            assert schema.to_native()['type'] == 'string'
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    # ========================================================================
    # INDEXING TESTS
    # ========================================================================
    
    def test_getitem_string_key(self):
        """Test __getitem__ with string key."""
        schema = XWSchema({
            'type': 'object',
            'properties': {
                'name': {'type': 'string'}
            }
        })
        result = schema['properties']
        assert result is not None
    
    def test_getitem_nested_path(self):
        """Test __getitem__ with nested path."""
        schema = XWSchema({
            'type': 'object',
            'properties': {
                'user': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'}
                    }
                }
            }
        })
        # Access nested property
        result = schema['properties']
        assert result is not None
    
    # ========================================================================
    # REPRESENTATION TESTS
    # ========================================================================
    
    def test_repr(self):
        """Test __repr__ method."""
        schema = XWSchema({'type': 'string'})
        repr_str = repr(schema)
        assert isinstance(repr_str, str)
        assert 'XWSchema' in repr_str
    
    # ========================================================================
    # EDGE CASES
    # ========================================================================
    
    def test_empty_schema(self):
        """Test handling of empty schema."""
        schema = XWSchema({})
        assert schema is not None
    
    def test_schema_with_only_type(self):
        """Test schema with only type field."""
        schema = XWSchema({'type': 'string'})
        assert schema is not None
    
    def test_schema_with_custom_properties(self):
        """Test schema with custom properties."""
        schema = XWSchema({
            'type': 'string',
            'x-custom': 'value'
        })
        assert schema is not None
    
    def test_nested_schema_deep(self):
        """Test deeply nested schema."""
        schema = XWSchema({
            'type': 'object',
            'properties': {
                'level1': {
                    'type': 'object',
                    'properties': {
                        'level2': {
                            'type': 'object',
                            'properties': {
                                'level3': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        })
        assert schema is not None

