#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/formats/schema/swagger_schema.py

Swagger Schema Serializer

Extends xwsystem.io.serialization for Swagger 2.0 specification support.
Reuses JSON/YAML serializers from xwsystem.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from typing import Any, Optional, Union

# Reuse xwsystem serializers
from exonware.xwsystem.io.serialization.formats.text.json import JsonSerializer
from exonware.xwsystem.io.serialization.formats.text.yaml import YamlSerializer
from exonware.xwsystem.io.serialization.contracts import EncodeOptions, DecodeOptions
from exonware.xwsystem.io.defs import CodecCapability
from exonware.xwsystem.io.serialization.errors import SerializationError
from exonware.xwsystem import get_logger
from ..base import ASchemaSerialization

logger = get_logger(__name__)


class SwaggerSchemaSerializer(ASchemaSerialization):
    """
    Swagger schema serializer - reuses JsonSerializer/YamlSerializer.
    
    Swagger 2.0 specs are JSON or YAML, so we delegate to those serializers
    and add Swagger-specific validation.
    """
    
    def __init__(self):
        """Initialize Swagger schema serializer."""
        super().__init__()
        # Reuse JSON and YAML serializers
        self._json_serializer = JsonSerializer()
        self._yaml_serializer = YamlSerializer()
    
    # ========================================================================
    # CODEC METADATA
    # ========================================================================
    
    @property
    def codec_id(self) -> str:
        return "swagger_schema"
    
    @property
    def media_types(self) -> list[str]:
        return ["application/swagger+json", "application/swagger+yaml", "application/json", "application/x-yaml"]
    
    @property
    def file_extensions(self) -> list[str]:
        return [".swagger.json", ".swagger.yaml", ".swagger.yml"]
    
    @property
    def format_name(self) -> str:
        return "SWAGGER"
    
    @property
    def mime_type(self) -> str:
        return "application/swagger+json"
    
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
        return ["swagger", "swagger_schema", "SWAGGER"]
    
    # ========================================================================
    # ASchemaSerialization IMPLEMENTATION
    # ========================================================================
    
    @property
    def schema_format_name(self) -> str:
        """Get schema format name for type/property mapping."""
        return "swagger"
    
    @property
    def reference_keywords(self) -> list[str]:
        """Swagger 2.0 uses $ref for references (JSON Schema compatible)."""
        return ['$ref']
    
    @property
    def definitions_keywords(self) -> list[str]:
        """Swagger 2.0 uses definitions for schema definitions."""
        return ['definitions']  # Swagger 2.0 uses definitions
    
    @property
    def properties_keyword(self) -> str:
        """Swagger uses 'properties' (JSON Schema compatible)."""
        return 'properties'
    
    @property
    def merge_keywords(self) -> dict[str, str]:
        """Swagger uses JSON Schema merge keywords."""
        return {
            'allOf': 'allOf',
            'anyOf': 'anyOf',
            'oneOf': 'oneOf'
        }
    
    def normalize_schema(self, schema: Any) -> dict[str, Any]:
        """Normalize Swagger spec to internal representation."""
        if isinstance(schema, dict):
            return schema.copy()
        else:
            raise SerializationError(f"Cannot normalize {type(schema).__name__} as Swagger spec")
    
    def denormalize_schema(self, normalized: dict[str, Any]) -> Any:
        """Convert normalized schema back to Swagger format."""
        return normalized.copy()
    
    # ========================================================================
    # CORE SERIALIZATION (Delegate to JsonSerializer/YamlSerializer)
    # ========================================================================
    
    def encode(self, value: Any, *, options: Optional[EncodeOptions] = None) -> Union[bytes, str]:
        """
        Encode Swagger specification to string.
        
        Uses JSON or YAML based on options or defaults to JSON.
        """
        # Validate it's a valid Swagger spec
        if isinstance(value, dict):
            self._validate_swagger_spec(value)
        
        # Determine format from options or default to JSON
        use_yaml = options and options.get('format') == 'yaml' if options else False
        
        if use_yaml:
            return self._yaml_serializer.encode(value, options=options)
        else:
            return self._json_serializer.encode(value, options=options)
    
    def decode(self, repr: Union[bytes, str], *, options: Optional[DecodeOptions] = None) -> Any:
        """
        Decode Swagger specification from string.
        
        Auto-detects JSON or YAML format.
        """
        # Try JSON first, then YAML
        try:
            spec = self._json_serializer.decode(repr, options=options)
        except Exception:
            try:
                spec = self._yaml_serializer.decode(repr, options=options)
            except Exception as e:
                raise SerializationError(f"Failed to decode Swagger spec: {e}") from e
        
        # Validate it's a valid Swagger spec
        if isinstance(spec, dict):
            self._validate_swagger_spec(spec)
        
        return spec
    
    # ========================================================================
    # SWAGGER VALIDATION
    # ========================================================================
    
    def _validate_swagger_spec(self, spec: dict[str, Any]) -> None:
        """
        Validate that dict is a valid Swagger 2.0 specification.
        """
        if not isinstance(spec, dict):
            raise SerializationError("Swagger specification must be a dictionary")
        
        # Check for required Swagger 2.0 fields
        if 'swagger' not in spec:
            raise SerializationError("Swagger specification must have 'swagger' field")
        
        swagger_version = spec['swagger']
        if not isinstance(swagger_version, str):
            raise SerializationError("Swagger 'swagger' field must be a string")
        
        # Validate version format (should be "2.0")
        if not swagger_version.startswith('2.'):
            logger.warning(f"Swagger version {swagger_version} may not be fully supported (expected 2.0)")
        
        # Check for required top-level fields
        required_fields = ['info', 'paths']
        for field in required_fields:
            if field not in spec:
                raise SerializationError(f"Swagger specification must have '{field}' field")
        
        # Validate info object
        if not isinstance(spec['info'], dict):
            raise SerializationError("Swagger 'info' must be a dictionary")
        
        if 'title' not in spec['info']:
            raise SerializationError("Swagger 'info' must have 'title' field")
        
        if 'version' not in spec['info']:
            raise SerializationError("Swagger 'info' must have 'version' field")
        
        # Validate paths object
        if not isinstance(spec['paths'], dict):
            raise SerializationError("Swagger 'paths' must be a dictionary")

