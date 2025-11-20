"""
xSchema new Core Errors

Error classes for xSchema new implementation.
"""


class XSchemaError(Exception):
    """Base exception for xSchema errors."""
    pass


class XSchemaValidationError(XSchemaError):
    """Exception raised for schema validation errors."""
    pass


class XSchemaGenerationError(XSchemaError):
    """Exception raised for schema generation errors."""
    pass


class XSchemaParsingError(XSchemaError):
    """Exception raised for schema parsing errors."""
    pass


class XSchemaVersionError(XSchemaError):
    """Exception raised for schema version errors."""
    pass


class XSchemaCompatibilityError(XSchemaError):
    """Exception raised for schema compatibility errors."""
    pass


class XSchemaReferenceError(XSchemaError):
    """Exception raised for schema reference errors."""
    pass
