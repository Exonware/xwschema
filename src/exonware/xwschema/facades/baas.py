#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/facades/baas.py
BaaS Facade for XWSchema (Optional BaaS Features)
Provides convenience methods for BaaS schema operations.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.16
Generation Date: 26-Jan-2026
NOTE: This is an OPTIONAL module for BaaS platform integration.
"""

from typing import Any
from pathlib import Path
from exonware.xwsystem import get_logger
from ..facade import XWSchema
from ..defs import SchemaFormat, ValidationMode
from ..operations.format_conversion import SchemaFormatConverter, convert_schema_format
from ..operations.conversion_pipeline import ConversionPipeline
from ..operations.validation_pipeline import ValidationPipeline
from ..errors import XWSchemaError
logger = get_logger(__name__)


class XWSchemaBaaSFacade:
    """
    BaaS facade for xwschema core capabilities.
    Provides:
    - Schema format conversion (via engine; schema I/O via xwdata)
    - Validation pipelines
    API/entity/storage/auth schema integration lives in domain packages:
    - xwapi.schema, xwauth.schema, xwentity.schema, xwstorage.schema
    Required dependencies: xwsystem, xwdata
    """

    def __init__(self):
        """Initialize BaaS facade."""
        # Core operations (always available)
        self._converter = SchemaFormatConverter()
        self._conversion_pipeline = ConversionPipeline(self._converter)
        self._validation_pipeline = ValidationPipeline()
        logger.debug("XWSchemaBaaSFacade initialized")
    # ============================================================================
    # SCHEMA FORMAT CONVERSION (Always Available - via engine / xwdata)
    # ============================================================================

    async def convert_schema_format(
        self,
        schema: dict[str, Any],
        from_format: SchemaFormat,
        to_format: SchemaFormat,
        **opts
    ) -> dict[str, Any]:
        """
        Convert schema from source format to target format.
        Uses engine for structure transformation; schema I/O uses xwdata.
        Args:
            schema: Schema definition to convert
            from_format: Source schema format
            to_format: Target schema format
            **opts: Additional conversion options
        Returns:
            Converted schema definition
        """
        return await self._converter.convert(schema, from_format, to_format, **opts)

    async def convert_schema_with_pipeline(
        self,
        schema: dict[str, Any],
        from_format: SchemaFormat,
        to_format: SchemaFormat,
        intermediate_formats: list[SchemaFormat] | None = None,
        **opts
    ) -> dict[str, Any]:
        """
        Convert schema using multi-step pipeline.
        Args:
            schema: Schema definition to convert
            from_format: Source schema format
            to_format: Target schema format
            intermediate_formats: Optional intermediate formats
            **opts: Additional pipeline options
        Returns:
            Converted schema definition
        """
        return await self._conversion_pipeline.execute(
            schema, from_format, to_format, intermediate_formats, **opts
        )
    # ============================================================================
    # VALIDATION PIPELINES
    # ============================================================================

    def create_validation_pipeline(self, name: str | None = None) -> ValidationPipeline:
        """
        Create a new validation pipeline.
        Args:
            name: Optional pipeline name
        Returns:
            ValidationPipeline instance
        """
        return ValidationPipeline(name=name)

    async def validate_with_pipeline(
        self,
        data: Any,
        schema: dict[str, Any],
        pipeline: ValidationPipeline,
        **opts
    ) -> dict[str, Any]:
        """
        Validate data using validation pipeline.
        Args:
            data: Data to validate
            schema: Schema definition
            pipeline: ValidationPipeline instance
            **opts: Additional validation options
        Returns:
            Validation result dictionary
        """
        from ..operations.validation_pipeline import ValidationResult
        result = await pipeline.validate(data, schema, **opts)
        return {
            'valid': result.is_valid,
            'errors': result.errors,
            'warnings': result.warnings,
            'metadata': result.metadata
        }
__all__ = ['XWSchemaBaaSFacade']
