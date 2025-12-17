#!/usr/bin/env python3
#exonware/xwschema/src/exonware/xwschema/formats/__init__.py
"""
Schema formats and registry support.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

# Abstract base for all schema serializers
from .base import (
    ASchemaSerialization,
    SchemaPrimitiveType,
    SchemaComplexType,
    SchemaTypeMapper,
    SchemaPropertyMapper,
)

# Schema format serializers (extend ASchemaSerialization)
from . import schema
from .schema import (
    JsonSchemaSerializer,
    AvroSchemaSerializer,
    OpenApiSchemaSerializer,
    ProtobufSchemaSerializer,
    GraphQLSchemaSerializer,
    XsdSchemaSerializer,
    WsdlSchemaSerializer,
    SwaggerSchemaSerializer,
)

__all__ = [
    # Abstract base
    'ASchemaSerialization',
    'SchemaPrimitiveType',
    'SchemaComplexType',
    'SchemaTypeMapper',
    'SchemaPropertyMapper',
    # Schema format module
    'schema',
    # Serializers
    'JsonSchemaSerializer',
    'AvroSchemaSerializer',
    'OpenApiSchemaSerializer',
    'ProtobufSchemaSerializer',
    'GraphQLSchemaSerializer',
    'XsdSchemaSerializer',
    'WsdlSchemaSerializer',
    'SwaggerSchemaSerializer',
]
