#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/formats/schema/protobuf_schema.py
Protobuf Schema Serializer
Extends xwsystem.io.serialization for Protocol Buffers schema support.
Basic implementation - full Protobuf IDL parser can be added later.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.3
Generation Date: 09-Nov-2025
"""

from typing import Any
from pathlib import Path
from exonware.xwsystem.io.serialization.contracts import EncodeOptions, DecodeOptions
from exonware.xwsystem.io.defs import CodecCapability
from exonware.xwsystem.io.serialization.errors import SerializationError
from exonware.xwsystem import get_logger
from ..base import ASchemaSerialization
logger = get_logger(__name__)


class ProtobufSchemaSerializer(ASchemaSerialization):
    """
    Protobuf Schema serializer - fully reuses xwsystem serialization infrastructure.
    Uses xwsystem serialization contracts and capabilities.
    No manual serialization - all delegated to xwsystem.
    """
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

    def encode(self, value: Any, *, options: EncodeOptions | None = None) -> bytes | str:
        """
        Encode Protobuf schema to string.
        Protobuf uses IDL (Interface Definition Language) text format.
        For dict values, converts to Protobuf IDL format.
        Note: This is schema-specific conversion, not general serialization.
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

    def decode(self, repr: bytes | str, *, options: DecodeOptions | None = None) -> Any:
        """
        Decode Protobuf schema from string.
        Parses Protobuf IDL into structured format (basic implementation).
        Returns a structured dictionary representation of the Protobuf schema.
        """
        if isinstance(repr, bytes):
            repr = repr.decode('utf-8')
        # Validate it's valid Protobuf IDL
        self._validate_protobuf_schema(repr)
        # Parse Protobuf IDL into structured format
        # Basic implementation: extracts messages, fields, enums, services
        return self._parse_protobuf_idl(repr)

    def _parse_protobuf_idl(self, idl: str) -> dict[str, Any]:
        """
        Parse Protobuf IDL into structured format.
        Basic implementation that extracts:
        - Syntax version (proto2/proto3)
        - Package name
        - Messages with fields and types
        - Enums with values
        - Services with RPC methods
        - Imports
        Args:
            idl: Protobuf IDL string
        Returns:
            Structured dictionary representation
        """
        result: dict[str, Any] = {
            'type': 'protobuf',
            'idl_content': idl,
            'syntax': 'proto3',  # Default
            'package': None,
            'messages': {},
            'enums': {},
            'services': {},
            'imports': []
        }
        # Basic parsing: extract protobuf definitions
        # This is a simplified parser - full parser would use protobuf library
        lines = idl.split('\n')
        current_message: str | None = None
        current_enum: str | None = None
        current_service: str | None = None
        in_block = False
        brace_level = 0
        for line in lines:
            original_line = line
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('//') or line.startswith('/*'):
                continue
            # Remove inline comments
            if '//' in line:
                line = line.split('//')[0].strip()
            # Detect syntax version
            if line.startswith('syntax = '):
                raw = line.split('=', 1)[1].strip().strip('"\';')
                result['syntax'] = raw if raw else 'proto3'
            # Detect package
            elif line.startswith('package '):
                package_match = line[8:].strip().rstrip(';').strip()
                result['package'] = package_match
            # Detect imports
            elif line.startswith('import '):
                import_match = line[7:].strip().rstrip(';').strip().strip('"').strip("'")
                result['imports'].append(import_match)
            # Detect message definitions
            elif line.startswith('message '):
                message_name = line[8:].split(' ')[0].split('{')[0].strip()
                if message_name:
                    current_message = message_name
                    current_enum = None
                    current_service = None
                    result['messages'][message_name] = {
                        'name': message_name,
                        'fields': {},
                        'nested_messages': {},
                        'nested_enums': {},
                        'oneofs': {},
                        'options': {}
                    }
                    in_block = True
                    brace_level = original_line.count('{') - original_line.count('}')
            # Detect enum definitions
            elif line.startswith('enum '):
                enum_name = line[5:].split(' ')[0].split('{')[0].strip()
                if enum_name:
                    current_enum = enum_name
                    current_message = None
                    current_service = None
                    if current_message and current_message in result['messages']:
                        # Nested enum
                        result['messages'][current_message]['nested_enums'][enum_name] = {
                            'name': enum_name,
                            'values': []
                        }
                    else:
                        result['enums'][enum_name] = {
                            'name': enum_name,
                            'values': []
                        }
                    in_block = True
                    brace_level = original_line.count('{') - original_line.count('}')
            # Detect service definitions
            elif line.startswith('service '):
                service_name = line[8:].split(' ')[0].split('{')[0].strip()
                if service_name:
                    current_service = service_name
                    current_message = None
                    current_enum = None
                    result['services'][service_name] = {
                        'name': service_name,
                        'methods': {}
                    }
                    in_block = True
                    brace_level = original_line.count('{') - original_line.count('}')
            # Track brace levels
            if '{' in original_line:
                brace_level += original_line.count('{')
            if '}' in original_line:
                brace_level -= original_line.count('}')
                if brace_level <= 0:
                    # End of block
                    in_block = False
                    brace_level = 0
                    if current_message:
                        current_message = None
                    if current_enum:
                        current_enum = None
                    if current_service:
                        current_service = None
            # Parse field definitions in messages
            elif in_block and current_message and current_message in result['messages']:
                # Field format: [optional/repeated] type field_name = field_number [options];
                # Or: oneof name { ... }
                if line.startswith('oneof '):
                    oneof_name = line[6:].split(' ')[0].split('{')[0].strip()
                    if oneof_name:
                        result['messages'][current_message]['oneofs'][oneof_name] = {
                            'name': oneof_name,
                            'fields': {}
                        }
                elif not line.startswith('{') and not line.startswith('}') and '=' in line:
                    # Try to parse field
                    parts = line.split('=')
                    if len(parts) >= 2:
                        left_part = parts[0].strip()
                        right_part = parts[1].split(';')[0].strip()
                        field_number = right_part.split()[0] if right_part.split() else None
                        # Extract field name and type
                        left_parts = left_part.split()
                        if len(left_parts) >= 2:
                            field_type = left_parts[-2]  # Second to last (before name)
                            field_name = left_parts[-1]  # Last
                            # Check for optional/repeated
                            is_repeated = 'repeated' in left_part.lower()
                            is_optional = 'optional' in left_part.lower()
                            if field_name and field_number:
                                result['messages'][current_message]['fields'][field_name] = {
                                    'name': field_name,
                                    'type': field_type,
                                    'number': int(field_number),
                                    'repeated': is_repeated,
                                    'optional': is_optional
                                }
            # Parse enum values
            elif in_block and current_enum:
                # Enum value format: NAME = value;
                if '=' in line and not line.startswith('option'):
                    enum_parts = line.split('=')
                    if len(enum_parts) >= 2:
                        enum_name_val = enum_parts[0].strip()
                        enum_value = enum_parts[1].split(';')[0].strip()
                        if current_message and current_message in result['messages']:
                            if current_enum in result['messages'][current_message]['nested_enums']:
                                result['messages'][current_message]['nested_enums'][current_enum]['values'].append({
                                    'name': enum_name_val,
                                    'value': int(enum_value) if enum_value.isdigit() else enum_value
                                })
                        elif current_enum in result['enums']:
                            result['enums'][current_enum]['values'].append({
                                'name': enum_name_val,
                                'value': int(enum_value) if enum_value.isdigit() else enum_value
                            })
            # Parse service methods (RPC)
            elif in_block and current_service and current_service in result['services']:
                # RPC format: rpc MethodName (RequestType) returns (ResponseType);
                if line.startswith('rpc '):
                    rpc_parts = line[4:].split('(')
                    if len(rpc_parts) >= 2:
                        method_name = rpc_parts[0].strip()
                        request_type = rpc_parts[1].split(')')[0].strip()
                        response_part = line.split('returns')
                        response_type = None
                        if len(response_part) >= 2:
                            response_type = response_part[1].split('(')[1].split(')')[0].strip() if '(' in response_part[1] else None
                        if method_name:
                            result['services'][current_service]['methods'][method_name] = {
                                'name': method_name,
                                'request_type': request_type,
                                'response_type': response_type
                            }
        return result
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
        Implements basic Protobuf IDL generation from dict structure.
        """
        lines = ["syntax = \"proto3\";", ""]
        # Extract package
        package = schema_dict.get('package')
        if package:
            lines.append(f"package {package};")
            lines.append("")
        # Extract messages
        messages = schema_dict.get('messages', {})
        if isinstance(messages, dict):
            for message_name, message_def in messages.items():
                if isinstance(message_def, dict):
                    lines.append(f"message {message_name} {{")
                    fields = message_def.get('fields', {})
                    if isinstance(fields, dict):
                        field_number = 1
                        for field_name, field_def in fields.items():
                            if isinstance(field_def, dict):
                                field_type = field_def.get('type', 'string')
                                field_number = field_def.get('number', field_number)
                                repeated = field_def.get('repeated', False)
                                optional = field_def.get('optional', False)
                                type_prefix = "repeated " if repeated else ("optional " if optional else "")
                                lines.append(f"  {type_prefix}{field_type} {field_name} = {field_number};")
                                field_number += 1
                            else:
                                lines.append(f"  {field_def} {field_name} = {field_number};")
                                field_number += 1
                    lines.append("}")
                    lines.append("")
        # Extract enums
        enums = schema_dict.get('enums', {})
        if isinstance(enums, dict):
            for enum_name, enum_def in enums.items():
                if isinstance(enum_def, dict):
                    lines.append(f"enum {enum_name} {{")
                    values = enum_def.get('values', {})
                    if isinstance(values, dict):
                        for value_name, value_number in values.items():
                            lines.append(f"  {value_name} = {value_number};")
                    lines.append("}")
                    lines.append("")
        if len(lines) <= 2:
            return "syntax = \"proto3\";\n\n// Generated from dict\n"
        return "\n".join(lines)
