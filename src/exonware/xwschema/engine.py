#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/engine.py

XWSchemaEngine - The Brain of XWSchema

This module provides the core orchestration engine that coordinates:
- XWData for schema storage and data navigation
- XWSystem's AutoSerializer for schema format I/O
- XWSchemaValidator for validation
- XWSchemaGenerator for schema generation
- Format conversion between schema formats

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

import asyncio
from typing import Any, Optional
from pathlib import Path
from exonware.xwsystem import get_logger
from exonware.xwsystem.io.serialization.auto_serializer import AutoSerializer

# Reuse XWData for schema storage
try:
    from exonware.xwdata import XWData
except ImportError:
    XWData = None

from .base import ASchemaEngine
from .config import XWSchemaConfig
from .defs import SchemaFormat, ValidationMode, SchemaGenerationMode
from .errors import (
    XWSchemaError, XWSchemaParseError, XWSchemaFormatError,
    XWSchemaValidationError
)
from .validator import XWSchemaValidator
from .generator import XWSchemaGenerator

logger = get_logger(__name__)


# ==============================================================================
# SCHEMA FORMAT EXTENSION MAPPING
# ==============================================================================

_SCHEMA_FORMAT_EXTENSIONS = {
    # JSON Schema
    '.json': SchemaFormat.JSON_SCHEMA,
    '.schema.json': SchemaFormat.JSON_SCHEMA,
    
    # Avro
    '.avsc': SchemaFormat.AVRO,
    '.avro': SchemaFormat.AVRO,
    
    # Protobuf
    '.proto': SchemaFormat.PROTOBUF,
    
    # OpenAPI
    '.openapi.json': SchemaFormat.OPENAPI,
    '.openapi.yaml': SchemaFormat.OPENAPI,
    '.openapi.yml': SchemaFormat.OPENAPI,
    
    # Swagger
    '.swagger.json': SchemaFormat.SWAGGER,
    '.swagger.yaml': SchemaFormat.SWAGGER,
    
    # GraphQL
    '.graphql': SchemaFormat.GRAPHQL,
    '.gql': SchemaFormat.GRAPHQL,
    
    # XML Schema
    '.xsd': SchemaFormat.XSD,
    '.wsdl': SchemaFormat.WSDL,
}


