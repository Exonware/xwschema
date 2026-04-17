#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/builder.py
XWSchema Builder
Provides builder pattern for creating schemas with all properties from old MIGRAT implementation.
Supports all OpenAPI/JSON Schema properties.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.16
Generation Date: 09-Nov-2025
"""

from typing import Any
import inspect
from datetime import datetime
# Fully reuse xwsystem for logging
from exonware.xwsystem import get_logger
from .type_utils import class_to_string, normalize_type
logger = get_logger(__name__)
# Capture NoneType at module level to avoid shadowing issues
NoneType = type(None)


class XWSchemaBuilder:
    """
    Builder for creating XWSchema instances with all properties.
    Supports all properties from old MIGRAT implementation:
    - Basic: type, title, description, format, enum, default, nullable, deprecated, confidential
    - Field control: strict, alias, exclude
    - String constraints: pattern, length_min, length_max, strip_whitespace, to_upper, to_lower
    - Numeric constraints: value_min, value_max, value_min_exclusive, value_max_exclusive, value_multiple_of
    - Array constraints: items, items_min, items_max, items_unique
    - Object constraints: properties, required, properties_additional, properties_min, properties_max
    - Logical constraints: schema_all_of, schema_any_of, schema_one_of, schema_not
    - Conditional constraints: schema_if, schema_then, schema_else
    - Content constraints: content_encoding, content_media_type, content_schema
    - Metadata: example, examples
    - References: ref, anchor
    """
    @staticmethod

    def build_schema_dict(
        # Basic properties
        type: type | str | None = None,
        title: str | None = None,
        description: str | None = None,
        format: str | None = None,
        enum: list[Any] | None = None,
        default: Any = None,
        nullable: bool = False,
        deprecated: bool = False,
        confidential: bool = False,
        # Field control
        strict: bool = False,
        alias: str | None = None,
        exclude: bool = False,
        # String constraints (OpenAPI standard naming)
        pattern: str | None = None,
        length_min: int | None = None,
        length_max: int | None = None,
        strip_whitespace: bool = False,
        to_upper: bool = False,
        to_lower: bool = False,
        # Numeric constraints (OpenAPI standard naming)
        value_min: int | float | None = None,
        value_max: int | float | None = None,
        value_min_exclusive: bool | float | int = False,
        value_max_exclusive: bool | float | int = False,
        value_multiple_of: int | float | None = None,
        # Array constraints (OpenAPI standard naming)
        items: dict[str, Any] | None = None,
        items_min: int | None = None,
        items_max: int | None = None,
        items_unique: bool = False,
        # Object constraints (OpenAPI standard naming)
        properties: dict[str, dict[str, Any]] | None = None,
        required: list[str] | None = None,
        properties_additional: bool | dict[str, Any] | None = None,
        properties_min: int | None = None,
        properties_max: int | None = None,
        # Logical constraints (OpenAPI standard naming)
        schema_all_of: list[dict[str, Any]] | None = None,
        schema_any_of: list[dict[str, Any]] | None = None,
        schema_one_of: list[dict[str, Any]] | None = None,
        schema_not: dict[str, Any] | None = None,
        # Conditional constraints (OpenAPI standard naming)
        schema_if: dict[str, Any] | None = None,
        schema_then: dict[str, Any] | None = None,
        schema_else: dict[str, Any] | None = None,
        # Content constraints
        content_encoding: str | None = None,
        content_media_type: str | None = None,
        content_schema: dict[str, Any] | None = None,
        # Metadata
        example: Any = None,
        examples: dict[str, Any] | None = None,
        # References
        ref: str | None = None,
        anchor: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Build a JSON Schema dict from all properties.
        """
        schema_dict: dict[str, Any] = {}
        # Convert Python type to JSON Schema type string
        type_map = {
            str: 'string',
            int: 'integer',
            float: 'number',
            bool: 'boolean',
            dict: 'object',
            list: 'array',
            tuple: 'array',
            NoneType: 'null'
        }
        # Basic properties
        if type is not None:
            # Built-in types -> JSON Schema type name; other classes -> string representation
            if type in type_map:
                schema_dict['type'] = type_map[type]
            elif isinstance(type, str):
                schema_dict['type'] = type
            elif inspect.isclass(type):
                schema_dict['type'] = class_to_string(type)
            else:
                schema_dict['type'] = normalize_type(type)
        if title:
            schema_dict['title'] = title
        if description:
            schema_dict['description'] = description
        if format:
            schema_dict['format'] = format
        if enum:
            schema_dict['enum'] = enum
        if default is not None:
            schema_dict['default'] = default
        if nullable:
            schema_dict['nullable'] = nullable
        if deprecated:
            schema_dict['deprecated'] = deprecated
        if confidential:
            schema_dict['x-confidential'] = confidential  # Custom extension
        # Field control (custom extensions)
        if strict:
            schema_dict['x-strict'] = strict
        if alias:
            schema_dict['x-alias'] = alias
        if exclude:
            schema_dict['x-exclude'] = exclude
        # String constraints
        if pattern:
            schema_dict['pattern'] = pattern
        if length_min is not None:
            schema_dict['minLength'] = length_min
        if length_max is not None:
            schema_dict['maxLength'] = length_max
        if strip_whitespace:
            schema_dict['stripWhitespace'] = strip_whitespace
        if to_upper:
            schema_dict['toUpper'] = to_upper
        if to_lower:
            schema_dict['toLower'] = to_lower
        # Numeric constraints
        if value_min is not None:
            if isinstance(value_min_exclusive, (int, float)) and not isinstance(value_min_exclusive, bool):
                schema_dict['exclusiveMinimum'] = value_min_exclusive
            elif value_min_exclusive:
                schema_dict['exclusiveMinimum'] = True
                schema_dict['minimum'] = value_min
            else:
                schema_dict['minimum'] = value_min
        elif value_min_exclusive and isinstance(value_min_exclusive, bool):
            # Handle case where value_min_exclusive is True but value_min is None
            # This sets exclusiveMinimum flag without a minimum value (edge case)
            schema_dict['exclusiveMinimum'] = True
        if value_max is not None:
            if isinstance(value_max_exclusive, (int, float)) and not isinstance(value_max_exclusive, bool):
                schema_dict['exclusiveMaximum'] = value_max_exclusive
            elif value_max_exclusive:
                schema_dict['exclusiveMaximum'] = True
                schema_dict['maximum'] = value_max
            else:
                schema_dict['maximum'] = value_max
        elif value_max_exclusive and isinstance(value_max_exclusive, bool):
            # Handle case where value_max_exclusive is True but value_max is None
            # This sets exclusiveMaximum flag without a maximum value (edge case)
            schema_dict['exclusiveMaximum'] = True
        if value_multiple_of is not None:
            schema_dict['multipleOf'] = value_multiple_of
        # Array constraints
        if items:
            schema_dict['items'] = items
        if items_min is not None:
            schema_dict['minItems'] = items_min
        if items_max is not None:
            schema_dict['maxItems'] = items_max
        if items_unique:
            schema_dict['uniqueItems'] = items_unique
        # Object constraints
        if properties:
            schema_dict['properties'] = properties
        if required:
            schema_dict['required'] = required
        if properties_additional is not None:
            if isinstance(properties_additional, bool):
                schema_dict['additionalProperties'] = properties_additional
            else:
                schema_dict['additionalProperties'] = properties_additional
        if properties_min is not None:
            schema_dict['minProperties'] = properties_min
        if properties_max is not None:
            schema_dict['maxProperties'] = properties_max
        # Logical constraints
        if schema_all_of:
            schema_dict['allOf'] = schema_all_of
        if schema_any_of:
            schema_dict['anyOf'] = schema_any_of
        if schema_one_of:
            schema_dict['oneOf'] = schema_one_of
        if schema_not:
            schema_dict['not'] = schema_not
        # Conditional constraints
        if schema_if:
            schema_dict['if'] = schema_if
        if schema_then:
            schema_dict['then'] = schema_then
        if schema_else:
            schema_dict['else'] = schema_else
        # Content constraints
        if content_encoding:
            schema_dict['contentEncoding'] = content_encoding
        if content_media_type:
            schema_dict['contentMediaType'] = content_media_type
        if content_schema:
            schema_dict['contentSchema'] = content_schema
        # Metadata
        if example is not None:
            schema_dict['example'] = example
        if examples:
            schema_dict['examples'] = examples
        # References
        if ref:
            schema_dict['$ref'] = ref
        if anchor:
            schema_dict['$anchor'] = anchor
        # Custom properties from extra keyword arguments
        if kwargs:
            schema_dict.update(kwargs)
        return schema_dict
