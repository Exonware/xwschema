#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/registry/errors.py

Schema Registry Error Classes

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""


class SchemaRegistryError(Exception):
    """Base exception for schema registry errors."""
    pass


class SchemaNotFoundError(SchemaRegistryError):
    """Raised when schema is not found in registry."""
    pass


class SchemaValidationError(SchemaRegistryError):
    """Raised when schema validation fails."""
    pass
