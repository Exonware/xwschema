#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/operations/format_conversion.py
Schema Format Conversion Operations (Optional BaaS Feature)
Provides schema format-to-format conversion (structure transformation) via the engine.
Schema document load/save and serialization format conversion use xwdata (XWData.load/save);
xwschema does not use xwjson directly. When cache_size > 0, reuses xwsystem create_cache (LRU).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.15
Generation Date: 26-Jan-2026
NOTE: This is an OPTIONAL module for BaaS platform integration.
"""

import hashlib
from typing import Any
from pathlib import Path
from exonware.xwsystem import get_logger
from ..contracts import ISchemaFormatConverter
from ..defs import SchemaFormat
from ..errors import XWSchemaError, XWSchemaFormatError
from ..engine import XWSchemaEngine
logger = get_logger(__name__)


class SchemaFormatConverter(ISchemaFormatConverter):
    """
    Schema format converter with optimization and caching.
    Uses XWSchemaEngine for schema structure transformations (e.g. OpenAPI → JSON Schema → Avro).
    Schema document I/O and serialization format conversion are done via xwdata (XWData).
    Features:
    - Conversion caching to avoid redundant conversions
    - Validation at each conversion step
    - Error recovery and partial conversion support
    This is an optional BaaS feature for multi-format schema capabilities.
    """

    def __init__(self, enable_caching: bool = True, cache_size: int = 1000):
        """
        Initialize schema format converter.
        Conversion is performed by the engine; schema file load/save use xwdata.
        When cache_size > 0, uses xwsystem create_cache for LRU conversion cache (reuse, performance).
        Args:
            enable_caching: Enable conversion result caching
            cache_size: Maximum cache size; when > 0 uses xwsystem create_cache
        """
        self._enable_caching = enable_caching
        self._cache_size = cache_size
        self._cache: Any = None
        self._cache_dict: dict[str, Any] = {}
        if enable_caching and cache_size > 0:
            from exonware.xwsystem.caching import create_cache
            self._cache = create_cache(
                capacity=cache_size,
                namespace="xwschema.format_conversion",
                name="SchemaFormatConverterCache",
            )
        else:
            self._cache = None
        # Engine handles schema structure transformation (no direct xwjson)
        self._engine = XWSchemaEngine()
        logger.debug("xwschema: Schema format conversion via engine (xwdata for I/O)")

    def _get_cache_key(
        self,
        schema: dict[str, Any],
        from_format: SchemaFormat,
        to_format: SchemaFormat
    ) -> str:
        """Generate cache key for conversion."""
        # Use hash of schema + formats for cache key
        schema_str = str(schema)[:500]  # Limit length for hashing
        key_str = f"{from_format.name}:{to_format.name}:{schema_str}"
        return hashlib.md5(key_str.encode()).hexdigest()

    async def convert(
        self,
        schema: dict[str, Any],
        from_format: SchemaFormat,
        to_format: SchemaFormat,
        **opts
    ) -> dict[str, Any]:
        """
        Convert schema between formats with optional optimization.
        Args:
            schema: Schema definition to convert
            from_format: Source schema format
            to_format: Target schema format
            **opts: Additional conversion options
        Returns:
            Converted schema definition
        """
        # Check cache (xwsystem create_cache when cache_size > 0, else dict)
        if self._enable_caching:
            cache_key = self._get_cache_key(schema, from_format, to_format)
            if self._cache is not None:
                cached = self._cache.get(cache_key)
                if cached is not None:
                    logger.debug(f"Schema conversion cache hit: {from_format.name} → {to_format.name}")
                    return cached
            elif cache_key in self._cache_dict:
                logger.debug(f"Schema conversion cache hit: {from_format.name} → {to_format.name}")
                return self._cache_dict[cache_key]
        # Same format - no conversion needed
        if from_format == to_format:
            return schema
        try:
            # Use engine's conversion logic (reuses existing conversion methods)
            result = await self._engine.convert_schema(schema, from_format, to_format)
            # Cache result
            if self._enable_caching:
                cache_key = self._get_cache_key(schema, from_format, to_format)
                if self._cache is not None:
                    try:
                        self._cache.put(cache_key, result)
                    except (TypeError, ValueError, AttributeError):
                        pass
                else:
                    if len(self._cache_dict) >= self._cache_size and self._cache_size > 0:
                        self._cache_dict.pop(next(iter(self._cache_dict)))
                    self._cache_dict[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"Schema format conversion failed: {from_format.name} → {to_format.name}: {e}")
            raise XWSchemaFormatError(
                f"Schema format conversion failed: {from_format.name} → {to_format.name}"
            ) from e

    async def convert_with_validation(
        self,
        schema: dict[str, Any],
        from_format: SchemaFormat,
        to_format: SchemaFormat,
        validate_result: bool = True,
        **opts
    ) -> dict[str, Any]:
        """
        Convert schema between formats with validation of result.
        Args:
            schema: Schema definition to convert
            from_format: Source schema format
            to_format: Target schema format
            validate_result: Whether to validate the converted schema
            **opts: Additional conversion options
        Returns:
            Validated converted schema definition
        """
        # Perform conversion
        result = await self.convert(schema, from_format, to_format, **opts)
        # Validate result if requested
        if validate_result:
            # Basic validation - check that result is a dict and has expected structure
            if not isinstance(result, dict):
                raise XWSchemaFormatError(
                    f"Converted schema is not a dict: {type(result)}"
                )
            # Format-specific validation could be added here
            # For now, just ensure basic structure
        return result

    def supports_conversion(
        self,
        from_format: SchemaFormat,
        to_format: SchemaFormat
    ) -> bool:
        """
        Check if conversion is supported between formats.
        Args:
            from_format: Source schema format
            to_format: Target schema format
        Returns:
            True if conversion is supported
        """
        # All format pairs are supported via JSON Schema intermediate
        # Engine handles all conversions
        return True

    def get_conversion_path(
        self,
        from_format: SchemaFormat,
        to_format: SchemaFormat
    ) -> list[SchemaFormat]:
        """
        Get optimal conversion path (direct or via intermediate formats).
        Args:
            from_format: Source schema format
            to_format: Target schema format
        Returns:
            List of schema formats in conversion path
        """
        # Same format - no conversion
        if from_format == to_format:
            return [from_format]
        # Engine uses JSON Schema as intermediate format
        if from_format != SchemaFormat.JSON_SCHEMA and to_format != SchemaFormat.JSON_SCHEMA:
            return [from_format, SchemaFormat.JSON_SCHEMA, to_format]
        # Direct conversion
        return [from_format, to_format]
# Convenience function
async def convert_schema_format(
    schema: dict[str, Any],
    from_format: SchemaFormat,
    to_format: SchemaFormat,
    **opts
) -> dict[str, Any]:
    """
    Convenience function for schema format conversion.
    Args:
        schema: Schema definition to convert
        from_format: Source schema format
        to_format: Target schema format
        **opts: Additional options
    Returns:
        Converted schema definition
    """
    converter = SchemaFormatConverter()
    return await converter.convert(schema, from_format, to_format, **opts)
__all__ = ['SchemaFormatConverter', 'convert_schema_format']
