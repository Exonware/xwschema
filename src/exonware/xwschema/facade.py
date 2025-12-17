#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/facade.py

XWSchema Facade - Main User API

This module provides the primary user-facing API with:
- Multi-type __init__ (handles dict/path/XWSchema/merge)
- Rich fluent API with method chaining
- Async operations throughout
- Engine-driven orchestration
- Reuses XWData for schema storage
- Reuses XWSystem for format I/O

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

import asyncio
from typing import Any, Optional, Union
from pathlib import Path
from exonware.xwsystem import get_logger

# Reuse XWData for schema storage
try:
    from exonware.xwdata import XWData
except ImportError:
    XWData = None

from .base import ASchema
from .config import XWSchemaConfig
from .engine import XWSchemaEngine
from .defs import SchemaFormat, ValidationMode, SchemaGenerationMode
from .errors import XWSchemaError, XWSchemaValidationError, XWSchemaParseError
from .builder import XWSchemaBuilder

logger = get_logger(__name__)


class XWSchema(ASchema):
    """
    XWSchema - Universal schema validation and generation facade.
    
    Features:
    - Multi-type constructor (dict/path/XWSchema)
    - Automatic format detection
    - Async operations throughout
    - Fluent chainable API
    - Engine-driven orchestration
    - Reuses XWData for schema storage (reuse!)
    - Reuses XWSystem for format I/O (reuse!)
    
    Examples:
        # From native dict
        schema = XWSchema({'type': 'object', 'properties': {'name': {'type': 'string'}}})
        
        # From file
        schema = await XWSchema.load('schema.json')
        
        # Validate data
        is_valid, errors = await schema.validate({'name': 'Alice'})
        
        # Generate schema from data
        schema = await XWSchema.from_data({'name': 'Alice', 'age': 30})
    """
    
    def __init__(
        self,
        schema: Union[
            dict,                           # Native Python dict
            str, Path,                      # File path
            'XWSchema',                     # Copy from another
            XWData                          # XWData instance (schema stored as data)
        ],
        metadata: Optional[dict] = None,
        config: Optional[XWSchemaConfig] = None,
        **opts
    ):
        """
        Universal constructor handling multiple input types intelligently.
        
        Args:
            schema: Schema in various forms (see type hints)
            metadata: Optional metadata to attach
            config: Optional configuration
            **opts: Additional options
        """
        super().__init__(config)
        self._config = config or XWSchemaConfig.default()
        self._engine = XWSchemaEngine(self._config)
        
        # Multi-type handling
        if isinstance(schema, dict):
            # Native Python dict - store as XWData
            self._schema_data = XWData.from_native(schema, metadata=metadata) if XWData else None
            self._schema_dict = schema
            self._format = SchemaFormat.JSON_SCHEMA  # Default to JSON Schema
        
        elif isinstance(schema, (str, Path)):
            # File path - load it (sync wrapper)
            self._schema_data = None
            self._schema_dict = self._sync_load_file(str(schema))
            if metadata:
                self._metadata.update(metadata)
        
        elif isinstance(schema, XWSchema):
            # Copy from another XWSchema
            self._schema_data = schema._schema_data
            self._schema_dict = schema._schema_dict
            self._format = schema._format
            if metadata:
                self._metadata.update(metadata)
        
        elif XWData and isinstance(schema, XWData):
            # XWData instance - use directly
            self._schema_data = schema
            self._schema_dict = schema.to_native() if hasattr(schema, 'to_native') else {}
            self._format = SchemaFormat.JSON_SCHEMA
        
        else:
            raise XWSchemaError(
                f"Cannot create XWSchema from type: {type(schema).__name__}",
                operation='init',
                context={
                    'expected_type': "dict, str, Path, XWSchema, or XWData",
                    'actual_type': type(schema).__name__
                },
                suggestion=f"Provide schema as dict, file path, XWSchema instance, or XWData instance, not {type(schema).__name__}"
            )
        
        logger.debug(f"XWSchema initialized (format: {self._format.name if self._format else 'unknown'})")
    
    def _sync_load_file(self, path: str) -> dict[str, Any]:
        """Sync wrapper for loading file in __init__."""
        new_loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(new_loop)
            return new_loop.run_until_complete(self._engine.load_schema(Path(path)))
        finally:
            new_loop.close()
            asyncio.set_event_loop(None)
    
    def _ensure_engine(self) -> XWSchemaEngine:
        """Ensure schema engine is initialized."""
        return self._engine
    
    # ==========================================================================
    # FACTORY METHODS
    # ==========================================================================
    
    @classmethod
    def create(
        cls,
        # Basic properties
        type: Optional[Union[type, str]] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        format: Optional[str] = None,
        enum: Optional[list[Any]] = None,
        default: Any = None,
        nullable: bool = False,
        deprecated: bool = False,
        confidential: bool = False,
        
        # Field control
        strict: bool = False,
        alias: Optional[str] = None,
        exclude: bool = False,
        
        # String constraints (OpenAPI standard naming)
        pattern: Optional[str] = None,
        length_min: Optional[int] = None,
        length_max: Optional[int] = None,
        strip_whitespace: bool = False,
        to_upper: bool = False,
        to_lower: bool = False,
        
        # Numeric constraints (OpenAPI standard naming)
        value_min: Optional[Union[int, float]] = None,
        value_max: Optional[Union[int, float]] = None,
        value_min_exclusive: Union[bool, float, int] = False,
        value_max_exclusive: Union[bool, float, int] = False,
        value_multiple_of: Optional[Union[int, float]] = None,
        
        # Array constraints (OpenAPI standard naming)
        items: Optional[dict[str, Any]] = None,
        items_min: Optional[int] = None,
        items_max: Optional[int] = None,
        items_unique: bool = False,
        
        # Object constraints (OpenAPI standard naming)
        properties: Optional[dict[str, dict[str, Any]]] = None,
        required: Optional[list[str]] = None,
        properties_additional: Optional[Union[bool, dict[str, Any]]] = None,
        properties_min: Optional[int] = None,
        properties_max: Optional[int] = None,
        
        # Logical constraints (OpenAPI standard naming)
        schema_all_of: Optional[list[dict[str, Any]]] = None,
        schema_any_of: Optional[list[dict[str, Any]]] = None,
        schema_one_of: Optional[list[dict[str, Any]]] = None,
        schema_not: Optional[dict[str, Any]] = None,
        
        # Conditional constraints (OpenAPI standard naming)
        schema_if: Optional[dict[str, Any]] = None,
        schema_then: Optional[dict[str, Any]] = None,
        schema_else: Optional[dict[str, Any]] = None,
        
        # Content constraints
        content_encoding: Optional[str] = None,
        content_media_type: Optional[str] = None,
        content_schema: Optional[dict[str, Any]] = None,
        
        # Metadata
        example: Any = None,
        examples: Optional[dict[str, Any]] = None,
        
        # References
        ref: Optional[str] = None,
        anchor: Optional[str] = None,
        
        # Configuration
        config: Optional[XWSchemaConfig] = None,
        metadata: Optional[dict] = None,
        
        # Backward compatibility aliases
        **kwargs
    ) -> 'XWSchema':
        """
        Create XWSchema with all properties from old MIGRAT implementation.
        
        Supports all OpenAPI/JSON Schema properties with backward compatibility aliases.
        This method provides the same API as the old XWSchema class.
        
        Examples:
            >>> # Simple string schema
            >>> schema = XWSchema.create(
            ...     type=str,
            ...     length_min=8,
            ...     pattern=r"^[A-Za-z0-9]+$",
            ...     confidential=True
            ... )
            
            >>> # Object schema with properties
            >>> schema = XWSchema.create(
            ...     type=dict,
            ...     properties={
            ...         'name': {'type': 'string'},
            ...         'age': {'type': 'integer', 'minimum': 0}
            ...     },
            ...     required=['name']
            ... )
            
            >>> # Array schema
            >>> schema = XWSchema.create(
            ...     type=list,
            ...     items={'type': 'string'},
            ...     items_min=1,
            ...     items_max=10
            ... )
        """
        # Build schema dict using builder
        schema_dict = XWSchemaBuilder.build_schema_dict(
            type=type,
            title=title,
            description=description,
            format=format,
            enum=enum,
            default=default,
            nullable=nullable,
            deprecated=deprecated,
            confidential=confidential,
            strict=strict,
            alias=alias,
            exclude=exclude,
            pattern=pattern,
            length_min=length_min,
            length_max=length_max,
            strip_whitespace=strip_whitespace,
            to_upper=to_upper,
            to_lower=to_lower,
            value_min=value_min,
            value_max=value_max,
            value_min_exclusive=value_min_exclusive,
            value_max_exclusive=value_max_exclusive,
            value_multiple_of=value_multiple_of,
            items=items,
            items_min=items_min,
            items_max=items_max,
            items_unique=items_unique,
            properties=properties,
            required=required,
            properties_additional=properties_additional,
            properties_min=properties_min,
            properties_max=properties_max,
            schema_all_of=schema_all_of,
            schema_any_of=schema_any_of,
            schema_one_of=schema_one_of,
            schema_not=schema_not,
            schema_if=schema_if,
            schema_then=schema_then,
            schema_else=schema_else,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            content_schema=content_schema,
            example=example,
            examples=examples,
            ref=ref,
            anchor=anchor,
            **kwargs
        )
        
        # Create XWSchema from built dict
        return cls(schema_dict, metadata=metadata, config=config)
    
    @classmethod
    async def load(cls, path: Union[str, Path], format: Optional[SchemaFormat] = None, config: Optional[XWSchemaConfig] = None) -> 'XWSchema':
        """
        Load schema from file.
        
        Args:
            path: Path to schema file
            format: Optional format hint (auto-detected if not provided)
            config: Optional configuration
            
        Returns:
            XWSchema instance
            
        Example:
            >>> schema = await XWSchema.load('schema.json')
            >>> schema = await XWSchema.load('schema.avsc', format=SchemaFormat.AVRO)
        """
        engine = XWSchemaEngine(config or XWSchemaConfig.default())
        schema_dict = await engine.load_schema(Path(path), format)
        return cls(schema_dict, config=config)
    
    @classmethod
    async def from_data(cls, data: Any, mode: SchemaGenerationMode = SchemaGenerationMode.INFER, config: Optional[XWSchemaConfig] = None) -> 'XWSchema':
        """
        Generate schema from data.
        
        Args:
            data: Data to generate schema from (can be dict, list, or XWData instance)
            mode: Generation mode
            config: Optional configuration
            
        Returns:
            XWSchema instance
            
        Example:
            >>> schema = await XWSchema.from_data({'name': 'Alice', 'age': 30})
            >>> schema = await XWSchema.from_data(xwdata_instance, mode=SchemaGenerationMode.COMPREHENSIVE)
        """
        engine = XWSchemaEngine(config or XWSchemaConfig.default())
        schema_dict = await engine.generate_schema(data, mode)
        return cls(schema_dict, config=config)
    
    @classmethod
    def from_native(cls, schema_dict: dict[str, Any], config: Optional[XWSchemaConfig] = None) -> 'XWSchema':
        """
        Create schema from native Python dict.
        
        Args:
            schema_dict: Schema definition as dict
            config: Optional configuration
            
        Returns:
            XWSchema instance
        """
        return cls(schema_dict, config=config)
    
    # ==========================================================================
    # VALIDATION
    # ==========================================================================
    
    async def validate(self, data: Any) -> tuple[bool, list[str]]:
        """
        Validate data against this schema.
        
        Reuses XWData for efficient navigation when data is XWData instance.
        
        Args:
            data: Data to validate (can be dict, list, or XWData instance)
            
        Returns:
            Tuple of (is_valid, error_messages)
            
        Example:
            >>> schema = XWSchema({'type': 'object', 'properties': {'name': {'type': 'string'}}})
            >>> is_valid, errors = await schema.validate({'name': 'Alice'})
            >>> if not is_valid:
            ...     print(f"Validation errors: {errors}")
        """
        try:
            schema_dict = self.to_native()
            return await self._engine.validate_data(data, schema_dict, self._config.validation.mode)
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False, [f"Validation failed: {str(e)}"]
    
    def validate_sync(self, data: Any) -> tuple[bool, list[str]]:
        """
        Synchronous wrapper for validate().
        
        Args:
            data: Data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        new_loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(new_loop)
            return new_loop.run_until_complete(self.validate(data))
        finally:
            new_loop.close()
            asyncio.set_event_loop(None)
    
    async def validate_issues(self, data: Any) -> list[dict[str, str]]:
        """
        Validate data against this schema and return structured issues.
        
        Returns a list of issues with node_path and issue_type for easier error handling.
        
        Args:
            data: Data to validate (can be dict, list, or XWData instance)
            
        Returns:
            List of dictionaries with 'node_path', 'issue_type', and 'message' keys
            
        Example:
            >>> schema = XWSchema({'type': 'object', 'properties': {'name': {'type': 'string'}}})
            >>> issues = await schema.validate_issues({'name': 123})
            >>> for issue in issues:
            ...     print(f"Path: {issue['node_path']}, Type: {issue['issue_type']}, Message: {issue['message']}")
        """
        try:
            schema_dict = self.to_native()
            validator = self._engine._ensure_validator()
            issues = validator.validate_schema_issues(data, schema_dict)
            
            # Convert ValidationIssue objects to dictionaries
            return [
                {
                    'node_path': issue.node_path,
                    'issue_type': issue.issue_type,
                    'message': issue.message
                }
                for issue in issues
            ]
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return [{
                'node_path': '/',
                'issue_type': 'validation_error',
                'message': f"Validation failed: {str(e)}"
            }]
    
    def validate_issues_sync(self, data: Any) -> list[dict[str, str]]:
        """
        Synchronous wrapper for validate_issues().
        
        Args:
            data: Data to validate
            
        Returns:
            List of dictionaries with 'node_path' and 'issue_type' keys
        """
        new_loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(new_loop)
            return new_loop.run_until_complete(self.validate_issues(data))
        finally:
            new_loop.close()
            asyncio.set_event_loop(None)
    
    # ==========================================================================
    # SERIALIZATION
    # ==========================================================================
    
    def to_native(self) -> dict[str, Any]:
        """
        Get native Python dict representation of schema.
        
        Returns:
            Schema definition as dict
        """
        if self._schema_data and XWData:
            return self._schema_data.to_native()
        return self._schema_dict
    
    async def serialize(self, format: Union[str, SchemaFormat], **opts) -> Union[str, bytes]:
        """
        Serialize schema to specified format.
        
        Reuses XWSystem's AutoSerializer for format I/O.
        
        Args:
            format: Target format
            **opts: Additional serialization options
            
        Returns:
            Serialized schema (str for text formats, bytes for binary)
        """
        schema_dict = self.to_native()
        engine = self._ensure_engine()
        
        # Convert format string to enum if needed
        if isinstance(format, str):
            try:
                format = SchemaFormat[format.upper()]
            except KeyError:
                format = SchemaFormat.JSON_SCHEMA  # Default
        
        # Use AutoSerializer's detect_and_serialize method
        serializer = engine._ensure_serializer()
        # Map schema format to serialization format
        format_hint = format.name if isinstance(format, SchemaFormat) else str(format).upper()
        if format_hint == 'JSON_SCHEMA':
            format_hint = 'JSON'
        return serializer.detect_and_serialize(schema_dict, format_hint=format_hint, **opts)
    
    async def save(self, path: Union[str, Path], format: Optional[Union[str, SchemaFormat]] = None, **opts) -> 'XWSchema':
        """
        Save schema to file.
        
        Reuses XWSystem's AutoSerializer for format I/O.
        
        Args:
            path: Path to save schema file
            format: Optional format (auto-detected from extension if not provided)
            **opts: Additional options
            
        Returns:
            Self for chaining
            
        Example:
            >>> await schema.save('schema.json')
            >>> await schema.save('schema.avsc', format=SchemaFormat.AVRO)
        """
        # Detect format from extension if not provided
        if format is None:
            format = self._engine._detect_schema_format(Path(path))
        elif isinstance(format, str):
            try:
                format = SchemaFormat[format.upper()]
            except KeyError:
                format = SchemaFormat.JSON_SCHEMA
        
        schema_dict = self.to_native()
        await self._engine.save_schema(schema_dict, Path(path), format)
        return self
    
    async def reload(self, path: Union[str, Path], format: Optional[Union[str, SchemaFormat]] = None, **opts) -> 'XWSchema':
        """
        Reload schema from file (updates current instance).
        
        Args:
            path: Path to schema file
            format: Optional format hint
            **opts: Additional options
            
        Returns:
            Self for chaining
        """
        if isinstance(format, str):
            try:
                format = SchemaFormat[format.upper()]
            except KeyError:
                format = None
        
        schema_dict = await self._engine.load_schema(Path(path), format)
        self._schema_dict = schema_dict
        if XWData:
            self._schema_data = XWData.from_native(schema_dict)
        return self
    
    # ==========================================================================
    # SCHEMA ACCESS
    # ==========================================================================
    
    def __getitem__(self, key: str) -> Any:
        """
        Get schema property using bracket notation.
        
        Reuses XWData's path navigation if available.
        
        Args:
            key: Schema property path (e.g., 'properties.name.type')
            
        Returns:
            Schema property value
            
        Example:
            >>> schema['properties']['name']['type']  # 'string'
            >>> schema['properties.name.type']  # 'string' (if XWData supports path notation)
        """
        if self._schema_data and XWData:
            try:
                return self._schema_data[key]
            except (KeyError, IndexError):
                pass
        
        # Fallback to native dict access
        keys = key.split('.')
        value = self._schema_dict
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                raise KeyError(f"Schema path '{key}' not found")
        return value
    
    def __repr__(self) -> str:
        """String representation."""
        format_name = self._format.name if self._format else 'unknown'
        return f"<XWSchema(format={format_name}, type={self._schema_dict.get('type', 'unknown')})>"

