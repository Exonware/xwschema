#!/usr/bin/env python3
#exonware/xwschema/src/exonware/xwschema/formats/__init__.py
"""
Schema formats and registry support.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.4
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
