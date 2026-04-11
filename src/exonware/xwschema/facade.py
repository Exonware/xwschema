#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/facade.py
XWSchema Facade - Main User API
This module provides the primary user-facing API with:
- Multi-type __init__ (handles dict/path/XWSchema/merge)
- Rich fluent API with method chaining
- Async operations throughout
- Engine-driven orchestration
This module fully reuses ecosystem libraries:
- xwdata: For schema storage and navigation (XWData.from_native(), to_native())
  - Uses XWData for path-based schema access
  - Uses XWData's query capabilities for schema queries
- xwsystem: For format I/O (AutoSerializer, JsonSerializer, YamlSerializer, etc.)
  - Uses xwsystem serialization registry for all file I/O
  - Uses xwsystem.get_logger() for logging
- No manual serialization or data manipulation - all delegated to libraries
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.11
Generation Date: 09-Nov-2025
"""

from __future__ import annotations
import asyncio
import inspect
import threading
from typing import Any
from collections.abc import Callable
from pathlib import Path
from collections import OrderedDict
from datetime import datetime
# Fully reuse xwsystem for logging and JSON
from exonware.xwsystem import get_logger, get_serializer, JsonSerializer
# xwdata is the base engine for xwschema (required dependency)
from exonware.xwdata import XWData
from .base import ASchema
from .config import XWSchemaConfig
from .engine import XWSchemaEngine
from .defs import SchemaFormat, ValidationMode, SchemaGenerationMode
from .errors import XWSchemaError, XWSchemaValidationError, XWSchemaParseError
from .builder import XWSchemaBuilder
from .type_utils import normalize_schema_dict, class_to_string, string_to_class
logger = get_logger(__name__)
_json_serializer = get_serializer(JsonSerializer)


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
    - Extends XWObject for identity management, timestamps, and metadata
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
        schema: dict | str | Path | XWSchema | XWData,
        metadata: dict | None = None,
        config: XWSchemaConfig | None = None,
        **opts
    ):
        """
        Universal constructor handling multiple input types intelligently.
        Args:
            schema: Schema in various forms:
                   - dict: Native Python dict
                   - str/Path: File path
                   - XWSchema: Copy from another
                   - XWData: XWData instance (schema stored as data)
            metadata: Optional metadata to attach
            config: Optional configuration
            **opts: Additional options
        """
        super().__init__(config=config)
        self._config = config or XWSchemaConfig.default()
        self._engine = XWSchemaEngine(self._config)
        # Multi-type handling
        if isinstance(schema, dict):
            # Normalize schema dict - convert class types to strings for storage
            # This allows users to use: {"type": XWSchema} or {"type": "exonware.xwschema.XWSchema"}
            normalized_schema = normalize_schema_dict(schema)
            # xwdata is the base engine: XWData for schema storage (path-based access, query, format-agnostic)
            self._schema_data = XWData.from_native(normalized_schema, metadata=metadata)
            self._schema_dict = normalized_schema
            self._format = SchemaFormat.JSON_SCHEMA  # Default to JSON Schema
        elif isinstance(schema, (str, Path)):
            self._schema_dict = self._sync_load_file(str(schema))
            self._schema_data = XWData.from_native(self._schema_dict)
            if metadata:
                self._metadata.update(metadata)
        elif isinstance(schema, XWSchema):
            # Copy from another XWSchema
            self._schema_data = schema._schema_data
            self._schema_dict = schema._schema_dict
            self._format = schema._format
            if metadata:
                self._metadata.update(metadata)
        elif isinstance(schema, XWData):
            # xwdata is the base engine: use XWData instance directly
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
        self._data = self._schema_data
        # Semantic id from schema $id / id (never use uid)
        schema_id = self._schema_dict.get("$id") or self._schema_dict.get("id")
        if schema_id is not None:
            self._id = str(schema_id)
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
        type: type | str | None = None,
        title: str | None = None,
        description: str | None = None,
        format: str | None = None,
        enum: list[Any] | None = None,
        default: Any = None,
        nullable: bool = False,
        deprecated: bool = False,
        confidential: bool = False,
        # Field control
        strict: bool = False,
        alias: str | None = None,
        exclude: bool = False,
        # String constraints (OpenAPI standard naming)
        pattern: str | None = None,
        length_min: int | None = None,
        length_max: int | None = None,
        strip_whitespace: bool = False,
        to_upper: bool = False,
        to_lower: bool = False,
        # Numeric constraints (OpenAPI standard naming)
        value_min: int | float | None = None,
        value_max: int | float | None = None,
        value_min_exclusive: bool | float | int = False,
        value_max_exclusive: bool | float | int = False,
        value_multiple_of: int | float | None = None,
        # Array constraints (OpenAPI standard naming)
        items: dict[str, Any] | None = None,
        items_min: int | None = None,
        items_max: int | None = None,
        items_unique: bool = False,
        # Object constraints (OpenAPI standard naming)
        properties: dict[str, dict[str, Any]] | None = None,
        required: list[str] | None = None,
        properties_additional: bool | dict[str, Any] | None = None,
        properties_min: int | None = None,
        properties_max: int | None = None,
        # Logical constraints (OpenAPI standard naming)
        schema_all_of: list[dict[str, Any]] | None = None,
        schema_any_of: list[dict[str, Any]] | None = None,
        schema_one_of: list[dict[str, Any]] | None = None,
        schema_not: dict[str, Any] | None = None,
        # Conditional constraints (OpenAPI standard naming)
        schema_if: dict[str, Any] | None = None,
        schema_then: dict[str, Any] | None = None,
        schema_else: dict[str, Any] | None = None,
        # Content constraints
        content_encoding: str | None = None,
        content_media_type: str | None = None,
        content_schema: dict[str, Any] | None = None,
        # Metadata
        example: Any = None,
        examples: dict[str, Any] | None = None,
        # References
        ref: str | None = None,
        anchor: str | None = None,
        # Configuration
        config: XWSchemaConfig | None = None,
        metadata: dict | None = None,
    ) -> XWSchema:
        """
        Create XWSchema with all properties from old MIGRAT implementation.
        Supports all OpenAPI/JSON Schema properties.
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
        )
        # Create XWSchema from built dict
        return cls(schema_dict, metadata=metadata, config=config)
    @classmethod

    async def load(cls, path: str | Path, format: SchemaFormat | str | None = None, config: XWSchemaConfig | None = None) -> XWSchema:
        """
        Load schema from file or URL.
        Args:
            path: Path to schema file or URL (str or Path)
            format: Optional format (e.g. "json", or SchemaFormat; auto-detected for files)
            config: Optional configuration
        Returns:
            XWSchema instance
        Example:
            >>> schema = await XWSchema.load('schema.json')
            >>> schema = await XWSchema.load('https://spec.openapis.org/oas/3.1/schema/2022-10-07', format='json')
            >>> schema = await XWSchema.load('schema.avsc', format=SchemaFormat.AVRO)
        """
        if isinstance(format, str):
            format = SchemaFormat.JSON_SCHEMA if format.lower() in ("json", "json_schema") else SchemaFormat[format.upper().replace("-", "_")]
        engine = XWSchemaEngine(config or XWSchemaConfig.default())
        schema_dict = await engine.load_schema(path, format)
        return cls(schema_dict, config=config)
    @classmethod

    async def from_data(cls, data: Any, mode: SchemaGenerationMode = SchemaGenerationMode.INFER, config: XWSchemaConfig | None = None) -> XWSchema:
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

    def from_native(cls, schema_dict: dict[str, Any], config: XWSchemaConfig | None = None) -> XWSchema:
        """
        Create schema from native Python dict.
        Args:
            schema_dict: Schema definition as dict
            config: Optional configuration
        Returns:
            XWSchema instance
        """
        return cls(schema_dict, config=config)
    @classmethod

    def from_string(cls, s: str, config: XWSchemaConfig | None = None) -> XWSchema:
        """
        Create schema from JSON string (reuses XWObject.from_string pattern).
        Uses xwsystem JsonSerializer; constructs XWSchema(schema_dict).
        """
        from exonware.xwsystem.io.serialization import JsonSerializer
        return cls(JsonSerializer().decode(s), config=config)
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

    async def check(self, data: Any) -> dict[str, Any]:
        """
        Schema check on XW data: validate and return result dict (same shape as xwdata SchemaValidator).
        Use this for integration with xwdata or when you need a dict with 'valid' and 'errors'.
        Accepts XWData, dict, or list.
        Args:
            data: Data to validate (XWData, dict, or list)
        Returns:
            Dict with 'valid' (bool), 'errors' (list[str]), and optionally 'format'
        Example:
            >>> schema = XWSchema({'type': 'object', 'properties': {'name': {'type': 'string'}}})
            >>> result = await schema.check(xwdata_instance)
            >>> if not result['valid']:
            ...     print(result['errors'])
        """
        is_valid, errors = await self.validate(data)
        return {'valid': is_valid, 'errors': errors or []}

    def check_sync(self, data: Any) -> dict[str, Any]:
        """
        Synchronous schema check on XW data (same shape as check()).
        Returns:
            Dict with 'valid' (bool), 'errors' (list[str])
        """
        is_valid, errors = self.validate_sync(data)
        return {'valid': is_valid, 'errors': errors or []}

    def validate_sync(self, data: Any) -> tuple[bool, list[str]]:
        """
        Synchronous wrapper for validate().
        Handles both cases:
        - When called from sync context: creates new event loop
        - When called from async context: uses direct synchronous validation to avoid loop conflicts
        Args:
            data: Data to validate
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            # Check if there's already a running event loop
            running_loop = asyncio.get_running_loop()
            # If we're in an async context, use synchronous validation directly
            # to avoid event loop conflicts
            validator = self._engine._ensure_validator()
            schema_dict = self.to_native()
            return validator.validate_schema(data, schema_dict)
        except RuntimeError:
            # No running loop - we're in a sync context, create a new loop
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
        Handles both cases:
        - When called from sync context: creates new event loop
        - When called from async context: uses direct synchronous validation to avoid loop conflicts
        Args:
            data: Data to validate
        Returns:
            List of dictionaries with 'node_path', 'issue_type', and 'message' keys
        """
        try:
            # Check if there's already a running event loop
            running_loop = asyncio.get_running_loop()
            # If we're in an async context, use synchronous validation directly
            # to avoid event loop conflicts
            validator = self._engine._ensure_validator()
            schema_dict = self.to_native()
            issues = validator.validate_schema_issues(data, schema_dict)
            return [
                {
                    'node_path': issue.node_path,
                    'issue_type': issue.issue_type,
                    'message': issue.message
                }
                for issue in issues
            ]
        except RuntimeError:
            # No running loop - we're in a sync context, create a new loop
            new_loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(new_loop)
                return new_loop.run_until_complete(self.validate_issues(data))
            finally:
                new_loop.close()
                asyncio.set_event_loop(None)
    # ==========================================================================
    # ISchemaProvider (xwsystem) – validate_schema, create_schema, validate_type, validate_range, validate_pattern
    # ==========================================================================

    def validate_schema(self, data: Any, schema: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate data against a schema (ISchemaProvider).
        Delegates to the engine's validator.
        """
        return self._engine._ensure_validator().validate_schema(data, schema)

    def create_schema(self, data: Any) -> dict[str, Any]:
        """
        Create schema from data (ISchemaProvider).
        Delegates to the engine's validator (generator).
        """
        return self._engine._ensure_validator().create_schema(data)

    def validate_type(self, data: Any, expected_type: str) -> bool:
        """Validate data type (ISchemaProvider). Delegates to engine's validator."""
        return self._engine._ensure_validator().validate_type(data, expected_type)

    def validate_range(self, data: Any, min_value: Any, max_value: Any) -> bool:
        """Validate data range (ISchemaProvider). Delegates to engine's validator."""
        return self._engine._ensure_validator().validate_range(data, min_value, max_value)

    def validate_pattern(self, data: str, pattern: str) -> bool:
        """Validate string pattern (ISchemaProvider). Delegates to engine's validator."""
        return self._engine._ensure_validator().validate_pattern(data, pattern)
    # ==========================================================================
    # SERIALIZATION
    # ==========================================================================

    def to_native(self) -> dict[str, Any]:
        """
        Get native Python dict representation of schema.
        Fully reuses XWData.to_native() for conversion.
        XWData provides format-agnostic conversion to native Python types.
        Returns:
            Schema definition as dict
        """
        return self._schema_data.to_native() if self._schema_data else self._schema_dict

    async def serialize(self, format: str | SchemaFormat, **opts) -> str | bytes:
        """Serialize schema. Uses xwsystem JsonSerializer for 'json'; else delegates to XWData.serialize."""
        fmt_str = self._schema_format_str(format)
        if fmt_str in ("json", "json-schema"):
            native = self.to_native()
            indent = opts.get("indent", 2)
            sort_keys = opts.get("sort_keys", False)
            result = _json_serializer.encode(
                native,
                options={"indent": indent, "sort_keys": sort_keys}
            )
            return result.decode("utf-8") if isinstance(result, bytes) else result
        return await self._schema_data.serialize(format=fmt_str, **opts)

    def _schema_format_str(self, format: str | SchemaFormat) -> str | None:
        """Map SchemaFormat to xwdata format string."""
        if not format:
            return None
        if isinstance(format, SchemaFormat):
            return format.name.lower().replace('_schema', '').replace('_', '-')
        return str(format).lower()

    def to_format(self, format: str | SchemaFormat, **opts) -> str | bytes:
        """Serialize schema to format (delegates to XWData.to_format())."""
        return self._schema_data.to_format(format=self._schema_format_str(format), **opts)

    def to_file(self, path: str | Path, format: str | SchemaFormat | None = None, **opts) -> XWSchema:
        """Save schema to file (delegates to XWData.to_file())."""
        self._schema_data.to_file(path, format=self._schema_format_str(format), **opts)
        return self

    async def save(self, path: str | Path, format: str | SchemaFormat | None = None, **opts) -> XWSchema:
        """Save schema to file (delegates to XWData.save; xwdata uses xwsystem for I/O)."""
        await self._schema_data.save(path, format=self._schema_format_str(format), **opts)
        return self

    async def reload(self, path: str | Path, format: str | SchemaFormat | None = None, **opts) -> XWSchema:
        """Reload schema from file (engine uses XWData.load)."""
        format_enum = format
        if isinstance(format, str) and format:
            try:
                format_enum = SchemaFormat[format.upper().replace("-", "_")]
            except KeyError:
                format_enum = None
        self._schema_dict = await self._engine.load_schema(Path(path), format_enum)
        self._schema_data = XWData.from_native(self._schema_dict)
        return self
    # ==========================================================================
    # SCHEMA ACCESS
    # ==========================================================================

    def __getitem__(self, key: str) -> Any:
        """
        Get schema property using bracket notation.
        Fully reuses XWData's path navigation if available.
        XWData provides efficient path-based access for schema properties.
        Args:
            key: Schema property path (e.g., 'properties.name.type')
        Returns:
            Schema property value
        Example:
            >>> schema['properties']['name']['type']  # 'string'
            >>> schema['properties.name.type']  # 'string' (if XWData supports path notation)
        """
        return self._schema_data[key]

    async def query(self, expression: str, format: str = 'sql', **opts) -> Any:
        """Query schema (delegates to XWData.query() via xwquery)."""
        return await self._schema_data.query(expression, format=format, **opts)

    def query_sync(self, expression: str, format: str = 'sql', **opts) -> Any:
        """
        Synchronous wrapper for query().
        Args:
            expression: Query expression
            format: Query format (default: 'sql')
            **opts: Additional query options
        Returns:
            Query result
        """
        new_loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(new_loop)
            return new_loop.run_until_complete(self.query(expression, format=format, **opts))
        finally:
            new_loop.close()
            asyncio.set_event_loop(None)

    def __repr__(self) -> str:
        """String representation."""
        format_name = self._format.name if self._format else 'unknown'
        return f"<XWSchema(format={format_name}, type={self._schema_dict.get('type', 'unknown')})>"
    # ==========================================================================
    # UTILITY METHODS - Extract and Load Properties/Parameters
    # ==========================================================================
    # Thread-safe cache for extraction to prevent deadlocks and improve performance
    _extraction_cache: dict[int, Any] = {}
    _extraction_cache_lock = threading.RLock()
    _extraction_in_progress: set[int] = set()  # Track objects currently being extracted
    _extraction_cache_max_size = 1024
    @staticmethod

    def _get_cache_key(obj: Any) -> int:
        """Generate cache key for object."""
        # Use object ID for caching
        return id(obj)
    @staticmethod

    def _clear_extraction_cache():
        """Clear the extraction cache (useful for testing)."""
        with XWSchema._extraction_cache_lock:
            XWSchema._extraction_cache.clear()
            XWSchema._extraction_in_progress.clear()
    @staticmethod

    def extract_properties(obj: Any) -> list[XWSchema]:
        """
        Extract all XWSchema property instances from an object (class or instance).
        Scans for properties decorated with @XWSchema by checking for
        the '_schema' and '_is_schema_decorated' attributes.
        Also finds @property decorated methods with type hints.
        Args:
            obj: Object (class or instance) to scan for schema properties
        Returns:
            List of XWSchema instances found on the object (one per property)
        Example:
            >>> class MyClass:
            ...     @XWSchema(type=str)
            ...     def name(self) -> str:
            ...         return self._name
            ...
            >>> schemas = XWSchema.extract_properties(MyClass)
            >>> len(schemas)
            1
        Uses caching to prevent deadlocks and improve performance.
        """
        cache_key = XWSchema._get_cache_key(obj)
        # Check cache first (deadlock breaker)
        with XWSchema._extraction_cache_lock:
            if cache_key in XWSchema._extraction_cache:
                cached = XWSchema._extraction_cache[cache_key]
                if isinstance(cached, list):
                    logger.debug(f"Cache hit for extract_properties: {obj.__name__ if inspect.isclass(obj) else obj.__class__.__name__}")
                    return cached.copy()  # Return copy to prevent mutation
            # Check if extraction is already in progress (deadlock breaker)
            if cache_key in XWSchema._extraction_in_progress:
                logger.warning(f"Circular extraction detected for {obj.__name__ if inspect.isclass(obj) else obj.__class__.__name__}, returning empty list")
                return []  # Return empty to break deadlock
            # Mark as in progress
            XWSchema._extraction_in_progress.add(cache_key)
        try:
            schemas: list[XWSchema] = []
            # Determine what to scan (class dict or instance dict)
            if inspect.isclass(obj):
                namespace = obj.__dict__
                annotations = getattr(obj, '__annotations__', {})
            else:
                # For instances, check both instance and class
                namespace = {}
                for k, v in vars(obj).items():
                    if hasattr(v, '_schema') or isinstance(v, property) or callable(v):
                        namespace[k] = v
                namespace.update({k: v for k, v in obj.__class__.__dict__.items()})
                annotations = getattr(obj.__class__, '__annotations__', {})
            for name, attr in namespace.items():
                # Skip private attributes (unless they have _schema)
                if name.startswith('_') and not hasattr(attr, '_schema'):
                    continue
                # Pattern 1: Check for @XWSchema decorated methods (has _schema and _is_schema_decorated)
                if hasattr(attr, '_schema') and hasattr(attr, '_is_schema_decorated'):
                    schema_obj = getattr(attr, '_schema')
                    if isinstance(schema_obj, XWSchema):
                        schemas.append(schema_obj)
                        logger.debug(f"Extracted @XWSchema property '{name}' from {obj.__name__ if inspect.isclass(obj) else obj.__class__.__name__}")
                # Pattern 2: Check if the attribute itself is an XWSchema (direct pattern)
                elif isinstance(attr, XWSchema):
                    schemas.append(attr)
                    logger.debug(f"Extracted direct XWSchema '{name}' from {obj.__name__ if inspect.isclass(obj) else obj.__class__.__name__}")
            # Cache the result
            with XWSchema._extraction_cache_lock:
                # Limit cache size
                if len(XWSchema._extraction_cache) >= XWSchema._extraction_cache_max_size:
                    # Remove oldest entry (FIFO)
                    oldest_key = next(iter(XWSchema._extraction_cache))
                    del XWSchema._extraction_cache[oldest_key]
                XWSchema._extraction_cache[cache_key] = schemas.copy()  # Store copy
                XWSchema._extraction_in_progress.remove(cache_key)
            return schemas
        except Exception as e:
            # Remove from in-progress on error
            with XWSchema._extraction_cache_lock:
                XWSchema._extraction_in_progress.discard(cache_key)
            logger.error(f"Error extracting properties from {obj.__name__ if inspect.isclass(obj) else obj.__class__.__name__}: {e}", exc_info=True)
            return []
    @staticmethod

    def load_properties(obj: Any, properties: list[XWSchema]) -> bool:
        """
        Load/attach XWSchema property instances to an object instance.
        Creates property getters/setters for each schema. Note that property
        names are inferred from the schema (if it has a name/alias) or must
        be provided via metadata.
        Args:
            obj: Object instance to attach properties to (must be an instance, not a class)
            properties: List of XWSchema instances to attach
        Returns:
            True if all properties were successfully attached, False otherwise
        Raises:
            ValueError: If obj is a class instead of an instance
        Note:
            This method creates simple property descriptors. For full property
            functionality with validation, consider using the @XWSchema decorator
            directly in class definitions.
        """
        import inspect
        if inspect.isclass(obj):
            raise ValueError("Cannot load properties onto a class. Use an instance instead.")
        if not properties:
            logger.warning(f"No properties provided to load onto {obj}")
            return True
        success_count = 0
        for i, schema in enumerate(properties):
            if not isinstance(schema, XWSchema):
                logger.warning(f"Skipping non-XWSchema object at index {i}: {type(schema)}")
                continue
            try:
                # Try to get property name from schema metadata or use index
                prop_name = None
                if hasattr(schema, '_metadata') and schema._metadata:
                    prop_name = schema._metadata.get('property_name')
                if not prop_name and hasattr(schema, 'alias') and schema.alias:
                    prop_name = schema.alias
                if not prop_name:
                    # Use a generated name
                    prop_name = f"_schema_property_{i}"
                    logger.warning(f"No property name found for schema at index {i}, using '{prop_name}'")
                # Create a simple property descriptor
                # Capture schema and prop_name in closure
                schema_instance = schema  # Capture for closure
                captured_prop_name = prop_name  # Capture for closure
                def getter(self_obj):
                    # Try to get value from instance storage
                    storage_attr = f"_{captured_prop_name}"
                    if hasattr(self_obj, storage_attr):
                        return getattr(self_obj, storage_attr)
                    return None
                def setter(self_obj, value):
                    # Validate if possible
                    if hasattr(schema_instance, 'validate_sync'):
                        is_valid, errors = schema_instance.validate_sync(value)
                        if not is_valid:
                            logger.warning(f"Validation failed for {captured_prop_name}: {errors}")
                    # Store in instance
                    storage_attr = f"_{captured_prop_name}"
                    setattr(self_obj, storage_attr, value)
                # Create property and attach to class
                prop = property(getter, setter)
                setattr(obj.__class__, prop_name, prop)
                logger.debug(f"Loaded property '{prop_name}' onto {obj.__class__.__name__} instance")
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to load property at index {i}: {e}", exc_info=True)
                continue
        all_success = success_count == len(properties)
        if not all_success:
            logger.warning(f"Only loaded {success_count}/{len(properties)} properties onto {obj.__class__.__name__}")
        return all_success
    @staticmethod

    def extract_parameters(func: Callable) -> tuple[list[XWSchema], list[XWSchema]]:
        """
        Extract parameter schemas from a function signature.
        Reuses extract_properties logic by treating the function as an object
        and extracting schemas from its signature. Uses caching to prevent deadlocks.
        Returns schemas for input parameters and return type as two separate lists.
        Input parameters are in the order they appear in the function signature
        (excluding 'self' and 'cls').
        Args:
            func: Function to extract parameters from
        Returns:
            Tuple of (in_list, out_list) where:
            - in_list: List of XWSchema for input parameters (ordered)
            - out_list: List of XWSchema for return type (typically one element)
        Example:
            >>> def my_func(x: int, y: str) -> bool:
            ...     return True
            ...
            >>> in_schemas, out_schemas = XWSchema.extract_parameters(my_func)
            >>> len(in_schemas)
            2
            >>> len(out_schemas)
            1
        """
        from typing import get_type_hints, get_origin, get_args, Any as TypingAny
        cache_key = XWSchema._get_cache_key(func)
        # Check cache first (deadlock breaker)
        with XWSchema._extraction_cache_lock:
            if cache_key in XWSchema._extraction_cache:
                # For functions, we need to return (in_list, out_list) tuple
                # Cache stores as list, but we need to reconstruct tuple
                cached = XWSchema._extraction_cache[cache_key]
                if isinstance(cached, tuple):
                    logger.debug(f"Cache hit for extract_parameters: {func.__name__}")
                    return cached  # Already a tuple
                # If it's a list, it's from extract_properties, need to convert
                logger.debug(f"Cache hit (properties) for extract_parameters: {func.__name__}, converting")
            # Check if extraction is already in progress (deadlock breaker)
            if cache_key in XWSchema._extraction_in_progress:
                logger.warning(f"Circular extraction detected for function {func.__name__}, returning empty lists")
                return ([], [])  # Return empty to break deadlock
            # Mark as in progress
            XWSchema._extraction_in_progress.add(cache_key)
        try:
            in_schemas: list[XWSchema] = []
            out_schemas: list[XWSchema] = []
            # Get function signature
            sig = inspect.signature(func)
            type_hints = get_type_hints(func, include_extras=True)
            # Extract input parameter schemas (excluding self/cls)
            # Reuse extract_properties logic by treating function parameters as properties
            for param_name, param in sig.parameters.items():
                if param_name in ('self', 'cls'):
                    continue
                # Get type annotation
                param_type = type_hints.get(param_name, TypingAny)
                # Determine if required (no default value)
                has_default = param.default is not inspect.Parameter.empty
                required = not has_default
                # Convert type to schema dict (reuse logic)
                schema_dict = XWSchema._type_to_schema_dict_static(param_type, required)
                # Create XWSchema (reusing property extraction pattern)
                schema = XWSchema(schema_dict)
                in_schemas.append(schema)
            # Extract return type schema
            return_type = type_hints.get('return', None)
            if return_type is not None:
                # Convert return type to schema dict
                schema_dict = XWSchema._type_to_schema_dict_static(return_type, required=True)
                schema = XWSchema(schema_dict)
                out_schemas.append(schema)
            result = (in_schemas, out_schemas)
            # Cache the result
            with XWSchema._extraction_cache_lock:
                # Limit cache size
                if len(XWSchema._extraction_cache) >= XWSchema._extraction_cache_max_size:
                    # Remove oldest entry (FIFO)
                    oldest_key = next(iter(XWSchema._extraction_cache))
                    del XWSchema._extraction_cache[oldest_key]
                XWSchema._extraction_cache[cache_key] = result
                XWSchema._extraction_in_progress.remove(cache_key)
            return result
        except Exception as e:
            # Remove from in-progress on error
            with XWSchema._extraction_cache_lock:
                XWSchema._extraction_in_progress.discard(cache_key)
            logger.error(f"Failed to extract parameters from {func.__name__}: {e}", exc_info=True)
            return ([], [])
    @staticmethod

    def load_parameters(func: Callable, parameters: dict[str, list[XWSchema]]) -> bool:
        """
        Load parameter schemas onto a function.
        Attaches schemas as function attributes. The parameters dict should have
        'in' and 'out' keys mapping to lists of XWSchema.
        Args:
            func: Function to attach schemas to
            parameters: Dictionary with 'in' and 'out' keys, each mapping to list of XWSchema
                - 'in': List of XWSchema for input parameters (ordered)
                - 'out': List of XWSchema for return type
        Returns:
            True if schemas were successfully attached, False otherwise
        Example:
            >>> def my_func(x: int, y: str) -> bool:
            ...     return True
            ...
            >>> schemas = {
            ...     'in': [XWSchema({'type': 'integer'}), XWSchema({'type': 'string'})],
            ...     'out': [XWSchema({'type': 'boolean'})]
            ... }
            >>> XWSchema.load_parameters(my_func, schemas)
            True
            >>> hasattr(my_func, '_in_schemas')
            True
        """
        try:
            in_schemas = parameters.get('in', [])
            out_schemas = parameters.get('out', [])
            # Validate inputs
            if not isinstance(in_schemas, list):
                logger.error("'in' parameter must be a list")
                return False
            if not isinstance(out_schemas, list):
                logger.error("'out' parameter must be a list")
                return False
            # Attach schemas as function attributes
            func._in_schemas = in_schemas
            func._out_schemas = out_schemas
            logger.debug(f"Loaded {len(in_schemas)} input and {len(out_schemas)} output schemas onto {func.__name__}")
            return True
        except Exception as e:
            logger.error(f"Failed to load parameters onto {func.__name__}: {e}", exc_info=True)
            return False
    @staticmethod

    def _type_to_schema_dict_static(param_type: Any, required: bool = True) -> dict[str, Any]:
        """
        Convert Python type annotation to XWSchema dictionary (static helper).
        This is a static version of the type conversion logic, extracted
        for use in utility functions.
        Args:
            param_type: Type annotation from function signature
            required: Whether the type is required
        Returns:
            Schema dictionary compatible with XWSchema
        """
        from typing import get_origin, get_args, Any as TypingAny
        schema: dict[str, Any] = {}
        # Handle None type
        if param_type is None or param_type is type(None):
            schema["type"] = "null"
            return schema
        # Handle generic types (List, Dict, Union, Optional, etc.)
        origin = getattr(param_type, '__origin__', None)
        args = getattr(param_type, '__args__', None)
        # Check origin name
        origin_name = None
        if hasattr(origin, '__name__'):
            origin_name = origin.__name__
        elif hasattr(origin, '__qualname__'):
            origin_name = origin.__qualname__.split('.')[-1]
        if origin is not None and origin_name:
            # Handle list[T] or list[T]
            if origin_name in ('list', 'List'):
                schema["type"] = "array"
                if args and len(args) > 0:
                    item_type = args[0]
                    schema["items"] = XWSchema._type_to_schema_dict_static(item_type, required=True)
                else:
                    schema["items"] = {}
            # Handle dict[K, V] or dict[K, V]
            elif origin_name in ('dict', 'Dict'):
                schema["type"] = "object"
            # Handle Union/Optional
            elif origin_name in ('Union', 'Optional'):
                non_none_args = [arg for arg in args if arg is not type(None)] if args else []
                if non_none_args:
                    # Use first non-None type
                    schema = XWSchema._type_to_schema_dict_static(non_none_args[0], required)
        # Handle simple types
        if "type" not in schema:
            type_mapping = {
                str: "string",
                int: "integer",
                float: "number",
                bool: "boolean",
                list: "array",
                dict: "object",
                tuple: "array",
                set: "array",
            }
            if param_type in type_mapping:
                schema["type"] = type_mapping[param_type]
            elif hasattr(param_type, '__name__'):
                # Use type name as fallback
                schema["type"] = param_type.__name__.lower()
            else:
                schema["type"] = "object"
        return schema
    # ============================================================================
    # XWObject Implementation
    # ============================================================================
    @property

    def id(self) -> str:
        """Semantic id (e.g. schema $id); distinct from uid."""
        return self._id if self._id is not None else ""
    @property

    def created_at(self) -> datetime:
        """Get the creation timestamp."""
        return self._created_at
    @property

    def updated_at(self) -> datetime:
        """Get the last update timestamp."""
        return self._updated_at

    def to_dict(self) -> dict[str, Any]:
        """
        Export schema as dictionary.
        Includes XWObject fields (id, uid, created_at, updated_at, title, description)
        and schema-specific data.
        """
        result = {
            "id": self.id,
            "uid": self.uid,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "schema": self.to_native(),
            "format": self._format.name if self._format else None,
        }
        if self.title:
            result["title"] = self.title
        if self.description:
            result["description"] = self.description
        if self._metadata:
            result["metadata"] = self._metadata
        return result

    def save_metadata(self, *args, **kwargs) -> None:
        """
        Save schema metadata to storage (placeholder).
        For saving schema definition to file, use await schema.save(path, format).
        """
        self._updated_at = datetime.now()
        logger.debug(f"Saving schema metadata: {self.uid}")

    def load_metadata(self, *args, **kwargs) -> None:
        """
        Load schema metadata from storage (placeholder).
        For loading schema from file, use await XWSchema.load(path).
        """
        logger.debug(f"Loading schema metadata: {self.uid}")
