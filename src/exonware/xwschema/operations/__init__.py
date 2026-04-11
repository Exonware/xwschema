#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/operations/__init__.py
XWSchema Operations Module
This module contains optional BaaS platform operations for schema format conversion,
validation pipelines, and advanced schema transformations.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.11
Generation Date: 26-Jan-2026
NOTE: This is an OPTIONAL module for BaaS platform integration.
All features in this module are optional and do not break existing functionality.
Schema format conversion uses the engine; schema I/O uses xwdata (no direct xwjson).
"""

from .format_conversion import SchemaFormatConverter, convert_schema_format
from .conversion_pipeline import ConversionPipeline
from .schema_transformer import SchemaTransformer
from .validation_pipeline import ValidationPipeline, PipelineStage, ValidationResult
__all__ = [
    'SchemaFormatConverter',
    'convert_schema_format',
    'ConversionPipeline',
    'SchemaTransformer',
    'ValidationPipeline',
    'PipelineStage',
    'ValidationResult',
]
