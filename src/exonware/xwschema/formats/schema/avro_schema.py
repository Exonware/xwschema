#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/formats/schema/avro_schema.py

Avro Schema Serializer

Avro SCHEMA files (.avsc) are JSON-based text files, so we reuse JsonSerializer.
Avro DATA serialization uses XWAvroSerializer from xwformats (binary format).

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from typing import Any, Optional, Union
from exonware.xwsystem.io.serialization.formats.text.json import JsonSerializer
from exonware.xwsystem.io.serialization.contracts import EncodeOptions, DecodeOptions
from exonware.xwsystem.io.defs import CodecCapability
from exonware.xwsystem.io.serialization.errors import SerializationError
from exonware.xwsystem import get_logger
from ..base import ASchemaSerialization

logger = get_logger(__name__)


class AvroSchemaSerializer(ASchemaSerialization):
    """
    Avro schema serializer - reuses JsonSerializer.
    
    Avro schema files (.avsc) are JSON files, so we delegate to JsonSerializer
    and add Avro-specific validation.
    
    Note: Avro DATA serialization uses XWAvroSerializer from xwformats (binary).
    """
    
    def __init__(self):
        """Initialize Avro schema serializer."""
        super().__init__()
        # Reuse JsonSerializer (Avro schemas are JSON)
        self._json_serializer = JsonSerializer()
        self.avro_primitives = {'null', 'boolean', 'int', 'long', 'float', 'double', 'bytes', 'string'}
        self.avro_complex = {'record', 'enum', 'array', 'map', 'union', 'fixed'}
    
    # ========================================================================
    # CODEC METADATA
    # ========================================================================
    
    @property
    def codec_id(self) -> str:
        return "avro_schema"
    
    @property
    def media_types(self) -> list[str]:
        return ["application/avro+json", "application/json"]
    
    @property
    def file_extensions(self) -> list[str]:
        return [".avsc", ".avro"]  # .avro can be schema or data, but we handle schema
    
    @property
    def format_name(self) -> str:
        return "AVRO_SCHEMA"
    
    @property
    def mime_type(self) -> str:
        return "application/avro+json"
    
    @property
    def is_binary_format(self) -> bool:
        return False  # Avro schemas are JSON (text)
    
    @property
    def supports_streaming(self) -> bool:
        return False
    
    @property
    def capabilities(self) -> CodecCapability:
        return CodecCapability.BIDIRECTIONAL
    
    @property
    def aliases(self) -> list[str]:
        return ["avro_schema", "avsc", "AVRO_SCHEMA"]
    
    # ========================================================================
    # ASchemaSerialization IMPLEMENTATION
    # ========================================================================
    
    @property
    def schema_format_name(self) -> str:
        """Get schema format name for type/property mapping."""
        return "avro"
    
    @property
    def reference_keywords(self) -> list[str]:
        """Avro doesn't have explicit references, but can use names/types."""
        return []  # Avro uses named types, not $ref-style references
    
    @property
    def definitions_keywords(self) -> list[str]:
        """Avro doesn't have a definitions section - types are named inline."""
        return []  # Avro uses named types directly
    
    @property
    def properties_keyword(self) -> str:
        """Avro uses 'fields' for record fields."""
        return 'fields'
    
    @property
    def merge_keywords(self) -> dict[str, str]:
        """Avro doesn't have merge keywords - uses union types instead."""
        return {}  # Avro uses union types, not allOf/anyOf
    
    def normalize_schema(self, schema: Any) -> dict[str, Any]:
        """Normalize Avro schema to internal representation."""
        if isinstance(schema, dict):
            return schema.copy()
        elif isinstance(schema, str):
            # Primitive type
            return {"type": schema}
        else:
            raise SerializationError(f"Cannot normalize {type(schema).__name__} as Avro schema")
    
    def denormalize_schema(self, normalized: dict[str, Any]) -> Any:
        """Convert normalized schema back to Avro format."""
        return normalized.copy()
    
    # ========================================================================
    # CORE SERIALIZATION (Delegate to JsonSerializer)
    # ========================================================================
    
    def encode(self, value: Any, *, options: Optional[EncodeOptions] = None) -> Union[bytes, str]:
        """Encode Avro schema - delegate to JsonSerializer."""
        if isinstance(value, dict):
            self._validate_avro_schema(value)
        elif isinstance(value, str) and value not in self.avro_primitives:
            raise SerializationError(f"Invalid Avro primitive type: {value}")
        return self._json_serializer.encode(value, options=options)
    
    def decode(self, repr: Union[bytes, str], *, options: Optional[DecodeOptions] = None) -> Any:
        """Decode Avro schema - delegate to JsonSerializer."""
        result = self._json_serializer.decode(repr, options=options)
        if isinstance(result, dict):
            self._validate_avro_schema(result)
        elif isinstance(result, str) and result not in self.avro_primitives:
            logger.warning(f"Unknown Avro type: {result}")
        return result
    
    def _validate_avro_schema(self, schema: dict[str, Any]) -> None:
        """Validate Avro schema structure."""
        if 'type' not in schema:
            raise SerializationError("Avro schema must have a 'type' field")
        
        schema_type = schema['type']
        if schema_type in self.avro_primitives:
            return
        
        if schema_type == 'record':
            if 'name' not in schema or 'fields' not in schema:
                raise SerializationError("Avro record must have 'name' and 'fields'")
        elif schema_type == 'enum':
            if 'name' not in schema or 'symbols' not in schema:
                raise SerializationError("Avro enum must have 'name' and 'symbols'")
        elif schema_type == 'array' and 'items' not in schema:
            raise SerializationError("Avro array must have 'items'")
        elif schema_type == 'map' and 'values' not in schema:
            raise SerializationError("Avro map must have 'values'")
        elif schema_type == 'fixed':
            if 'name' not in schema or 'size' not in schema:
                raise SerializationError("Avro fixed must have 'name' and 'size'")
        elif schema_type not in self.avro_complex:
            raise SerializationError(f"Unknown Avro type: {schema_type}")

