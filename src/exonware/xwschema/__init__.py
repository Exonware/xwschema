"""
xwschema: Schema validation and data structure definition library

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

# Public API
from .facade import XWSchema
from .defs import SchemaFormat, ValidationMode, SchemaGenerationMode, ConstraintType
from .config import XWSchemaConfig, ValidationConfig, GenerationConfig, PerformanceConfig
from .builder import XWSchemaBuilder
from .validator import ValidationIssue
from .errors import (
    XWSchemaError,
    XWSchemaValidationError,
    XWSchemaTypeError,
    XWSchemaConstraintError,
    XWSchemaParseError,
    XWSchemaFormatError,
    XWSchemaReferenceError,
    XWSchemaGenerationError
)

__version__ = "0.0.1.1"
__author__ = "Eng. Muhammad AlShehri"
__email__ = "connect@exonware.com"
__company__ = "eXonware.com"

__all__ = [
    # Main API
    'XWSchema',
    'XWSchemaBuilder',
    'ValidationIssue',
    
    # Enums
    'SchemaFormat',
    'ValidationMode',
    'SchemaGenerationMode',
    'ConstraintType',
    
    # Configuration
    'XWSchemaConfig',
    'ValidationConfig',
    'GenerationConfig',
    'PerformanceConfig',
    
    # Errors
    'XWSchemaError',
    'XWSchemaValidationError',
    'XWSchemaTypeError',
    'XWSchemaConstraintError',
    'XWSchemaParseError',
    'XWSchemaFormatError',
    'XWSchemaReferenceError',
    'XWSchemaGenerationError',
]
