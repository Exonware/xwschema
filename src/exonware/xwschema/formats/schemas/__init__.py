#!/usr/bin/env python3
#exonware/xwschema/src/exonware/xwschema/formats/schemas/__init__.py
"""
Schema registry integration.

Provides enterprise schema registry support for:
- AWS Glue Schema Registry
- Confluent Schema Registry
- Schema evolution and compatibility checking

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
"""

from .schema_registry import (
    SchemaInfo,
    ConfluentSchemaRegistry,
    AWSGlueSchemaRegistry,
)

__all__ = [
    'SchemaInfo',
    'ConfluentSchemaRegistry',
    'AWSGlueSchemaRegistry',
]

