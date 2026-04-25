#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/type_utils.py
Type Utilities for XWSchema
Provides bidirectional conversion between class types and string representations.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.19
Generation Date: 30-Dec-2025
"""

from typing import Any
import importlib
import inspect


def class_to_string(cls: type) -> str:
    """
    Convert a class to its string representation.
    Format: "module.path.ClassName"
    Supports:
    - Regular classes
    - ABC/Protocol classes
    - Built-in types (str, int, etc.)
    Args:
        cls: Class to convert
    Returns:
        String representation (e.g., "exonware.xwschema.XWSchema" or "builtins.str")
    """
    # Handle built-in types
    if cls in (str, int, float, bool, dict, list, tuple, type(None)):
        return f"builtins.{cls.__name__}"
    if not inspect.isclass(cls):
        raise TypeError(f"Expected a class, got {type(cls).__name__}")
    module = getattr(cls, '__module__', None)
    name = getattr(cls, '__name__', None)
    if not module or not name:
        raise ValueError(f"Cannot determine module or name for class {cls}")
    return f"{module}.{name}"


def string_to_class(class_string: str) -> type | None:
    """
    Convert a string representation to a class.
    Supports:
    - Custom classes: "exonware.xwschema.XWSchema"
    - Built-in types: "builtins.str", "builtins.int", etc.
    Args:
        class_string: String representation (e.g., "exonware.xwschema.XWSchema" or "builtins.str")
    Returns:
        Class object, or None for unknown builtin type name / malformed path (e.g. not exactly two parts).
    Raises:
        ImportError, AttributeError, ValueError: If the module or class cannot be loaded.
    """
    # Handle built-in types
    if class_string.startswith("builtins."):
        type_name = class_string.split(".", 1)[1]
        builtin_types = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "dict": dict,
            "list": list,
            "tuple": tuple,
            "NoneType": type(None),
            "None": type(None)
        }
        return builtin_types.get(type_name)
    # Split module path and class name
    parts = class_string.rsplit('.', 1)
    if len(parts) != 2:
        return None
    module_path, class_name = parts
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name, None)
    if cls is None or not inspect.isclass(cls):
        return None
    return cls


def normalize_type(type_value: Any) -> str | list[str] | dict[str, Any]:
    """
    Normalize a type value to string representation.
    Handles:
    - Class objects -> string representation
    - String -> string (unchanged)
    - List of classes/strings -> list of strings
    - Dict (anyOf/oneOf/etc.) -> normalized dict
    Args:
        type_value: Type value (class, string, list, or dict)
    Returns:
        Normalized type (string, list of strings, or dict)
    """
    if type_value is None:
        return None
    # Handle class objects: built-in -> JSON Schema type name; others -> class_to_string
    if inspect.isclass(type_value):
        builtin_to_json = {
            str: 'string', int: 'integer', float: 'number', bool: 'boolean',
            dict: 'object', list: 'array', tuple: 'array', type(None): 'null'
        }
        if type_value in builtin_to_json:
            return builtin_to_json[type_value]
        return class_to_string(type_value)
    # Handle strings (already normalized)
    if isinstance(type_value, str):
        return type_value
    # Handle lists (e.g., ["string", "null"] or [str, None])
    if isinstance(type_value, list):
        normalized = []
        for item in type_value:
            if inspect.isclass(item):
                normalized.append(class_to_string(item))
            elif item is None:
                normalized.append("null")
            else:
                normalized.append(str(item))
        return normalized
    # Handle dicts (e.g., anyOf, oneOf, etc.)
    if isinstance(type_value, dict):
        normalized = {}
        for key, value in type_value.items():
            if key == "type":
                normalized[key] = normalize_type(value)
            elif key in ("anyOf", "oneOf", "allOf"):
                # Recursively normalize nested schemas
                normalized[key] = [
                    normalize_schema_dict(item) if isinstance(item, dict) else item
                    for item in value
                ] if isinstance(value, list) else value
            else:
                normalized[key] = normalize_type(value) if isinstance(value, (type, str, list, dict)) else value
        return normalized
    # Fallback: convert to string
    return str(type_value)


def normalize_schema_dict(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize a schema dictionary, converting all class types to strings.
    Recursively processes the schema dict to convert:
    - Class objects in "type" field -> string representation
    - Class objects in nested schemas -> string representation
    Args:
        schema: Schema dictionary
    Returns:
        Normalized schema dictionary with all types as strings
    """
    if not isinstance(schema, dict):
        return schema
    normalized = {}
    for key, value in schema.items():
        if key == "type":
            normalized[key] = normalize_type(value)
        elif key in ("anyOf", "oneOf", "allOf", "not"):
            # Recursively normalize nested schemas
            if isinstance(value, list):
                normalized[key] = [
                    normalize_schema_dict(item) if isinstance(item, dict) else normalize_type(item)
                    for item in value
                ]
            elif isinstance(value, dict):
                normalized[key] = normalize_schema_dict(value)
            else:
                normalized[key] = value
        elif key == "items" and isinstance(value, dict):
            normalized[key] = normalize_schema_dict(value)
        elif key == "properties" and isinstance(value, dict):
            normalized[key] = {
                prop_name: normalize_schema_dict(prop_schema) if isinstance(prop_schema, dict) else prop_schema
                for prop_name, prop_schema in value.items()
            }
        elif isinstance(value, dict):
            normalized[key] = normalize_schema_dict(value)
        elif isinstance(value, list):
            normalized[key] = [
                normalize_schema_dict(item) if isinstance(item, dict) else normalize_type(item)
                for item in value
            ]
        else:
            # Check if value is a class
            if inspect.isclass(value):
                normalized[key] = class_to_string(value)
            else:
                normalized[key] = value
    return normalized


def denormalize_type(type_value: Any, resolve_classes: bool = False) -> Any:
    """
    Denormalize a type value, optionally converting strings back to classes.
    Args:
        type_value: Type value (string, list, or dict)
        resolve_classes: If True, convert string representations back to classes
    Returns:
        Denormalized type (class if resolve_classes=True, otherwise string)
    """
    if type_value is None:
        return None
    if not resolve_classes:
        return type_value
    # Handle strings - try to convert to class
    if isinstance(type_value, str):
        cls = string_to_class(type_value)
        return cls if cls is not None else type_value
    # Handle lists
    if isinstance(type_value, list):
        return [
            denormalize_type(item, resolve_classes=resolve_classes)
            for item in type_value
        ]
    # Handle dicts
    if isinstance(type_value, dict):
        denormalized = {}
        for key, value in type_value.items():
            if key == "type":
                denormalized[key] = denormalize_type(value, resolve_classes=resolve_classes)
            elif isinstance(value, (dict, list)):
                denormalized[key] = denormalize_type(value, resolve_classes=resolve_classes)
            else:
                denormalized[key] = value
        return denormalized
    return type_value
