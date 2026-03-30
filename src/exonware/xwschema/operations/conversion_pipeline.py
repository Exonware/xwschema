#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/operations/conversion_pipeline.py
Schema Conversion Pipeline (Optional BaaS Feature)
Provides multi-step schema conversion pipelines for complex conversion workflows.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.4
Generation Date: 26-Jan-2026
NOTE: This is an OPTIONAL module for BaaS platform integration.
"""

from __future__ import annotations
from typing import Any
from pathlib import Path
from exonware.xwsystem import get_logger
from ..contracts import IConversionPipeline, ISchemaFormatConverter
from ..defs import SchemaFormat
from ..errors import XWSchemaError, XWSchemaFormatError
from .format_conversion import SchemaFormatConverter
logger = get_logger(__name__)


class ConversionPipeline(IConversionPipeline):
    """
    Multi-step schema conversion pipeline.
    Provides support for complex schema conversion workflows with multiple steps.
    This is an optional BaaS feature.
    """

    def __init__(self, converter: ISchemaFormatConverter | None = None):
        """
        Initialize conversion pipeline.
        Args:
            converter: Optional schema format converter (creates default if not provided)
        """
        self._converter = converter or SchemaFormatConverter()
        self._steps: list[tuple[SchemaFormat, bool]] = []  # (format, optimize) tuples

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
        # Build conversion path
        if intermediate_formats:
            path = [from_format] + intermediate_formats + [to_format]
        else:
            # Use converter's optimal path
            path = self._converter.get_conversion_path(from_format, to_format)
        # Remove duplicates and optimize
        optimized_path = []
        prev_format = None
        for fmt in path:
            if fmt != prev_format:
                optimized_path.append(fmt)
                prev_format = fmt
        # Execute conversions step by step
        current_schema = schema
        for i in range(len(optimized_path) - 1):
            source_format = optimized_path[i]
            target_format = optimized_path[i + 1]
            current_schema = await self._converter.convert(
                current_schema,
                source_format,
                target_format,
                **opts
            )
            logger.debug(f"Pipeline step {i+1}/{len(optimized_path)-1}: {source_format.name} → {target_format.name}")
        return current_schema

    def add_step(self, step_format: SchemaFormat, optimize: bool = False) -> ConversionPipeline:
        """
        Add conversion step to pipeline.
        Args:
            step_format: Intermediate format for this step
            optimize: Whether to optimize at this step
        Returns:
            Self for chaining
        """
        self._steps.append((step_format, optimize))
        return self

    def clear_steps(self) -> ConversionPipeline:
        """
        Clear all pipeline steps.
        Returns:
            Self for chaining
        """
        self._steps.clear()
        return self
__all__ = ['ConversionPipeline']
