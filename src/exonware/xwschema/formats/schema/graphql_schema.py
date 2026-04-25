#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/formats/schema/graphql_schema.py
GraphQL Schema Serializer
Extends xwsystem.io.serialization for GraphQL schema definition language support.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.19
Generation Date: 09-Nov-2025
"""

from typing import Any
from exonware.xwsystem.io.serialization.contracts import EncodeOptions, DecodeOptions
from exonware.xwsystem.io.defs import CodecCapability
from exonware.xwsystem.io.serialization.errors import SerializationError
from exonware.xwsystem import get_logger
from ..base import ASchemaSerialization
logger = get_logger(__name__)


class GraphQLSchemaSerializer(ASchemaSerialization):
    """
    GraphQL Schema serializer - fully reuses xwsystem serialization infrastructure.
    Uses xwsystem serialization contracts and capabilities.
    No manual serialization - all delegated to xwsystem.
    """
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

    def encode(self, value: Any, *, options: EncodeOptions | None = None) -> bytes | str:
        """
        Encode GraphQL schema to string.
        GraphQL uses SDL (Schema Definition Language) text format.
        For dict values, converts to GraphQL SDL format.
        Note: This is schema-specific conversion, not general serialization.
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

    def decode(self, repr: bytes | str, *, options: DecodeOptions | None = None) -> Any:
        """
        Decode GraphQL schema from string.
        Parses GraphQL SDL into structured format (basic implementation).
        Returns a structured dictionary representation of the GraphQL schema.
        """
        if isinstance(repr, bytes):
            repr = repr.decode('utf-8')
        # Validate it's valid GraphQL SDL
        self._validate_graphql_schema(repr)
        # Parse GraphQL SDL into structured format
        # Basic implementation: extracts types, fields, and directives
        return self._parse_graphql_sdl(repr)

    def _parse_graphql_sdl(self, sdl: str) -> dict[str, Any]:
        """
        Parse GraphQL SDL into structured format.
        Basic implementation that extracts:
        - Types (type, interface, input, enum, scalar)
        - Fields with types and directives
        - Directives
        - Queries, mutations, subscriptions (if schema definition present)
        Args:
            sdl: GraphQL SDL string
        Returns:
            Structured dictionary representation
        """
        result: dict[str, Any] = {
            'type': 'graphql',
            'sdl_content': sdl,
            'types': {},
            'interfaces': {},
            'enums': {},
            'inputs': {},
            'scalars': {},
            'queries': {},
            'mutations': {},
            'subscriptions': {},
            'directives': []
        }
        # Basic parsing: extract type definitions
        # This is a simplified parser - full parser would use graphql-core library
        lines = sdl.split('\n')
        current_type: str | None = None
        current_kind: str | None = None
        in_block = False
        for line in lines:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            # Detect type definitions
            if line.startswith('type '):
                # Extract type name
                type_name = line[5:].split(' ')[0].split('(')[0].split('{')[0].strip()
                if type_name:
                    current_type = type_name
                    current_kind = 'type'
                    result['types'][type_name] = {
                        'name': type_name,
                        'fields': {},
                        'implements': [],
                        'directives': []
                    }
                    in_block = True
            elif line.startswith('interface '):
                interface_name = line[10:].split(' ')[0].split('(')[0].split('{')[0].strip()
                if interface_name:
                    current_type = interface_name
                    current_kind = 'interface'
                    result['interfaces'][interface_name] = {
                        'name': interface_name,
                        'fields': {},
                        'directives': []
                    }
                    in_block = True
            elif line.startswith('enum '):
                enum_name = line[5:].split(' ')[0].split('{')[0].strip()
                if enum_name:
                    current_type = enum_name
                    current_kind = 'enum'
                    result['enums'][enum_name] = {
                        'name': enum_name,
                        'values': [],
                        'directives': []
                    }
                    in_block = True
            elif line.startswith('input '):
                input_name = line[6:].split(' ')[0].split('(')[0].split('{')[0].strip()
                if input_name:
                    current_type = input_name
                    current_kind = 'input'
                    result['inputs'][input_name] = {
                        'name': input_name,
                        'fields': {},
                        'directives': []
                    }
                    in_block = True
            elif line.startswith('scalar '):
                scalar_name = line[7:].split(' ')[0].strip()
                if scalar_name:
                    result['scalars'][scalar_name] = {
                        'name': scalar_name,
                        'directives': []
                    }
            elif line.startswith('directive @'):
                directive_name = line[11:].split(' ')[0].split('(')[0].split('(')[0].strip()
                if directive_name:
                    result['directives'].append(directive_name)
            elif line.startswith('schema '):
                # Schema definition
                if 'type Query' in line or 'query' in line.lower():
                    result['has_query'] = True
                if 'type Mutation' in line or 'mutation' in line.lower():
                    result['has_mutation'] = True
                if 'type Subscription' in line or 'subscription' in line.lower():
                    result['has_subscription'] = True
            elif line == '}' or line.endswith('}'):
                # End of block
                in_block = False
                current_type = None
                current_kind = None
            elif in_block and current_type and current_kind:
                # Parse field definitions within blocks
                if ':' in line and not line.startswith('#'):
                    # Field definition: name: Type
                    field_match = line.split(':')
                    if len(field_match) >= 2:
                        field_name = field_match[0].strip()
                        field_type = field_match[1].split('!')[0].strip().split('[')[0].strip()
                        if current_kind == 'type' and current_type in result['types']:
                            result['types'][current_type]['fields'][field_name] = {
                                'name': field_name,
                                'type': field_type,
                                'required': '!' in field_match[1],
                                'list': '[' in field_match[1]
                            }
                        elif current_kind == 'interface' and current_type in result['interfaces']:
                            result['interfaces'][current_type]['fields'][field_name] = {
                                'name': field_name,
                                'type': field_type,
                                'required': '!' in field_match[1],
                                'list': '[' in field_match[1]
                            }
                        elif current_kind == 'input' and current_type in result['inputs']:
                            result['inputs'][current_type]['fields'][field_name] = {
                                'name': field_name,
                                'type': field_type,
                                'required': '!' in field_match[1],
                                'list': '[' in field_match[1]
                            }
                        elif current_kind == 'enum' and current_type in result['enums']:
                            # Enum value
                            enum_value = field_name
                            result['enums'][current_type]['values'].append(enum_value)
        return result
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
        Implements basic GraphQL SDL generation from dict structure.
        """
        lines = []
        # Extract types
        types = schema_dict.get('types', {})
        if isinstance(types, dict):
            for type_name, type_def in types.items():
                if isinstance(type_def, dict):
                    type_kind = type_def.get('kind', 'type')
                    if type_kind == 'OBJECT' or 'fields' in type_def:
                        lines.append(f"type {type_name} {{")
                        fields = type_def.get('fields', {})
                        if isinstance(fields, dict):
                            for field_name, field_def in fields.items():
                                if isinstance(field_def, dict):
                                    field_type = field_def.get('type', 'String')
                                    if isinstance(field_type, dict):
                                        field_type = field_type.get('name', 'String')
                                    required = field_def.get('required', False)
                                    field_type_str = f"{field_type}!" if required else field_type
                                    lines.append(f"  {field_name}: {field_type_str}")
                                else:
                                    lines.append(f"  {field_name}: {field_def}")
                        lines.append("}")
                        lines.append("")
                    elif type_kind == 'ENUM' or 'values' in type_def:
                        lines.append(f"enum {type_name} {{")
                        values = type_def.get('values', [])
                        for value in values:
                            if isinstance(value, dict):
                                lines.append(f"  {value.get('name', value)}")
                            else:
                                lines.append(f"  {value}")
                        lines.append("}")
                        lines.append("")
                    elif type_kind == 'INTERFACE' or 'interface' in type_def:
                        lines.append(f"interface {type_name} {{")
                        fields = type_def.get('fields', {})
                        if isinstance(fields, dict):
                            for field_name, field_def in fields.items():
                                if isinstance(field_def, dict):
                                    field_type = field_def.get('type', 'String')
                                    if isinstance(field_type, dict):
                                        field_type = field_type.get('name', 'String')
                                    lines.append(f"  {field_name}: {field_type}")
                        lines.append("}")
                        lines.append("")
        # Extract queries and mutations
        query_type = schema_dict.get('queryType', {})
        if isinstance(query_type, dict) and query_type.get('name'):
            lines.insert(0, f"type Query {{")
            lines.insert(1, "  # Query fields")
            lines.insert(2, "}")
            lines.insert(3, "")
        mutation_type = schema_dict.get('mutationType', {})
        if isinstance(mutation_type, dict) and mutation_type.get('name'):
            lines.append("type Mutation {")
            lines.append("  # Mutation fields")
            lines.append("}")
            lines.append("")
        if not lines:
            return "# GraphQL Schema\n# Generated from dict\n"
        return "\n".join(lines)
