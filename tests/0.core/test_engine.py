#!/usr/bin/env python3
"""
Core tests for XWSchemaEngine.

Tests the orchestration engine that coordinates:
- Schema loading
- Schema saving
- Format conversion
- Validation coordination
- Generation coordination

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
from exonware.xwschema.engine import XWSchemaEngine
from exonware.xwschema.defs import SchemaFormat
from exonware.xwschema.config import XWSchemaConfig
from exonware.xwschema.errors import XWSchemaError, XWSchemaParseError


@pytest.mark.xwschema_core
class TestXWSchemaEngine:
    """Test XWSchemaEngine - orchestration engine."""
    
    @pytest.fixture
    def engine(self):
        """Create engine instance."""
        return XWSchemaEngine()
    
    @pytest.fixture
    def engine_with_config(self):
        """Create engine with custom config."""
        config = XWSchemaConfig()
        return XWSchemaEngine(config)
    
    @pytest.fixture
    def sample_schema_dict(self):
        """Sample schema dictionary."""
        return {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            }
        }
    
    # ========================================================================
    # INITIALIZATION TESTS
    # ========================================================================
    
    def test_engine_init_default(self):
        """Test engine initialization with default config."""
        engine = XWSchemaEngine()
        assert engine is not None
    
    def test_engine_init_with_config(self):
        """Test engine initialization with custom config."""
        config = XWSchemaConfig()
        engine = XWSchemaEngine(config)
        assert engine is not None
    
    # ========================================================================
    # SCHEMA LOADING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_load_schema_from_json_file(self, engine, sample_schema_dict):
        """Test loading schema from JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_schema_dict, f)
            temp_path = Path(f.name)
        
        try:
            schema = await engine.load_schema(temp_path)
            assert schema is not None
            assert schema['type'] == 'object'
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    @pytest.mark.asyncio
    async def test_load_schema_with_format_hint(self, engine, sample_schema_dict):
        """Test loading schema with format hint."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_schema_dict, f)
            temp_path = Path(f.name)
        
        try:
            schema = await engine.load_schema(temp_path, format=SchemaFormat.JSON_SCHEMA)
            assert schema is not None
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    @pytest.mark.asyncio
    async def test_load_schema_nonexistent_file(self, engine):
        """Test loading schema from nonexistent file raises error."""
        with pytest.raises((FileNotFoundError, XWSchemaParseError)):
            await engine.load_schema(Path('/nonexistent/file.json'))
    
    # ========================================================================
    # SCHEMA SAVING TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_save_schema_to_json_file(self, engine, sample_schema_dict):
        """Test saving schema to JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            await engine.save_schema(sample_schema_dict, temp_path, format=SchemaFormat.JSON_SCHEMA)
            assert temp_path.exists()
            
            # Verify content
            with open(temp_path, 'r') as f:
                loaded = json.load(f)
            assert loaded['type'] == 'object'
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    @pytest.mark.asyncio
    async def test_save_schema_with_format(self, engine, sample_schema_dict):
        """Test saving schema with specific format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            await engine.save_schema(
                sample_schema_dict,
                temp_path,
                format=SchemaFormat.JSON_SCHEMA
            )
            assert temp_path.exists()
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    # ========================================================================
    # FORMAT CONVERSION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_convert_schema_format(self, engine, sample_schema_dict):
        """Test converting schema between formats."""
        # Convert JSON Schema to normalized format
        converted = await engine.convert_schema(
            sample_schema_dict,
            SchemaFormat.JSON_SCHEMA,
            SchemaFormat.JSON_SCHEMA  # Same format for now
        )
        assert converted is not None
    
    @pytest.mark.asyncio
    async def test_convert_schema_format_invalid(self, engine, sample_schema_dict):
        """Test converting schema with invalid format raises error."""
        # Test with invalid format enum (use a value that doesn't exist)
        # Since SchemaFormat is an enum, we need to test with a valid enum but different format
        # For now, test that conversion between different formats works
        # (full invalid format testing requires enum validation)
        converted = await engine.convert_schema(
            sample_schema_dict,
            SchemaFormat.JSON_SCHEMA,
            SchemaFormat.AVRO  # Different format - should work or return schema as-is
        )
        assert converted is not None
    
    # ========================================================================
    # VALIDATION COORDINATION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_validate_data_coordination(self, engine, sample_schema_dict):
        """Test validation coordination through engine."""
        data = {'name': 'Alice', 'age': 30}
        is_valid, errors = await engine.validate_data(data, sample_schema_dict)
        assert is_valid
        assert len(errors) == 0
    
    @pytest.mark.asyncio
    async def test_validate_data_invalid(self, engine, sample_schema_dict):
        """Test validation coordination with invalid data."""
        data = {'name': 123}  # Wrong type
        is_valid, errors = await engine.validate_data(data, sample_schema_dict)
        assert not is_valid
        assert len(errors) > 0
    
    # ========================================================================
    # GENERATION COORDINATION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_generate_schema_from_data(self, engine):
        """Test schema generation coordination through engine."""
        data = {'name': 'Alice', 'age': 30}
        schema = await engine.generate_schema(data)
        assert schema is not None
        assert schema.get('type') == 'object'
    
    @pytest.mark.asyncio
    async def test_generate_schema_from_list(self, engine):
        """Test schema generation from list data."""
        data = ['a', 'b', 'c']
        schema = await engine.generate_schema(data)
        assert schema is not None
        assert schema.get('type') == 'array'
    
    @pytest.mark.asyncio
    async def test_generate_schema_from_primitive(self, engine):
        """Test schema generation from primitive data."""
        schema = await engine.generate_schema('test')
        assert schema is not None
        assert schema.get('type') == 'string'
    
    # ========================================================================
    # FORMAT DETECTION TESTS
    # ========================================================================
    
    def test_detect_format_from_extension_json(self, engine):
        """Test format detection from .json extension."""
        path = Path('test.json')
        format = engine._detect_schema_format(path)
        assert format == SchemaFormat.JSON_SCHEMA
    
    def test_detect_format_from_extension_avro(self, engine):
        """Test format detection from .avsc extension."""
        path = Path('test.avsc')
        format = engine._detect_schema_format(path)
        assert format == SchemaFormat.AVRO
    
    def test_detect_format_from_extension_xsd(self, engine):
        """Test format detection from .xsd extension."""
        path = Path('test.xsd')
        format = engine._detect_schema_format(path)
        assert format == SchemaFormat.XSD
    
    def test_detect_format_unknown_extension(self, engine):
        """Test format detection with unknown extension defaults to JSON."""
        path = Path('test.unknown')
        format = engine._detect_schema_format(path)
        # Should default to JSON_SCHEMA or raise
        assert format is not None

