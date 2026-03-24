"""
xwschema: Schema validation and data structure definition library
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.3
Generation Date: 09-Nov-2025
"""
# xwdata, xwsystem, xwquery are required; no fallbacks
# Public API

from .facade import XWSchema
from .defs import SchemaFormat, ValidationMode, SchemaGenerationMode, ConstraintType
from .config import XWSchemaConfig, ValidationConfig, GenerationConfig, PerformanceConfig
from .builder import XWSchemaBuilder
from .validator import ValidationIssue
from .type_utils import class_to_string, string_to_class, normalize_type, normalize_schema_dict
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
from .version import __version__
__author__ = "eXonware Backend Team"
__email__ = "connect@exonware.com"
__company__ = "eXonware.com"
# Note: extract_properties, load_properties, extract_parameters, load_parameters
# are static methods on XWSchema class, accessible as XWSchema.extract_properties() etc.
# They are not exported here as separate functions to avoid confusion.
__all__ = [
    # Main API
    'XWSchema',
    'XWSchemaBuilder',
    'ValidationIssue',
    # Type Utilities
    'class_to_string',
    'string_to_class',
    'normalize_type',
    'normalize_schema_dict',
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
