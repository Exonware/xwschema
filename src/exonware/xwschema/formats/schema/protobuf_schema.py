#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/formats/schema/protobuf_schema.py

Protobuf Schema Serializer

Extends xwsystem.io.serialization for Protocol Buffers schema support.
Basic implementation - full Protobuf IDL parser can be added later.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from typing import Any, Optional, Union
from pathlib import Path
from exonware.xwsystem.io.serialization.contracts import EncodeOptions, DecodeOptions
from exonware.xwsystem.io.defs import CodecCapability
from exonware.xwsystem.io.serialization.errors import SerializationError
from exonware.xwsystem import get_logger
from ..base import ASchemaSerialization

logger = get_logger(__name__)


class ProtobufSchemaSerializer(ASchemaSerialization):
    """
    Protobuf schema serializer.
    
    Protobuf SCHEMA files (.proto) are IDL text files.
    Protobuf DATA serialization uses XWProtobufSerializer from xwformats (binary).
    
    For now, handles .proto files as text. Full IDL parser can be added later.
    """
    
    def __init__(self):
        """Initialize Protobuf schema serializer."""
        super().__init__()
    
    # ========================================================================
    # CODEC METADATA
    # ========================================================================
    
    @property
    def codec_id(self) -> str:
        return "protobuf_schema"
    
    @property
    def media_types(self) -> list[str]:
        return ["application/x-protobuf", "text/x-protobuf"]
    
    @property
    def file_extensions(self) -> list[str]:
        return [".proto"]
    
    @property
    def format_name(self) -> str:
        return "PROTOBUF_SCHEMA"
    
    @property
    def mime_type(self) -> str:
        return "application/x-protobuf"
    
    @property
    def is_binary_format(self) -> bool:
        return False  # .proto files are text
    
    @property
    def supports_streaming(self) -> bool:
        return False
    
    @property
    def capabilities(self) -> CodecCapability:
        return CodecCapability.BIDIRECTIONAL
    
    @property
    def aliases(self) -> list[str]:
        return ["protobuf_schema", "proto", "PROTOBUF_SCHEMA"]
    
    # ========================================================================
    # ASchemaSerialization IMPLEMENTATION
    # ========================================================================
    
    @property
    def schema_format_name(self) -> str:
        """Get schema format name for type/property mapping."""
        return "protobuf_schema"
    
    @property
    def reference_keywords(self) -> list[str]:
        """Protobuf uses import and package for references."""
        return ['import', 'package']  # Protobuf uses imports, not $ref
    
    @property
    def definitions_keywords(self) -> list[str]:
        """Protobuf uses message, enum, service for definitions."""
        return ['message', 'enum', 'service']  # Protobuf structure
    
    @property
    def properties_keyword(self) -> str:
        """Protobuf uses 'field' for message fields."""
        return 'field'  # Protobuf uses fields, not properties
    
    @property
    def merge_keywords(self) -> dict[str, str]:
        """Protobuf doesn't have merge keywords - uses inheritance/extensions."""
        return {}  # Protobuf uses extends/oneof, not allOf/anyOf
    
    def normalize_schema(self, schema: Any) -> dict[str, Any]:
        """Normalize Protobuf schema to internal representation."""
        if isinstance(schema, str):
            # Protobuf IDL text - store as string for now
            return {"idl_content": schema, "type": "protobuf"}
        elif isinstance(schema, dict):
            return schema.copy()
        else:
            raise SerializationError(f"Cannot normalize {type(schema).__name__} as Protobuf schema")
    
    def denormalize_schema(self, normalized: dict[str, Any]) -> Any:
        """Convert normalized schema back to Protobuf format."""
        if "idl_content" in normalized:
            return normalized["idl_content"]
        return normalized.copy()
    
    # ========================================================================
    # CORE SERIALIZATION (Text-based IDL)
    # ========================================================================
    
    def encode(self, value: Any, *, options: Optional[EncodeOptions] = None) -> Union[bytes, str]:
        """
        Encode Protobuf schema to string.
        
        For now, if value is already a string (Protobuf IDL), return it.
        If it's a dict, convert to Protobuf IDL format (basic implementation).
        """
        if isinstance(value, str):
            # Already Protobuf IDL text
            self._validate_protobuf_schema(value)
            return value
        elif isinstance(value, dict):
            # Convert dict to Protobuf IDL (basic implementation)
            return self._dict_to_protobuf(value)
        else:
            raise SerializationError(f"Cannot encode {type(value).__name__} as Protobuf schema")
    
    def decode(self, repr: Union[bytes, str], *, options: Optional[DecodeOptions] = None) -> Any:
        """
        Decode Protobuf schema from string.
        
        For now, returns the string as-is. Full Protobuf IDL parser can be added later.
        """
        if isinstance(repr, bytes):
            repr = repr.decode('utf-8')
        
        # Validate it's valid Protobuf IDL
        self._validate_protobuf_schema(repr)
        
        # For now, return as string (full parser can be added later)
        # TODO: Parse Protobuf IDL into structured format
        return repr
    
    # ========================================================================
    # PROTOBUF VALIDATION
    # ========================================================================
    
    def _validate_protobuf_schema(self, schema: str) -> None:
        """
        Basic validation of Protobuf IDL syntax.
        
        Full parser can be added later using protobuf library.
        """
        if not isinstance(schema, str):
            raise SerializationError("Protobuf schema must be a string")
        
        # Basic syntax checks
        if 'syntax' not in schema and 'message' not in schema and 'enum' not in schema:
            logger.warning("Protobuf schema may be invalid - no syntax, message, or enum found")
    
    def _dict_to_protobuf(self, schema_dict: dict[str, Any]) -> str:
        """
        Convert dict representation to Protobuf IDL format.
        
        Basic implementation - full conversion can be added later.
        """
        # This is a placeholder - full implementation would require
        # proper Protobuf IDL generation
        logger.warning("Dict to Protobuf IDL conversion is not fully implemented")
        return f"syntax = \"proto3\";\n\n// Generated from dict - full conversion not yet implemented\n"

