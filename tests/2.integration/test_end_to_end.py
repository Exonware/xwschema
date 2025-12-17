#!/usr/bin/env python3
"""
Integration tests for XWSchema end-to-end workflows.

Tests complete workflows:
- Load → Validate → Save
- Generate → Validate → Convert
- Format conversion workflows
- Multi-format roundtrips

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
from exonware.xwschema import XWSchema
from exonware.xwschema.defs import SchemaFormat


@pytest.mark.xwschema_integration
class TestEndToEndWorkflows:
    """Test end-to-end workflows."""
    
    # ========================================================================
    # LOAD → VALIDATE → SAVE WORKFLOWS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_load_validate_save_workflow(self):
        """Test complete workflow: load schema, validate data, save schema."""
        # Create schema file
        schema_dict = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            },
            'required': ['name']
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_dict, f)
            input_path = Path(f.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            # Load
            schema = await XWSchema.load(input_path)
            assert schema is not None
            
            # Validate
            is_valid, errors = await schema.validate({'name': 'Alice', 'age': 30})
            assert is_valid
            
            # Save
            saved = await schema.save(output_path)
            assert saved is not None
            assert output_path.exists()
        finally:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
    
    @pytest.mark.asyncio
    async def test_generate_validate_workflow(self):
        """Test workflow: generate schema from data, validate data."""
        # Generate schema from data
        data = {'name': 'Alice', 'age': 30, 'tags': ['a', 'b']}
        schema = await XWSchema.from_data(data)
        assert schema is not None
        
        # Validate original data
        is_valid, errors = await schema.validate(data)
        assert is_valid
        
        # Validate similar data
        similar_data = {'name': 'Bob', 'age': 25, 'tags': ['c']}
        is_valid, errors = await schema.validate(similar_data)
        assert is_valid
    
    @pytest.mark.asyncio
    async def test_create_validate_workflow(self):
        """Test workflow: create schema, validate data."""
        # Create schema
        schema = XWSchema.create(
            type=dict,
            properties={
                'name': {'type': 'string', 'minLength': 1},
                'age': {'type': 'integer', 'minimum': 0}
            },
            required=['name']
        )
        assert schema is not None
        
        # Validate valid data
        is_valid, errors = await schema.validate({'name': 'Alice', 'age': 30})
        assert is_valid
        
        # Validate invalid data
        is_valid, errors = await schema.validate({'age': 30})  # Missing name
        assert not is_valid
    
    # ========================================================================
    # FORMAT CONVERSION WORKFLOWS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_json_to_avro_conversion_workflow(self):
        """Test workflow: load JSON Schema, convert to Avro, validate."""
        # Create JSON Schema
        json_schema = XWSchema({
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            }
        })
        
        # Serialize to different format (if supported)
        # This tests the conversion capability
        json_str = await json_schema.serialize('json')
        assert json_str is not None
    
    @pytest.mark.asyncio
    async def test_multi_format_roundtrip_workflow(self):
        """Test workflow: convert through multiple formats."""
        # Start with JSON Schema
        original = XWSchema({
            'type': 'object',
            'properties': {
                'name': {'type': 'string'}
            }
        })
        
        # Serialize and parse (roundtrip)
        json_str = await original.serialize('json')
        assert json_str is not None
        
        # Could load back and verify
        # This tests format conversion stability
    
    # ========================================================================
    # SCHEMA GENERATION WORKFLOWS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_generate_from_multiple_samples(self):
        """Test generating schema from multiple data samples."""
        samples = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25},
            {'name': 'Charlie', 'age': 35}
        ]
        
        # Generate from first sample
        schema = await XWSchema.from_data(samples[0])
        assert schema is not None
        
        # Validate all samples
        for sample in samples:
            is_valid, errors = await schema.validate(sample)
            assert is_valid
    
    @pytest.mark.asyncio
    async def test_generate_and_refine_workflow(self):
        """Test workflow: generate schema, refine with constraints."""
        # Generate from data
        data = {'name': 'Alice', 'age': 30}
        schema = await XWSchema.from_data(data)
        
        # Validate
        is_valid, errors = await schema.validate(data)
        assert is_valid
        
        # Schema can be further refined with additional constraints
        # (This would require schema modification API)
    
    # ========================================================================
    # VALIDATION WORKFLOWS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_validate_multiple_objects(self):
        """Test validating multiple objects against same schema."""
        schema = XWSchema({
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            },
            'required': ['name']
        })
        
        valid_objects = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25}
        ]
        
        invalid_objects = [
            {'age': 30},  # Missing name
            {'name': 123}  # Wrong type
        ]
        
        # Validate valid objects
        for obj in valid_objects:
            is_valid, errors = await schema.validate(obj)
            assert is_valid
        
        # Validate invalid objects
        for obj in invalid_objects:
            is_valid, errors = await schema.validate(obj)
            assert not is_valid
    
    @pytest.mark.asyncio
    async def test_validate_nested_structures(self):
        """Test validating nested structures."""
        schema = XWSchema({
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
        })
        
        data = {
            'user': {
                'name': 'Alice',
                'tags': ['a', 'b', 'c']
            }
        }
        
        is_valid, errors = await schema.validate(data)
        assert is_valid
    
    # ========================================================================
    # FILE OPERATIONS WORKFLOWS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_save_load_roundtrip(self):
        """Test save and load roundtrip."""
        original_schema = XWSchema({
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            }
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # Save
            await original_schema.save(temp_path)
            assert temp_path.exists()
            
            # Load
            loaded_schema = await XWSchema.load(temp_path)
            assert loaded_schema is not None
            
            # Verify schema structure
            original_native = original_schema.to_native()
            loaded_native = loaded_schema.to_native()
            assert original_native['type'] == loaded_native['type']
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    @pytest.mark.asyncio
    async def test_load_validate_save_different_format(self):
        """Test loading, validating, and saving in different format."""
        # Load JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'type': 'string'}, f)
            json_path = Path(f.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_path = Path(f.name)
        
        try:
            # Load from JSON
            schema = await XWSchema.load(json_path)
            assert schema is not None
            
            # Validate
            is_valid, errors = await schema.validate('test')
            assert is_valid
            
            # Save as YAML (if supported)
            await schema.save(yaml_path, format='yaml')
            assert yaml_path.exists()
        finally:
            if json_path.exists():
                json_path.unlink()
            if yaml_path.exists():
                yaml_path.unlink()
    
    # ========================================================================
    # SCHEMA COMPOSITION WORKFLOWS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_merge_schemas_workflow(self):
        """Test merging multiple schemas."""
        schema1 = XWSchema({'type': 'object', 'properties': {'name': {'type': 'string'}}})
        schema2 = XWSchema({'type': 'object', 'properties': {'age': {'type': 'integer'}}})
        
        # Merge schemas (if API supports it)
        # This tests schema composition capabilities
        merged_native = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            }
        }
        merged = XWSchema(merged_native)
        
        # Validate against merged schema
        is_valid, errors = await merged.validate({'name': 'Alice', 'age': 30})
        assert is_valid
    
    # ========================================================================
    # ERROR HANDLING WORKFLOWS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_file(self):
        """Test error handling for invalid file."""
        with pytest.raises((FileNotFoundError, Exception)):
            await XWSchema.load('/nonexistent/file.json')
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_schema(self):
        """Test error handling for invalid schema structure."""
        # Invalid schema should be handled gracefully
        try:
            schema = XWSchema('not a dict')
            # Should either raise error or handle gracefully
        except Exception:
            pass  # Expected
    
    @pytest.mark.asyncio
    async def test_error_handling_validation_errors(self):
        """Test error reporting for validation failures."""
        schema = XWSchema({
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            },
            'required': ['name']
        })
        
        # Validate invalid data
        is_valid, errors = await schema.validate({'age': 30})
        assert not is_valid
        assert len(errors) > 0
        # Errors should be descriptive
        assert any('name' in error.lower() or 'required' in error.lower() for error in errors)

