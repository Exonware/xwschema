#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/formats/schema/json_schema.py

JSON Schema Serializer

JSON Schema is just JSON with a specific structure, so we reuse JsonSerializer
from xwsystem.io.serialization and add JSON Schema validation.

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


class JsonSchemaSerializer(ASchemaSerialization):
    """
    JSON Schema serializer - reuses JsonSerializer.
    
    JSON Schema files are JSON files, so we delegate to JsonSerializer
    and add JSON Schema-specific validation.
    """
    
    def __init__(self):
        """Initialize JSON Schema serializer."""
        super().__init__()
        # Reuse JsonSerializer directly
        self._json_serializer = JsonSerializer()
    
    # ========================================================================
    # CODEC METADATA (Override for schema-specific extensions)
    # ========================================================================
    
    @property
    def codec_id(self) -> str:
        return "json_schema"
    
    @property
    def media_types(self) -> list[str]:
        return ["application/schema+json", "application/json"]
    
    @property
    def file_extensions(self) -> list[str]:
        return [".schema.json", ".json"]
    
    @property
    def format_name(self) -> str:
        return "JSON_SCHEMA"
    
    @property
    def mime_type(self) -> str:
        return "application/schema+json"
    
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
        return ["json_schema", "jsonschema", "JSON_SCHEMA"]
    
    # ========================================================================
    # ASchemaSerialization IMPLEMENTATION
    # ========================================================================
    
    @property
    def schema_format_name(self) -> str:
        """Get schema format name for type/property mapping."""
        return "json_schema"
    
    @property
    def reference_keywords(self) -> list[str]:
        """JSON Schema uses $ref for references."""
        return ['$ref']
    
    @property
    def definitions_keywords(self) -> list[str]:
        """JSON Schema uses $defs (Draft 2020-12) or definitions (older drafts)."""
        return ['$defs', 'definitions']
    
    @property
    def properties_keyword(self) -> str:
        """JSON Schema uses 'properties' for object properties."""
        return 'properties'
    
    @property
    def merge_keywords(self) -> dict[str, str]:
        """JSON Schema merge keywords."""
        return {
            'allOf': 'allOf',
            'anyOf': 'anyOf',
            'oneOf': 'oneOf'
        }
    
    def normalize_schema(self, schema: Any) -> dict[str, Any]:
        """Normalize JSON Schema to internal representation."""
        if isinstance(schema, dict):
            return schema.copy()
        elif isinstance(schema, str):
            # Primitive type
            return {"type": schema}
        else:
            raise SerializationError(f"Cannot normalize {type(schema).__name__} as JSON Schema")
    
    def denormalize_schema(self, normalized: dict[str, Any]) -> Any:
        """Convert normalized schema back to JSON Schema format."""
        return normalized.copy()
    
    # ========================================================================
    # CORE SERIALIZATION (Delegate to JsonSerializer)
    # ========================================================================
    
    def encode(self, value: Any, *, options: Optional[EncodeOptions] = None) -> Union[bytes, str]:
        """Encode JSON Schema - delegate to JsonSerializer."""
        if isinstance(value, dict):
            self._validate_json_schema(value)
        return self._json_serializer.encode(value, options=options)
    
    def decode(self, repr: Union[bytes, str], *, options: Optional[DecodeOptions] = None) -> Any:
        """Decode JSON Schema - delegate to JsonSerializer."""
        result = self._json_serializer.decode(repr, options=options)
        if isinstance(result, dict):
            self._validate_json_schema(result)
        return result
    
    def _validate_json_schema(self, schema: dict[str, Any]) -> None:
        """Validate JSON Schema structure."""
        valid_keywords = {
            'type', 'properties', 'items', 'required', 'enum', 'const',
            'allOf', 'anyOf', 'oneOf', 'not', 'if', 'then', 'else',
            'format', 'pattern', 'minLength', 'maxLength',
            'minimum', 'maximum', 'exclusiveMinimum', 'exclusiveMaximum',
            'multipleOf', 'minItems', 'maxItems', 'uniqueItems',
            'minProperties', 'maxProperties', 'additionalProperties',
            '$ref', '$id', '$schema', '$anchor', '$defs', 'definitions',
            'title', 'description', 'default', 'examples', 'example',
            'readOnly', 'writeOnly', 'deprecated', 'nullable'
        }
        
        if '$schema' in schema and not isinstance(schema['$schema'], str):
            raise SerializationError("$schema must be a string")
        
        # Log unknown keywords (but don't fail)
        for key in schema.keys():
            if key not in valid_keywords and not key.startswith('$') and not key.startswith('x-'):
                logger.debug(f"Unknown JSON Schema keyword: {key}")

