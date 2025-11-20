"""
XData Schema Module

Comprehensive schema operations including validation, generation, and management.
Provides schema processing capabilities for various formats.
"""

from .facade import xSchema
from .model import (
    ASchemaNode,
    SchemaProcessor,
    SchemaValidator,
    SchemaGenerator,
    SchemaParser,
    SchemaVersionManager,
    SchemaReferenceResolver
)
from ..core.errors import (
    XSchemaError,
    XSchemaValidationError,
    XSchemaGenerationError,
    XSchemaParsingError,
    XSchemaVersionError,
    XSchemaCompatibilityError,
    XSchemaReferenceError
)

__all__ = [
    # Main xSchema class
    'xSchema',
    
    # Schema processing components
    'ASchemaNode',
    'SchemaProcessor',
    'SchemaValidator',
    'SchemaGenerator',
    'SchemaParser',
    'SchemaVersionManager',
    'SchemaReferenceResolver',
    
    # Error classes
    'XSchemaError',
    'XSchemaValidationError',
    'XSchemaGenerationError',
    'XSchemaParsingError',
    'XSchemaVersionError',
    'XSchemaCompatibilityError',
    'XSchemaReferenceError'
]

# Module metadata
__version__ = "1.0.0"
__author__ = "xComBot Development Team"
__description__ = "Comprehensive schema operations and validation for XData" 