class XWSchemaEngine(ASchemaEngine):
    """
    Universal schema engine orchestrating all xwschema operations.
    
    The engine is the brain of xwschema, coordinating:
    1. Schema storage via XWData (reuse, no duplication)
    2. Format I/O via xwsystem's AutoSerializer (reuse, no duplication)
    3. Validation via XWSchemaValidator
    4. Generation via XWSchemaGenerator
    5. Format conversion between schema formats
    
    This is a pure orchestration engine - it delegates to specialized
    components and doesn't implement low-level logic itself.
    """
    
    def __init__(self, config: Optional[XWSchemaConfig] = None):
        """
        Initialize schema engine with configuration.
        
        Args:
            config: Optional configuration (uses defaults if not provided)
        """
        super().__init__(config)
        self._config = config or XWSchemaConfig.default()
        
        # Core components (lazy initialization)
        self._serializer: Optional[AutoSerializer] = None
        self._validator: Optional[XWSchemaValidator] = None
        self._generator: Optional[XWSchemaGenerator] = None
        
        logger.debug("XWSchemaEngine initialized")
    
    # ==========================================================================
    # SERIALIZER MANAGEMENT
    # ==========================================================================
    
    def _ensure_serializer(self) -> AutoSerializer:
        """
        Lazy initialize AutoSerializer from xwsystem.
        
        Reuses xwsystem's serialization infrastructure.
        """
        if self._serializer is None:
            # Use AutoSerializer from xwsystem (reuse, no duplication)
            self._serializer = AutoSerializer(default_format='JSON')
            logger.debug("xwschema: Initialized AutoSerializer from xwsystem")
        
        return self._serializer
    
    # ==========================================================================
    # VALIDATOR MANAGEMENT
    # ==========================================================================
    
    def _ensure_validator(self) -> XWSchemaValidator:
        """Lazy initialize validator."""
        if self._validator is None:
            self._validator = XWSchemaValidator(mode=self._config.validation.mode)
        return self._validator
    
    # ==========================================================================
    # GENERATOR MANAGEMENT
    # ==========================================================================
    
    def _ensure_generator(self) -> XWSchemaGenerator:
        """Lazy initialize generator."""
        if self._generator is None:
            self._generator = XWSchemaGenerator(config=self._config.generation)
        return self._generator
    
    # ==========================================================================
    # SCHEMA FORMAT DETECTION
    # ==========================================================================
    
    def _detect_schema_format(self, path: Path) -> SchemaFormat:
        """Detect schema format from file extension."""
        suffix = path.suffix.lower()
        
        # Try exact match first
        if suffix in _SCHEMA_FORMAT_EXTENSIONS:
            return _SCHEMA_FORMAT_EXTENSIONS[suffix]
        
        # Try compound extensions (e.g., .schema.json)
        for ext, format_type in _SCHEMA_FORMAT_EXTENSIONS.items():
            if str(path).lower().endswith(ext):
                return format_type
        
        # Default to JSON Schema
        return SchemaFormat.JSON_SCHEMA
    
    # ==========================================================================
    # SCHEMA LOADING
    # ==========================================================================
    
    async def load_schema(self, path: Path, format: Optional[SchemaFormat] = None) -> dict[str, Any]:
        """
        Load schema from file.
        
        Reuses XWSystem's AutoSerializer for format I/O.
        
        Args:
            path: Path to schema file
            format: Optional format hint (auto-detected if not provided)
            
        Returns:
            Schema definition as dict
        """
        try:
            # Detect format if not provided
            if format is None:
                format = self._detect_schema_format(path)
            
            # Use XWSystem's AutoSerializer (reuse, no duplication)
            serializer = self._ensure_serializer()
            
            # Load schema file
            # Note: For now, we use JSON/YAML loading. Schema-specific parsers
            # (Avro, Protobuf, etc.) will be added as format handlers in xwsystem
            # Use auto_load_file_async for async file loading
            format_hint = format.name if format else None
            if format_hint:
                # Map schema format to serialization format
                format_hint = format_hint.replace('_', '').upper()  # JSON_SCHEMA -> JSONSCHEMA -> JSON
                if format_hint == 'JSONSCHEMA':
                    format_hint = 'JSON'
            schema_dict = await serializer.auto_load_file_async(path, format_hint=format_hint)
            
            if not isinstance(schema_dict, dict):
                raise XWSchemaParseError(
                    f"Schema file does not contain a valid schema object",
                    path=str(path),
                    format=format.name
                )
            
            logger.debug(f"Loaded schema from {path} (format: {format.name})")
            return schema_dict
            
        except Exception as e:
            raise XWSchemaParseError(
                f"Failed to load schema from {path}: {e}",
                path=str(path),
                format=format.name if format else None
            ) from e
    
    # ==========================================================================
    # SCHEMA SAVING
    # ==========================================================================
    
    async def save_schema(self, schema: dict[str, Any], path: Path, format: SchemaFormat) -> None:
        """
        Save schema to file.
        
        Reuses XWSystem's AutoSerializer for format I/O.
        
        Args:
            schema: Schema definition
            path: Path to save schema file
            format: Schema format
        """
        try:
            # Use XWSystem's AutoSerializer (reuse, no duplication)
            serializer = self._ensure_serializer()
            
            # Save schema file
            # Note: For now, we use JSON/YAML serialization. Schema-specific
            # serializers (Avro, Protobuf, etc.) will be added as format handlers
            # Use auto_save_file_async for async file saving
            format_hint = format.name if format else None
            if format_hint:
                # Map schema format to serialization format
                format_hint = format_hint.replace('_', '').upper()  # JSON_SCHEMA -> JSONSCHEMA -> JSON
                if format_hint == 'JSONSCHEMA':
                    format_hint = 'JSON'
            await serializer.auto_save_file_async(schema, path, format_hint=format_hint)
            
            logger.debug(f"Saved schema to {path} (format: {format.name})")
            
        except Exception as e:
            raise XWSchemaError(
                f"Failed to save schema to {path}: {e}",
                operation='save',
                path=str(path),
                format=format.name
            ) from e
    
    # ==========================================================================
    # VALIDATION
    # ==========================================================================
    
    async def validate_data(self, data: Any, schema: dict[str, Any], mode: ValidationMode = ValidationMode.STRICT) -> tuple[bool, list[str]]:
        """
        Validate data against schema.
        
        Reuses XWSchemaValidator which uses XWData for efficient navigation.
        
        Args:
            data: Data to validate (can be dict, list, or XWData instance)
            schema: Schema definition
            mode: Validation mode
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        validator = self._ensure_validator()
        return validator.validate_schema(data, schema)
    
    # ==========================================================================
    # SCHEMA GENERATION
    # ==========================================================================
    
    async def generate_schema(self, data: Any, mode: SchemaGenerationMode = SchemaGenerationMode.INFER) -> dict[str, Any]:
        """
        Generate schema from data.
        
        Reuses XWSchemaGenerator which uses XWData for structure analysis.
        
        Args:
            data: Data to generate schema from (can be dict, list, or XWData instance)
            mode: Generation mode
            
        Returns:
            Schema definition
        """
        generator = self._ensure_generator()
        return await generator.generate_from_data(data, mode)
    
    # ==========================================================================
    # FORMAT CONVERSION
    # ==========================================================================
    
    async def convert_schema(self, schema: dict[str, Any], from_format: SchemaFormat, to_format: SchemaFormat) -> dict[str, Any]:
        """
        Convert schema between formats.
        
        Args:
            schema: Schema definition
            from_format: Source format
            to_format: Target format
            
        Returns:
            Converted schema definition
            
        Note:
            Full format conversion will be implemented when schema format
            serializers (Avro, Protobuf, etc.) are added to xwsystem.
            For now, this is a placeholder that returns the schema as-is
            if formats are the same, or converts JSON Schema to other formats
            when converters are available.
        """
        if from_format == to_format:
            return schema
        
        # For now, return schema as-is
        # TODO: Implement format converters when schema format serializers are added
        # Handle case where format might be a string (for error cases)
        from_format_name = from_format.name if hasattr(from_format, 'name') else str(from_format)
        to_format_name = to_format.name if hasattr(to_format, 'name') else str(to_format)
        logger.warning(
            f"Format conversion from {from_format_name} to {to_format_name} "
            "not yet fully implemented. Returning schema as-is."
        )
        
        return schema

