#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/engine.py
XWSchemaEngine - The Brain of XWSchema
Orchestrates xwschema; load/save via xwdata (xwdata uses xwsystem for I/O). Validation and generation in-house.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.14
Generation Date: 09-Nov-2025
"""

from typing import Any
from pathlib import Path
import errno
from exonware.xwsystem.io.serialization.formats.text import json as _xw_json
import os
from exonware.xwsystem import get_logger
from exonware.xwdata import XWData
from .base import ASchemaEngine
from .config import XWSchemaConfig
from .defs import SchemaFormat, ValidationMode, SchemaGenerationMode
from .errors import (
    XWSchemaError, XWSchemaParseError, XWSchemaFormatError,
    XWSchemaValidationError
)
from .validator import DefaultValidationStrategy
from .generator import DefaultGenerationStrategy
logger = get_logger(__name__)


def _ensure_local_path_exists(source: str, is_url: bool) -> None:
    """Raise FileNotFoundError for missing local paths before delegating I/O to xwdata."""
    if is_url:
        return
    p = Path(source)
    if not p.exists():
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(p))


# ==============================================================================
# SCHEMA FORMAT EXTENSION MAPPING
# ==============================================================================
_SCHEMA_FORMAT_EXTENSIONS = {
    # JSON Schema
    '.json': SchemaFormat.JSON_SCHEMA,
    '.schema.json': SchemaFormat.JSON_SCHEMA,
    # Avro
    '.avsc': SchemaFormat.AVRO,
    '.avro': SchemaFormat.AVRO,
    # Protobuf
    '.proto': SchemaFormat.PROTOBUF,
    # OpenAPI
    '.openapi.json': SchemaFormat.OPENAPI,
    '.openapi.yaml': SchemaFormat.OPENAPI,
    '.openapi.yml': SchemaFormat.OPENAPI,
    # Swagger
    '.swagger.json': SchemaFormat.SWAGGER,
    '.swagger.yaml': SchemaFormat.SWAGGER,
    # GraphQL
    '.graphql': SchemaFormat.GRAPHQL,
    '.gql': SchemaFormat.GRAPHQL,
    # XML Schema
    '.xsd': SchemaFormat.XSD,
    '.wsdl': SchemaFormat.WSDL,
}


class XWSchemaEngine(ASchemaEngine):
    """
    Universal schema engine orchestrating all xwschema operations.
    Reuses xwdata to the max: load_schema/save_schema use XWData.load/save only;
    $ref resolution uses xwdata ReferenceResolver. Validation and generation in-house.
    """

    def __init__(self, config: XWSchemaConfig | None = None):
        super().__init__(config)
        self._config = config or XWSchemaConfig.default()
        self._validation_strategy: DefaultValidationStrategy | None = None
        self._generation_strategy: DefaultGenerationStrategy | None = None
        logger.debug("XWSchemaEngine initialized")
    @staticmethod

    def _schema_format_to_str(format: SchemaFormat | None) -> str | None:
        """Map SchemaFormat to xwdata format string."""
        if not format:
            return None
        name = format.name if hasattr(format, 'name') else str(format)
        s = name.lower().replace('_schema', '').replace('_', '-')
        return 'json' if s == 'json' else s
    # ==========================================================================
    # VALIDATION / GENERATION STRATEGIES (Option 5: composition)
    # ==========================================================================

    def _ensure_validator(self) -> DefaultValidationStrategy:
        """Lazy initialize validation strategy (used by facade as validator)."""
        if self._validation_strategy is None:
            self._validation_strategy = DefaultValidationStrategy(mode=self._config.validation.mode)
        return self._validation_strategy

    def _ensure_generator(self) -> DefaultGenerationStrategy:
        """Lazy initialize generation strategy."""
        if self._generation_strategy is None:
            self._generation_strategy = DefaultGenerationStrategy(config=self._config.generation)
        return self._generation_strategy
    # ==========================================================================
    # SCHEMA FORMAT DETECTION
    # ==========================================================================

    def _detect_schema_format(self, path: Path) -> SchemaFormat:
        """Detect schema format from file extension."""
        suffix = path.suffix.lower()
        # Try exact match first
        if suffix in _SCHEMA_FORMAT_EXTENSIONS:
            return _SCHEMA_FORMAT_EXTENSIONS[suffix]
        # Try compound extensions (e.g., .schema.json)
        for ext, format_type in _SCHEMA_FORMAT_EXTENSIONS.items():
            if str(path).lower().endswith(ext):
                return format_type
        # Default to JSON Schema
        return SchemaFormat.JSON_SCHEMA
    # ==========================================================================
    # SCHEMA LOADING
    # ==========================================================================

    async def load_schema(self, path: str | Path, format: SchemaFormat | None = None) -> dict[str, Any]:
        """
        Load schema from file or URL.
        Uses XWData.load() for file I/O (caching, format detection). Resolves $ref using
        xwdata's ReferenceResolver when enable_reference_resolution.
        Args:
            path: Path to schema file or URL (str or Path)
            format: Optional format (auto-detected from path for files; default JSON for URLs)
        Returns:
            Schema definition as dict (with references resolved if config enabled)
        """
        source = str(path) if isinstance(path, Path) else path
        is_url = source.startswith(("http://", "https://"))
        if format is None:
            format = (
                SchemaFormat.JSON_SCHEMA
                if is_url
                else self._detect_schema_format(Path(source))
            )
        schema_dict: dict[str, Any]
        if not is_url and format == SchemaFormat.JSON_SCHEMA:
            path_obj = Path(source)
            if path_obj.is_file():
                try:
                    with open(path_obj, encoding="utf-8") as f:
                        schema_dict = _xw_json.load(f)
                except Exception as e:
                    raise XWSchemaParseError(
                        f"Failed to load JSON schema file: {e}",
                        path=source,
                        format=format.name,
                    ) from e
            else:
                _ensure_local_path_exists(source, is_url)
                format_hint = self._schema_format_to_str(format)
                data = await XWData.load(source, format_hint=format_hint)
                schema_dict = data.to_native()
        else:
            _ensure_local_path_exists(source, is_url)
            format_hint = self._schema_format_to_str(format)
            data = await XWData.load(source, format_hint=format_hint)
            schema_dict = data.to_native()
        if not isinstance(schema_dict, dict):
            raise XWSchemaParseError(
                f"Schema file does not contain a valid schema object",
                path=source,
                format=format.name
            )
        base_path = Path(source).parent if not is_url else None
        if getattr(self._config, "enable_reference_resolution", False) and self._has_ref(schema_dict):
            schema_dict = await self._resolve_schema_refs(schema_dict, base_path)
        logger.debug(f"Loaded schema from {source} (format: {format.name})")
        return schema_dict

    def _has_ref(self, obj: Any) -> bool:
        """Check if schema (or nested) contains $ref."""
        if isinstance(obj, dict):
            if '$ref' in obj:
                return True
            for v in obj.values():
                if self._has_ref(v):
                    return True
        elif isinstance(obj, list):
            for item in obj:
                if self._has_ref(item):
                    return True
        return False

    async def _resolve_schema_refs(self, schema_dict: dict[str, Any], base_path: Path | None = None) -> dict[str, Any]:
        """Resolve $ref in schema using xwdata's ReferenceResolver (xwdata is required)."""
        try:
            from exonware.xwdata.data.references.resolver import ReferenceResolver
            from exonware.xwdata.data.strategies.json import JSONFormatStrategy
            resolver = ReferenceResolver()
            strategy = JSONFormatStrategy()
            resolved = await resolver.resolve(schema_dict, strategy, base_path=base_path)
            return resolved if isinstance(resolved, dict) else schema_dict
        except Exception as e:
            logger.warning(f"Reference resolution failed: {e}, using schema as-is")
            return schema_dict
    # ==========================================================================
    # SCHEMA SAVING
    # ==========================================================================

    async def save_schema(self, schema: dict[str, Any], path: Path, format: SchemaFormat) -> None:
        """Save schema to file. Uses stdlib JSON for JSON_SCHEMA to avoid xwdata serializer deps; else delegates to XWData.save."""
        path_obj = Path(path)
        if format == SchemaFormat.JSON_SCHEMA and not str(path_obj).startswith(("http://", "https://")):
            try:
                with open(path_obj, "w", encoding="utf-8") as f:
                    _xw_json.dump(schema, f, indent=2)
                logger.debug(f"Saved schema to {path} (format: {format.name})")
                return
            except Exception as e:
                raise XWSchemaError(f"Failed to save JSON schema file: {e}") from e
        data = XWData.from_native(schema)
        await data.save(path, format=self._schema_format_to_str(format))
        logger.debug(f"Saved schema to {path} (format: {format.name})")
    # ==========================================================================
    # VALIDATION
    # ==========================================================================

    async def validate_data(self, data: Any, schema: dict[str, Any], mode: ValidationMode = ValidationMode.STRICT) -> tuple[bool, list[str]]:
        """
        Validate data against schema.
        Reuses DefaultValidationStrategy which uses XWData for efficient navigation.
        Resolves $ref in schema using xwdata ReferenceResolver when enabled.
        Args:
            data: Data to validate (can be dict, list, or XWData instance)
            schema: Schema definition (may contain $ref; resolved when config enables)
            mode: Validation mode
        Returns:
            Tuple of (is_valid, error_messages)
        """
        # Resolve references in schema when enabled (reuses xwdata ReferenceResolver)
        if getattr(self._config, "enable_reference_resolution", False) and self._has_ref(schema):
            base = getattr(self._config, 'reference_base_path', None)
            schema = await self._resolve_schema_refs(schema, base)
        validator = self._ensure_validator()
        return validator.validate_schema(data, schema)
    # ==========================================================================
    # SCHEMA GENERATION
    # ==========================================================================

    async def generate_schema(self, data: Any, mode: SchemaGenerationMode = SchemaGenerationMode.INFER) -> dict[str, Any]:
        """
        Generate schema from data.
        Reuses DefaultGenerationStrategy which uses XWData for structure analysis.
        Args:
            data: Data to generate schema from (can be dict, list, or XWData instance)
            mode: Generation mode
        Returns:
            Schema definition
        """
        generator = self._ensure_generator()
        return await generator.generate_from_data(data, mode)
    # ==========================================================================
    # FORMAT CONVERSION
    # ==========================================================================

    async def convert_schema(self, schema: dict[str, Any], from_format: SchemaFormat, to_format: SchemaFormat) -> dict[str, Any]:
        """
        Convert schema between formats.
        Converts schemas between different formats using format-specific converters.
        Supports conversion between JSON Schema, OpenAPI, GraphQL, Protobuf, Avro, and XSD.
        Args:
            schema: Schema definition
            from_format: Source format
            to_format: Target format
        Returns:
            Converted schema definition
        Priority Alignment:
        - Usability: Simple format conversion API
        - Maintainability: Strategy-based conversion approach
        - Performance: Efficient format-specific conversion
        - Extensibility: Easy to add new format converters
        Note:
            Uses intermediate JSON Schema representation for most conversions.
            Format-specific optimizations can be added for direct conversions.
        """
        if from_format == to_format:
            return schema
        from_format_name = from_format.name if hasattr(from_format, 'name') else str(from_format)
        to_format_name = to_format.name if hasattr(to_format, 'name') else str(to_format)
        logger.debug(f"Converting schema from {from_format_name} to {to_format_name}")
        # Convert via intermediate JSON Schema representation
        # Strategy: from_format → JSON Schema → to_format
        # Step 1: Normalize to JSON Schema (if not already)
        json_schema = await self._normalize_to_json_schema(schema, from_format)
        # Step 2: Convert JSON Schema to target format
        result = await self._convert_from_json_schema(json_schema, to_format)
        logger.debug(f"Schema conversion completed: {from_format_name} → {to_format_name}")
        return result

    async def _normalize_to_json_schema(self, schema: Any, from_format: SchemaFormat) -> dict[str, Any]:
        """
        Normalize schema from source format to JSON Schema.
        Args:
            schema: Schema in source format
            from_format: Source format
        Returns:
            JSON Schema representation
        """
        if from_format == SchemaFormat.JSON_SCHEMA:
            # Already JSON Schema
            return schema if isinstance(schema, dict) else {}
        # Use format-specific normalizers
        if from_format == SchemaFormat.OPENAPI:
            return self._normalize_openapi_to_json_schema(schema)
        elif from_format == SchemaFormat.SWAGGER:
            return self._normalize_swagger_to_json_schema(schema)
        elif from_format == SchemaFormat.GRAPHQL:
            return self._normalize_graphql_to_json_schema(schema)
        elif from_format == SchemaFormat.PROTOBUF:
            return self._normalize_protobuf_to_json_schema(schema)
        elif from_format == SchemaFormat.AVRO:
            return self._normalize_avro_to_json_schema(schema)
        elif from_format == SchemaFormat.XSD:
            return self._normalize_xsd_to_json_schema(schema)
        else:
            # Unknown format - try to use as-is
            logger.warning(f"Unknown source format {from_format.name}, using schema as-is")
            return schema if isinstance(schema, dict) else {}

    async def _convert_from_json_schema(self, json_schema: dict[str, Any], to_format: SchemaFormat) -> dict[str, Any]:
        """
        Convert JSON Schema to target format.
        Args:
            json_schema: JSON Schema representation
            to_format: Target format
        Returns:
            Schema in target format
        """
        if to_format == SchemaFormat.JSON_SCHEMA:
            # Already JSON Schema
            return json_schema
        # Use format-specific converters
        if to_format == SchemaFormat.OPENAPI:
            return self._convert_json_schema_to_openapi(json_schema)
        elif to_format == SchemaFormat.SWAGGER:
            return self._convert_json_schema_to_swagger(json_schema)
        elif to_format == SchemaFormat.GRAPHQL:
            return self._convert_json_schema_to_graphql(json_schema)
        elif to_format == SchemaFormat.PROTOBUF:
            return self._convert_json_schema_to_protobuf(json_schema)
        elif to_format == SchemaFormat.AVRO:
            return self._convert_json_schema_to_avro(json_schema)
        elif to_format == SchemaFormat.XSD:
            return self._convert_json_schema_to_xsd(json_schema)
        else:
            # Unknown format - return JSON Schema
            logger.warning(f"Unknown target format {to_format.name}, returning JSON Schema")
            return json_schema
    # Format-specific normalizers (to JSON Schema)

    def _normalize_openapi_to_json_schema(self, openapi_schema: dict[str, Any]) -> dict[str, Any]:
        """Normalize OpenAPI schema to JSON Schema."""
        # OpenAPI 3.x uses JSON Schema for schemas, but wraps them in components/schemas
        if 'components' in openapi_schema and 'schemas' in openapi_schema['components']:
            # Extract first schema as example
            schemas = openapi_schema['components']['schemas']
            if schemas:
                return list(schemas.values())[0]
        # Try direct schema extraction
        if 'schema' in openapi_schema:
            return openapi_schema['schema']
        return openapi_schema

    def _normalize_swagger_to_json_schema(self, swagger_schema: dict[str, Any]) -> dict[str, Any]:
        """Normalize Swagger (OpenAPI 2.0) schema to JSON Schema."""
        # Similar to OpenAPI but with 'definitions' instead of 'components/schemas'
        if 'definitions' in swagger_schema and swagger_schema['definitions']:
            schemas = swagger_schema['definitions']
            if schemas:
                return list(schemas.values())[0]
        if 'schema' in swagger_schema:
            return swagger_schema['schema']
        return swagger_schema

    def _normalize_graphql_to_json_schema(self, graphql_schema: dict[str, Any]) -> dict[str, Any]:
        """Normalize GraphQL schema to JSON Schema."""
        # Basic conversion: extract type information
        json_schema: dict[str, Any] = {
            '$schema': 'http://json-schema.org/draft-07/schema#',
            'type': 'object',
            'properties': {}
        }
        # Extract types from GraphQL schema
        if 'types' in graphql_schema:
            for type_name, type_def in graphql_schema['types'].items():
                if 'fields' in type_def:
                    for field_name, field_def in type_def['fields'].items():
                        json_schema['properties'][field_name] = {
                            'type': self._graphql_type_to_json_type(field_def.get('type', 'string'))
                        }
        return json_schema

    def _normalize_protobuf_to_json_schema(self, protobuf_schema: dict[str, Any]) -> dict[str, Any]:
        """Normalize Protobuf schema to JSON Schema."""
        # Basic conversion: extract message information
        json_schema: dict[str, Any] = {
            '$schema': 'http://json-schema.org/draft-07/schema#',
            'type': 'object',
            'properties': {}
        }
        # Extract messages from Protobuf schema
        if 'messages' in protobuf_schema:
            for message_name, message_def in protobuf_schema['messages'].items():
                if 'fields' in message_def:
                    for field_name, field_def in message_def['fields'].items():
                        json_schema['properties'][field_name] = {
                            'type': self._protobuf_type_to_json_type(field_def.get('type', 'string'))
                        }
        return json_schema

    def _normalize_avro_to_json_schema(self, avro_schema: dict[str, Any]) -> dict[str, Any]:
        """Normalize Avro schema to JSON Schema."""
        # Avro schemas are close to JSON Schema already
        # Main difference: Avro uses 'fields' array, JSON Schema uses 'properties' object
        if isinstance(avro_schema, dict):
            if 'fields' in avro_schema:
                # Convert fields array to properties object
                json_schema = avro_schema.copy()
                json_schema['properties'] = {}
                for field in avro_schema['fields']:
                    if isinstance(field, dict) and 'name' in field:
                        json_schema['properties'][field['name']] = {
                            'type': self._avro_type_to_json_type(field.get('type', 'string'))
                        }
                del json_schema['fields']
                return json_schema
            return avro_schema
        return {}

    def _normalize_xsd_to_json_schema(self, xsd_schema: dict[str, Any]) -> dict[str, Any]:
        """Normalize XSD schema to JSON Schema."""
        # Basic conversion - XSD to JSON Schema is complex
        json_schema: dict[str, Any] = {
            '$schema': 'http://json-schema.org/draft-07/schema#',
            'type': 'object',
            'properties': {}
        }
        # Simplified conversion - full implementation would require proper XSD parsing
        if 'elements' in xsd_schema:
            for element_name, element_def in xsd_schema['elements'].items():
                json_schema['properties'][element_name] = {
                    'type': self._xsd_type_to_json_type(element_def.get('type', 'string'))
                }
        return json_schema
    # Format-specific converters (from JSON Schema)

    def _convert_json_schema_to_openapi(self, json_schema: dict[str, Any]) -> dict[str, Any]:
        """Convert JSON Schema to OpenAPI format."""
        return {
            'openapi': '3.0.0',
            'info': {
                'title': 'Converted Schema',
                'version': '1.0.0'
            },
            'components': {
                'schemas': {
                    'Schema': json_schema
                }
            }
        }

    def _convert_json_schema_to_swagger(self, json_schema: dict[str, Any]) -> dict[str, Any]:
        """Convert JSON Schema to Swagger (OpenAPI 2.0) format."""
        return {
            'swagger': '2.0',
            'info': {
                'title': 'Converted Schema',
                'version': '1.0.0'
            },
            'definitions': {
                'Schema': json_schema
            }
        }

    def _convert_json_schema_to_graphql(self, json_schema: dict[str, Any]) -> dict[str, Any]:
        """Convert JSON Schema to GraphQL format."""
        result: dict[str, Any] = {
            'type': 'graphql',
            'types': {},
            'sdl_content': ''
        }
        # Create GraphQL type from JSON Schema properties
        if 'properties' in json_schema:
            fields = {}
            for prop_name, prop_def in json_schema['properties'].items():
                if isinstance(prop_def, dict):
                    fields[prop_name] = {
                        'name': prop_name,
                        'type': self._json_type_to_graphql_type(prop_def.get('type', 'string')),
                        'required': prop_name in json_schema.get('required', []),
                        'list': False
                    }
            result['types']['QueryType'] = {
                'name': 'QueryType',
                'fields': fields
            }
        return result

    def _convert_json_schema_to_protobuf(self, json_schema: dict[str, Any]) -> dict[str, Any]:
        """Convert JSON Schema to Protobuf format."""
        result: dict[str, Any] = {
            'type': 'protobuf',
            'syntax': 'proto3',
            'messages': {}
        }
        # Create Protobuf message from JSON Schema properties
        if 'properties' in json_schema:
            fields = {}
            field_number = 1
            for prop_name, prop_def in json_schema['properties'].items():
                if isinstance(prop_def, dict):
                    fields[prop_name] = {
                        'name': prop_name,
                        'type': self._json_type_to_protobuf_type(prop_def.get('type', 'string')),
                        'number': field_number,
                        'repeated': prop_def.get('type') == 'array',
                        'optional': prop_name not in json_schema.get('required', [])
                    }
                    field_number += 1
            result['messages']['Schema'] = {
                'name': 'Schema',
                'fields': fields
            }
        return result

    def _convert_json_schema_to_avro(self, json_schema: dict[str, Any]) -> dict[str, Any]:
        """Convert JSON Schema to Avro format."""
        result: dict[str, Any] = {
            'type': 'record',
            'name': 'Schema',
            'fields': []
        }
        # Convert properties to fields
        if 'properties' in json_schema:
            for prop_name, prop_def in json_schema['properties'].items():
                if isinstance(prop_def, dict):
                    result['fields'].append({
                        'name': prop_name,
                        'type': self._json_type_to_avro_type(prop_def.get('type', 'string'))
                    })
        return result

    def _convert_json_schema_to_xsd(self, json_schema: dict[str, Any]) -> dict[str, Any]:
        """Convert JSON Schema to XSD format."""
        result: dict[str, Any] = {
            'type': 'xsd',
            'elements': {}
        }
        # Convert properties to elements
        if 'properties' in json_schema:
            for prop_name, prop_def in json_schema['properties'].items():
                if isinstance(prop_def, dict):
                    result['elements'][prop_name] = {
                        'name': prop_name,
                        'type': self._json_type_to_xsd_type(prop_def.get('type', 'string'))
                    }
        return result
    # Type conversion helpers

    def _graphql_type_to_json_type(self, graphql_type: str) -> str:
        """Convert GraphQL type to JSON Schema type."""
        type_map = {
            'String': 'string',
            'Int': 'integer',
            'Float': 'number',
            'Boolean': 'boolean',
            'ID': 'string'
        }
        return type_map.get(graphql_type, 'string')

    def _protobuf_type_to_json_type(self, protobuf_type: str) -> str:
        """Convert Protobuf type to JSON Schema type."""
        type_map = {
            'string': 'string',
            'int32': 'integer',
            'int64': 'integer',
            'float': 'number',
            'double': 'number',
            'bool': 'boolean',
            'bytes': 'string'
        }
        return type_map.get(protobuf_type.lower(), 'string')

    def _avro_type_to_json_type(self, avro_type: str) -> str:
        """Convert Avro type to JSON Schema type."""
        type_map = {
            'string': 'string',
            'int': 'integer',
            'long': 'integer',
            'float': 'number',
            'double': 'number',
            'boolean': 'boolean',
            'bytes': 'string',
            'null': 'null'
        }
        return type_map.get(str(avro_type).lower(), 'string')

    def _xsd_type_to_json_type(self, xsd_type: str) -> str:
        """Convert XSD type to JSON Schema type."""
        type_map = {
            'xs:string': 'string',
            'xs:integer': 'integer',
            'xs:decimal': 'number',
            'xs:float': 'number',
            'xs:double': 'number',
            'xs:boolean': 'boolean',
            'xs:date': 'string',
            'xs:dateTime': 'string'
        }
        return type_map.get(xsd_type, 'string')

    def _json_type_to_graphql_type(self, json_type: str) -> str:
        """Convert JSON Schema type to GraphQL type."""
        type_map = {
            'string': 'String',
            'integer': 'Int',
            'number': 'Float',
            'boolean': 'Boolean',
            'array': '[String]',
            'object': 'JSON'
        }
        return type_map.get(json_type, 'String')

    def _json_type_to_protobuf_type(self, json_type: str) -> str:
        """Convert JSON Schema type to Protobuf type."""
        type_map = {
            'string': 'string',
            'integer': 'int32',
            'number': 'double',
            'boolean': 'bool',
            'array': 'string'  # Simplified
        }
        return type_map.get(json_type, 'string')

    def _json_type_to_avro_type(self, json_type: str) -> str:
        """Convert JSON Schema type to Avro type."""
        type_map = {
            'string': 'string',
            'integer': 'int',
            'number': 'double',
            'boolean': 'boolean',
            'array': {'type': 'array', 'items': 'string'},
            'object': {'type': 'record', 'name': 'object', 'fields': []}
        }
        return type_map.get(json_type, 'string')

    def _json_type_to_xsd_type(self, json_type: str) -> str:
        """Convert JSON Schema type to XSD type."""
        type_map = {
            'string': 'xs:string',
            'integer': 'xs:integer',
            'number': 'xs:decimal',
            'boolean': 'xs:boolean',
            'array': 'xs:string'  # Simplified
        }
        return type_map.get(json_type, 'xs:string')
