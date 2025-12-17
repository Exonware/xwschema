#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/formats/schema/graphql_schema.py

GraphQL Schema Serializer

Extends xwsystem.io.serialization for GraphQL schema definition language support.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from typing import Any, Optional, Union
from exonware.xwsystem.io.serialization.contracts import EncodeOptions, DecodeOptions
from exonware.xwsystem.io.defs import CodecCapability
from exonware.xwsystem.io.serialization.errors import SerializationError
from exonware.xwsystem import get_logger
from ..base import ASchemaSerialization

logger = get_logger(__name__)


class GraphQLSchemaSerializer(ASchemaSerialization):
    """
    GraphQL schema serializer.
    
    GraphQL schemas are SDL (Schema Definition Language) text files.
    For now, handles .graphql/.gql files as text. Full SDL parser can be added later.
    """
    
    def __init__(self):
        """Initialize GraphQL schema serializer."""
        super().__init__()
    
    # ========================================================================
    # CODEC METADATA
    # ========================================================================
    
    @property
    def codec_id(self) -> str:
        return "graphql_schema"
    
    @property
    def media_types(self) -> list[str]:
        return ["application/graphql", "text/graphql"]
    
    @property
    def file_extensions(self) -> list[str]:
        return [".graphql", ".gql"]
    
    @property
    def format_name(self) -> str:
        return "GRAPHQL_SCHEMA"
    
    @property
    def mime_type(self) -> str:
        return "application/graphql"
    
    @property
    def is_binary_format(self) -> bool:
        return False
    
    @property
    def supports_streaming(self) -> bool:
        return False
    
    @property
    def capabilities(self) -> CodecCapability:
        return CodecCapability.BIDIRECTIONAL
    
    @property
    def aliases(self) -> list[str]:
        return ["graphql_schema", "graphql", "gql", "GRAPHQL_SCHEMA"]
    
    # ========================================================================
    # ASchemaSerialization IMPLEMENTATION
    # ========================================================================
    
    @property
    def schema_format_name(self) -> str:
        """Get schema format name for type/property mapping."""
        return "graphql_schema"
    
    @property
    def reference_keywords(self) -> list[str]:
        """GraphQL uses type references and implements for references."""
        return ['type', 'implements']  # GraphQL uses type names, not $ref
    
    @property
    def definitions_keywords(self) -> list[str]:
        """GraphQL uses type, interface, enum, input, scalar for definitions."""
        return ['type', 'interface', 'enum', 'input', 'scalar']  # GraphQL structure
    
    @property
    def properties_keyword(self) -> str:
        """GraphQL uses 'field' for type fields."""
        return 'field'  # GraphQL uses fields, not properties
    
    @property
    def merge_keywords(self) -> dict[str, str]:
        """GraphQL uses union and interface for composition."""
        return {
            'allOf': 'implements',  # GraphQL implements is similar to allOf
            'anyOf': 'union',       # GraphQL union is similar to anyOf
            'oneOf': 'interface'    # GraphQL interface is similar to oneOf
        }
    
    def normalize_schema(self, schema: Any) -> dict[str, Any]:
        """Normalize GraphQL schema to internal representation."""
        if isinstance(schema, str):
            # GraphQL SDL text - store as string for now
            return {"sdl_content": schema, "type": "graphql"}
        elif isinstance(schema, dict):
            return schema.copy()
        else:
            raise SerializationError(f"Cannot normalize {type(schema).__name__} as GraphQL schema")
    
    def denormalize_schema(self, normalized: dict[str, Any]) -> Any:
        """Convert normalized schema back to GraphQL format."""
        if "sdl_content" in normalized:
            return normalized["sdl_content"]
        return normalized.copy()
    
    # ========================================================================
    # CORE SERIALIZATION (Text-based SDL)
    # ========================================================================
    
    def encode(self, value: Any, *, options: Optional[EncodeOptions] = None) -> Union[bytes, str]:
        """
        Encode GraphQL schema to string.
        
        For now, if value is already a string (GraphQL SDL), return it.
        If it's a dict, convert to GraphQL SDL format (basic implementation).
        """
        if isinstance(value, str):
            # Already GraphQL SDL text
            self._validate_graphql_schema(value)
            return value
        elif isinstance(value, dict):
            # Convert dict to GraphQL SDL (basic implementation)
            return self._dict_to_graphql(value)
        else:
            raise SerializationError(f"Cannot encode {type(value).__name__} as GraphQL schema")
    
    def decode(self, repr: Union[bytes, str], *, options: Optional[DecodeOptions] = None) -> Any:
        """
        Decode GraphQL schema from string.
        
        For now, returns the string as-is. Full GraphQL SDL parser can be added later.
        """
        if isinstance(repr, bytes):
            repr = repr.decode('utf-8')
        
        # Validate it's valid GraphQL SDL
        self._validate_graphql_schema(repr)
        
        # For now, return as string (full parser can be added later)
        # TODO: Parse GraphQL SDL into structured format
        return repr
    
    # ========================================================================
    # GRAPHQL VALIDATION
    # ========================================================================
    
    def _validate_graphql_schema(self, schema: str) -> None:
        """
        Basic validation of GraphQL SDL syntax.
        
        Full parser can be added later using graphql-core library.
        """
        if not isinstance(schema, str):
            raise SerializationError("GraphQL schema must be a string")
        
        # Basic syntax checks
        if 'type' not in schema.lower() and 'interface' not in schema.lower() and 'enum' not in schema.lower():
            logger.warning("GraphQL schema may be invalid - no type, interface, or enum found")
    
    def _dict_to_graphql(self, schema_dict: dict[str, Any]) -> str:
        """
        Convert dict representation to GraphQL SDL format.
        
        Basic implementation - full conversion can be added later.
        """
        # This is a placeholder - full implementation would require
        # proper GraphQL SDL generation
        logger.warning("Dict to GraphQL SDL conversion is not fully implemented")
        return "# GraphQL Schema\n# Generated from dict - full conversion not yet implemented\n"

