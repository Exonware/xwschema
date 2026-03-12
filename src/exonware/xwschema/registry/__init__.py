#!/usr/bin/env python3
#exonware/xwschema/src/exonware/xwschema/registry/__init__.py
"""
Schema registry integration.
Provides enterprise schema registry support for:
- AWS Glue Schema Registry
- Confluent Schema Registry
- Schema evolution and compatibility checking
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
"""

from .schema_registry import (
    SchemaInfo,
    ConfluentSchemaRegistry,
    AwsGlueSchemaRegistry,
    SchemaRegistry,
)
from .base import ASchemaRegistry
from .defs import CompatibilityLevel
from .errors import SchemaRegistryError, SchemaNotFoundError, SchemaValidationError
from .catalog import (
    SchemaCatalog,
    SchemaCatalogEntry,
    apply_migration,
    diff_schema_definitions,
)
__all__ = [
    'SchemaInfo',
    'ASchemaRegistry',
    'ConfluentSchemaRegistry',
    'AwsGlueSchemaRegistry',
    'SchemaRegistry',
    'CompatibilityLevel',
    'SchemaRegistryError',
    'SchemaNotFoundError',
    'SchemaValidationError',
    'SchemaCatalog',
    'SchemaCatalogEntry',
    'apply_migration',
    'diff_schema_definitions',
]
