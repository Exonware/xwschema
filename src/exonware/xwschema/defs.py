#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/defs.py

XWSchema Types and Enums

This module defines all the enums and types for the XWSchema system:
- SchemaFormat: Supported schema formats (JSON Schema, Avro, Protobuf, OpenAPI, etc.)
- ValidationMode: Validation operation modes
- SchemaGenerationMode: Schema generation strategies

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from enum import Enum, Flag, auto as _auto
from typing import Any, Optional


# ==============================================================================
# SCHEMA FORMATS
# ==============================================================================

class SchemaFormat(Enum):
    """Supported schema formats."""
    
    # Standard schema formats
    JSON_SCHEMA = _auto()      # JSON Schema (Draft 7, 2019-09, 2020-12)
    AVRO = _auto()             # Apache Avro schema
    PROTOBUF = _auto()         # Protocol Buffers schema (.proto)
    OPENAPI = _auto()          # OpenAPI 3.0/3.1 schema
    SWAGGER = _auto()          # Swagger 2.0 schema (legacy)
    GRAPHQL = _auto()          # GraphQL schema
    WSDL = _auto()             # WSDL schema (XML)
    XSD = _auto()              # XML Schema Definition
    
    # Data format schemas
    PARQUET = _auto()          # Parquet schema
    ORC = _auto()              # ORC schema
    THRIFT = _auto()           # Apache Thrift IDL
    
    # Special modes
    AUTO = _auto()             # Auto-detect schema format


# ==============================================================================
# VALIDATION MODES
# ==============================================================================

class ValidationMode(Enum):
    """Validation operation modes."""
    
    STRICT = _auto()           # Strict validation (all constraints enforced)
    LAX = _auto()              # Lax validation (warnings only)
    FAST = _auto()             # Fast validation (skip expensive checks)
    DETAILED = _auto()         # Detailed validation (full error reporting)


# ==============================================================================
# SCHEMA GENERATION MODES
# ==============================================================================

class SchemaGenerationMode(Enum):
    """Schema generation strategies."""
    
    INFER = _auto()            # Infer schema from data structure
    STRICT = _auto()           # Generate strict schema (all constraints)
    MINIMAL = _auto()          # Generate minimal schema (types only)
    COMPREHENSIVE = _auto()    # Generate comprehensive schema (with examples, descriptions)


# ==============================================================================
# CONSTRAINT TYPES
# ==============================================================================

class ConstraintType(Enum):
    """Types of schema constraints."""
    
    TYPE = _auto()             # Type constraint
    ENUM = _auto()             # Enum constraint
    PATTERN = _auto()          # Pattern constraint (regex)
    RANGE = _auto()            # Range constraint (min/max)
    LENGTH = _auto()           # Length constraint (min/max length)
    REQUIRED = _auto()         # Required field constraint
    FORMAT = _auto()           # Format constraint (date, email, etc.)
    CUSTOM = _auto()           # Custom constraint

