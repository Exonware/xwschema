#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/contracts.py
XWSchema Interfaces and Contracts
This module defines all interfaces for the xwschema library following
GUIDELINES_DEV.md standards. All interfaces use 'I' prefix.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.10
Generation Date: 09-Nov-2025
"""

from __future__ import annotations
from typing import Any, Protocol, runtime_checkable
from pathlib import Path
from exonware.xwsystem.shared import IObject
# ISchema extends IData so schema is a valid IData node (sub-node in XWEntity/XWData).
from exonware.xwdata.contracts import IData
# ISchema extends ISchemaProvider (xwsystem) so schema is also the concrete schema provider.
from exonware.xwsystem.validation.contracts import ISchemaProvider
# Import enums from defs
from .defs import SchemaFormat, ValidationMode, SchemaGenerationMode
# ==============================================================================
# CORE SCHEMA INTERFACE
# ==============================================================================
@runtime_checkable

class ISchema(IData, IObject, ISchemaProvider, Protocol):
    """
    Core interface for all XWSchema instances.
    Extends IData (xwdata), IObject (xwsystem), and ISchemaProvider (xwsystem).
    Implementations are both schema documents and schema validation providers.
    Follows GUIDELINES_DEV.md: ISchema (interface) → ASchema (abstract) → XWSchema (concrete).
    From IData: schema as sub-node in XWData; delegate to _data (XWData).
    From ISchemaProvider: validate_schema(data, schema), create_schema(data), validate_type, validate_range, validate_pattern.
    """

    async def validate(self, data: Any) -> tuple[bool, list[str]]:
        """
        Validate data against this schema.
        Args:
            data: Data to validate (can be dict, list, or XWData instance)
        Returns:
            Tuple of (is_valid, error_messages)
        """
        ...

    def to_native(self) -> dict[str, Any]:
        """Get native Python dict representation of schema."""
        ...

    async def serialize(self, format: str | SchemaFormat, **opts) -> str | bytes:
        """Serialize schema to specified format."""
        ...

    async def save(self, path: str | Path, format: str | SchemaFormat | None = None, **opts) -> ISchema:
        """Save schema to file (returns self for chaining)."""
        ...

    async def load(self, path: str | Path, format: str | SchemaFormat | None = None, **opts) -> ISchema:
        """Load schema from file (returns self for chaining)."""
        ...

    def get_format(self) -> str | None:
        """Get schema format information."""
        ...

    def get_metadata(self) -> dict[str, Any]:
        """Get schema metadata dictionary."""
        ...
# ==============================================================================
# SCHEMA ENGINE INTERFACE
# ==============================================================================
@runtime_checkable

class ISchemaEngine(Protocol):
    """
    Interface for schema processing engine.
    Orchestrates schema validation, generation, and format conversion.
    """

    async def validate_data(self, data: Any, schema: dict[str, Any], mode: ValidationMode = ValidationMode.STRICT) -> tuple[bool, list[str]]:
        """Validate data against schema."""
        ...

    async def generate_schema(self, data: Any, mode: SchemaGenerationMode = SchemaGenerationMode.INFER) -> dict[str, Any]:
        """Generate schema from data."""
        ...

    async def convert_schema(self, schema: dict[str, Any], from_format: SchemaFormat, to_format: SchemaFormat) -> dict[str, Any]:
        """Convert schema between formats."""
        ...

    async def load_schema(self, path: Path, format: SchemaFormat | None = None) -> dict[str, Any]:
        """Load schema from file."""
        ...

    async def save_schema(self, schema: dict[str, Any], path: Path, format: SchemaFormat) -> None:
        """Save schema to file."""
        ...
# ==============================================================================
# SCHEMA GENERATOR INTERFACE
# ==============================================================================
@runtime_checkable

class ISchemaGenerator(Protocol):
    """Interface for schema generation operations."""

    async def generate_from_data(self, data: Any, mode: SchemaGenerationMode = SchemaGenerationMode.INFER) -> dict[str, Any]:
        """Generate schema from data."""
        ...

    async def generate_from_xwdata(self, data: Any, mode: SchemaGenerationMode = SchemaGenerationMode.INFER) -> dict[str, Any]:
        """Generate schema from XWData instance."""
        ...

    def infer_type(self, value: Any) -> str:
        """Infer JSON Schema type from Python value."""
        ...
# ==============================================================================
# STRATEGY INTERFACES (Option 5: composition)
# ==============================================================================
# Type aliases for strategy composition; implementations are internal (Default*).
IValidationStrategy = ISchemaProvider  # from xwsystem
IGenerationStrategy = ISchemaGenerator
# ==============================================================================
# BaaS OPTIONAL FEATURES - Format Conversion Interfaces (OPTIONAL)
# ==============================================================================
@runtime_checkable

class ISchemaFormatConverter(Protocol):
    """
    Optional interface for advanced schema format conversion.
    Provides enhanced format conversion capabilities beyond the basic
    convert_schema method in ISchemaEngine. This is an OPTIONAL feature
    for BaaS platform integration.
    """

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
        ...

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
        ...
@runtime_checkable

class IConversionPipeline(Protocol):
    """
    Optional interface for multi-step schema conversion pipelines.
    Allows chaining multiple format conversions with intermediate
    optimizations. This is an OPTIONAL feature for BaaS platform.
    """

    async def execute(
        self,
        schema: dict[str, Any],
        from_format: SchemaFormat,
        to_format: SchemaFormat,
        intermediate_formats: list[SchemaFormat] | None = None,
        **opts
    ) -> dict[str, Any]:
        """
        Execute multi-step conversion pipeline.
        Args:
            schema: Schema definition to convert
            from_format: Source schema format
            to_format: Target schema format
            intermediate_formats: Optional intermediate formats for conversion path
            **opts: Additional pipeline options
        Returns:
            Converted schema definition
        """
        ...

    def add_step(self, step_format: SchemaFormat, optimize: bool = False) -> IConversionPipeline:
        """
        Add conversion step to pipeline.
        Args:
            step_format: Intermediate format for this step
            optimize: Whether to optimize at this step
        Returns:
            Self for chaining
        """
        ...
