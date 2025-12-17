#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/builder.py

XWSchema Builder

Provides builder pattern for creating schemas with all properties from old MIGRAT implementation.
Supports all OpenAPI/JSON Schema properties with backward compatibility aliases.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from typing import Any, Optional, Union
from datetime import datetime
from exonware.xwsystem import get_logger

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
        type: Optional[Union[type, str]] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        format: Optional[str] = None,
        enum: Optional[list[Any]] = None,
        default: Any = None,
        nullable: bool = False,
        deprecated: bool = False,
        confidential: bool = False,
        
        # Field control
        strict: bool = False,
        alias: Optional[str] = None,
        exclude: bool = False,
        
        # String constraints (OpenAPI standard naming)
        pattern: Optional[str] = None,
        length_min: Optional[int] = None,
        length_max: Optional[int] = None,
        strip_whitespace: bool = False,
        to_upper: bool = False,
        to_lower: bool = False,
        
        # Numeric constraints (OpenAPI standard naming)
        value_min: Optional[Union[int, float]] = None,
        value_max: Optional[Union[int, float]] = None,
        value_min_exclusive: Union[bool, float, int] = False,
        value_max_exclusive: Union[bool, float, int] = False,
        value_multiple_of: Optional[Union[int, float]] = None,
        
        # Array constraints (OpenAPI standard naming)
        items: Optional[dict[str, Any]] = None,
        items_min: Optional[int] = None,
        items_max: Optional[int] = None,
        items_unique: bool = False,
        
        # Object constraints (OpenAPI standard naming)
        properties: Optional[dict[str, dict[str, Any]]] = None,
        required: Optional[list[str]] = None,
        properties_additional: Optional[Union[bool, dict[str, Any]]] = None,
        properties_min: Optional[int] = None,
        properties_max: Optional[int] = None,
        
        # Logical constraints (OpenAPI standard naming)
        schema_all_of: Optional[list[dict[str, Any]]] = None,
        schema_any_of: Optional[list[dict[str, Any]]] = None,
        schema_one_of: Optional[list[dict[str, Any]]] = None,
        schema_not: Optional[dict[str, Any]] = None,
        
        # Conditional constraints (OpenAPI standard naming)
        schema_if: Optional[dict[str, Any]] = None,
        schema_then: Optional[dict[str, Any]] = None,
        schema_else: Optional[dict[str, Any]] = None,
        
        # Content constraints
        content_encoding: Optional[str] = None,
        content_media_type: Optional[str] = None,
        content_schema: Optional[dict[str, Any]] = None,
        
        # Metadata
        example: Any = None,
        examples: Optional[dict[str, Any]] = None,
        
        # References
        ref: Optional[str] = None,
        anchor: Optional[str] = None,
        
        # Backward compatibility aliases
        **kwargs
    ) -> dict[str, Any]:
        """
        Build a JSON Schema dict from all properties.
        
        Supports backward compatibility aliases:
        - min_length -> length_min
        - max_length -> length_max
        - minimum -> value_min
        - maximum -> value_max
        - min_items -> items_min
        - max_items -> items_max
        - additional_properties -> properties_additional
        - all_of -> schema_all_of
        - any_of -> schema_any_of
        - one_of -> schema_one_of
        - not_ -> schema_not
        """
        
        # Handle backward compatibility aliases
        if 'min_length' in kwargs and length_min is None:
            length_min = kwargs.pop('min_length')
        if 'max_length' in kwargs and length_max is None:
            length_max = kwargs.pop('max_length')
        if 'minimum' in kwargs and value_min is None:
            value_min = kwargs.pop('minimum')
        if 'maximum' in kwargs and value_max is None:
            value_max = kwargs.pop('maximum')
        if 'min_items' in kwargs and items_min is None:
            items_min = kwargs.pop('min_items')
        if 'max_items' in kwargs and items_max is None:
            items_max = kwargs.pop('max_items')
        if 'additional_properties' in kwargs and properties_additional is None:
            properties_additional = kwargs.pop('additional_properties')
        if 'all_of' in kwargs and schema_all_of is None:
            schema_all_of = kwargs.pop('all_of')
        if 'any_of' in kwargs and schema_any_of is None:
            schema_any_of = kwargs.pop('any_of')
        if 'one_of' in kwargs and schema_one_of is None:
            schema_one_of = kwargs.pop('one_of')
        if 'not_' in kwargs and schema_not is None:
            schema_not = kwargs.pop('not_')
        
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
            if isinstance(type, str):
                schema_dict['type'] = type
            elif type in type_map:
                schema_dict['type'] = type_map[type]
            else:
                schema_dict['type'] = str(type)
        
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
        
        # Custom properties from kwargs
        schema_dict.update(kwargs)
        
        return schema_dict

