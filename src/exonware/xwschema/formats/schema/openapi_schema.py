#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/formats/schema/openapi_schema.py

OpenAPI Schema Serializer

Extends xwsystem.io.serialization for OpenAPI 3.0/3.1 specification support.
Reuses JSON/YAML serializers from xwsystem.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from typing import Any, Optional, Union
from pathlib import Path

# Reuse xwsystem serializers
from exonware.xwsystem.io.serialization.formats.text.json import JsonSerializer
from exonware.xwsystem.io.serialization.formats.text.yaml import YamlSerializer
from exonware.xwsystem.io.serialization.contracts import EncodeOptions, DecodeOptions
from exonware.xwsystem.io.defs import CodecCapability
from exonware.xwsystem.io.serialization.errors import SerializationError
from exonware.xwsystem import get_logger
from ..base import ASchemaSerialization

logger = get_logger(__name__)


class OpenApiSchemaSerializer(ASchemaSerialization):
    """
    OpenAPI schema serializer - reuses JsonSerializer/YamlSerializer.
    
    OpenAPI specs are JSON or YAML, so we delegate to those serializers
    and add OpenAPI-specific validation.
    """
    
    def __init__(self):
        """Initialize OpenAPI schema serializer."""
        super().__init__()
        # Reuse JSON and YAML serializers
        self._json_serializer = JsonSerializer()
        self._yaml_serializer = YamlSerializer()
    
    # ========================================================================
    # CODEC METADATA
    # ========================================================================
    
    @property
    def codec_id(self) -> str:
        return "openapi_schema"
    
    @property
    def media_types(self) -> list[str]:
        return ["application/vnd.oai.openapi+json", "application/vnd.oai.openapi+yaml", "application/json", "application/x-yaml"]
    
    @property
    def file_extensions(self) -> list[str]:
        return [".openapi.json", ".openapi.yaml", ".openapi.yml"]
    
    @property
    def format_name(self) -> str:
        return "OPENAPI"
    
    @property
    def mime_type(self) -> str:
        return "application/vnd.oai.openapi+json"
    
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
        return ["openapi", "openapi_schema", "OPENAPI", "oas"]
    
    # ========================================================================
    # ASchemaSerialization IMPLEMENTATION
    # ========================================================================
    
    @property
    def schema_format_name(self) -> str:
        """Get schema format name for type/property mapping."""
        return "openapi"
    
    @property
    def reference_keywords(self) -> list[str]:
        """OpenAPI uses $ref for references (JSON Schema compatible)."""
        return ['$ref']
    
    @property
    def definitions_keywords(self) -> list[str]:
        """OpenAPI uses components/schemas for definitions."""
        return ['components', 'schemas', 'definitions']  # OpenAPI 3.x uses components/schemas
    
    @property
    def properties_keyword(self) -> str:
        """OpenAPI uses 'properties' (JSON Schema compatible)."""
        return 'properties'
    
    @property
    def merge_keywords(self) -> dict[str, str]:
        """OpenAPI uses JSON Schema merge keywords."""
        return {
            'allOf': 'allOf',
            'anyOf': 'anyOf',
            'oneOf': 'oneOf'
        }
    
    def normalize_schema(self, schema: Any) -> dict[str, Any]:
        """Normalize OpenAPI spec to internal representation."""
        if isinstance(schema, dict):
            return schema.copy()
        else:
            raise SerializationError(f"Cannot normalize {type(schema).__name__} as OpenAPI spec")
    
    def denormalize_schema(self, normalized: dict[str, Any]) -> Any:
        """Convert normalized schema back to OpenAPI format."""
        return normalized.copy()
    
    # ========================================================================
    # CORE SERIALIZATION (Delegate to JsonSerializer/YamlSerializer)
    # ========================================================================
    
    def encode(self, value: Any, *, options: Optional[EncodeOptions] = None) -> Union[bytes, str]:
        """
        Encode OpenAPI specification to string.
        
        Uses JSON or YAML based on options or defaults to JSON.
        """
        # Validate it's a valid OpenAPI spec
        if isinstance(value, dict):
            self._validate_openapi_spec(value)
        
        # Determine format from options or default to JSON
        use_yaml = options and options.get('format') == 'yaml' if options else False
        
        if use_yaml:
            return self._yaml_serializer.encode(value, options=options)
        else:
            return self._json_serializer.encode(value, options=options)
    
    def decode(self, repr: Union[bytes, str], *, options: Optional[DecodeOptions] = None) -> Any:
        """
        Decode OpenAPI specification from string.
        
        Auto-detects JSON or YAML format.
        """
        # Try JSON first, then YAML
        try:
            spec = self._json_serializer.decode(repr, options=options)
        except Exception:
            try:
                spec = self._yaml_serializer.decode(repr, options=options)
            except Exception as e:
                raise SerializationError(f"Failed to decode OpenAPI spec: {e}") from e
        
        # Validate it's a valid OpenAPI spec
        if isinstance(spec, dict):
            self._validate_openapi_spec(spec)
        
        return spec
    
    # ========================================================================
    # OPENAPI VALIDATION
    # ========================================================================
    
    def _validate_openapi_spec(self, spec: dict[str, Any]) -> None:
        """
        Validate that dict is a valid OpenAPI specification.
        """
        if not isinstance(spec, dict):
            raise SerializationError("OpenAPI specification must be a dictionary")
        
        # Check for required OpenAPI fields
        if 'openapi' not in spec:
            # Check for Swagger 2.0 (legacy)
            if 'swagger' in spec:
                logger.warning("Swagger 2.0 detected. Consider migrating to OpenAPI 3.0")
                return
            raise SerializationError("OpenAPI specification must have 'openapi' field")
        
        openapi_version = spec['openapi']
        if not isinstance(openapi_version, str):
            raise SerializationError("OpenAPI 'openapi' field must be a string")
        
        # Validate version format (e.g., "3.0.0", "3.1.0")
        if not openapi_version.startswith('3.'):
            logger.warning(f"OpenAPI version {openapi_version} may not be fully supported")
        
        # Check for required top-level fields
        required_fields = ['info', 'paths']
        for field in required_fields:
            if field not in spec:
                raise SerializationError(f"OpenAPI specification must have '{field}' field")
        
        # Validate info object
        if not isinstance(spec['info'], dict):
            raise SerializationError("OpenAPI 'info' must be a dictionary")
        
        if 'title' not in spec['info']:
            raise SerializationError("OpenAPI 'info' must have 'title' field")
        
        # Validate paths object
        if not isinstance(spec['paths'], dict):
            raise SerializationError("OpenAPI 'paths' must be a dictionary")
        
        # Validate components if present (OpenAPI 3.0+)
        if 'components' in spec:
            if not isinstance(spec['components'], dict):
                raise SerializationError("OpenAPI 'components' must be a dictionary")

