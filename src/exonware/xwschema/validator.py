#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/validator.py

XWSchema Validator Implementation

This module provides schema validation implementation that reuses:
- XWData for efficient data navigation
- XWSystem.validation.contracts.ISchemaValidator interface
- XWSystem validation utilities

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

import re
from typing import Any, Optional
from dataclasses import dataclass
from exonware.xwsystem import get_logger

# Reuse XWData for data navigation
try:
    from exonware.xwdata import XWData
except ImportError:
    XWData = None

# Reuse XWSystem validation interface
try:
    from exonware.xwsystem.validation.contracts import ISchemaValidator as XWSystemISchemaValidator
except ImportError:
    XWSystemISchemaValidator = None

from .contracts import ISchemaValidator
from .errors import XWSchemaValidationError, XWSchemaTypeError, XWSchemaConstraintError
from .defs import ValidationMode

logger = get_logger(__name__)


@dataclass
class ValidationIssue:
    """Structured validation issue with node path and issue type."""
    node_path: str  # JSON Pointer-style path (e.g., "/users/0/name", "/age")
    issue_type: str  # Type of issue (e.g., "type_mismatch", "missing_required", "constraint_violation")
    message: str  # Human-readable error message


class XWSchemaValidator(ISchemaValidator):
    """
    Schema validator implementation.
    
    Reuses XWData for efficient data navigation and XWSystem validation utilities.
    Implements ISchemaValidator interface for consistency.
    """
    
    def __init__(self, mode: ValidationMode = ValidationMode.STRICT):
        """Initialize validator."""
        self._mode = mode
        self._validation_cache: dict[str, tuple[bool, list[str]]] = {}
        
        logger.debug(f"XWSchemaValidator initialized (mode: {mode})")
    
    def validate_schema(self, data: Any, schema: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate data against schema.
        
        Reuses XWData for efficient path-based validation when data is XWData instance.
        
        Args:
            data: Data to validate (can be dict, list, or XWData instance)
            schema: Schema definition (JSON Schema format)
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            # Convert XWData to native if needed for validation
            if XWData and isinstance(data, XWData):
                # Use XWData for efficient navigation during validation
                return self._validate_with_xwdata(data, schema)
            else:
                # Standard validation for native Python types
                return self._validate_native(data, schema)
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False, [f"Validation failed: {str(e)}"]
    
    def validate_schema_issues(self, data: Any, schema: dict[str, Any], path: str = "") -> list[ValidationIssue]:
        """
        Validate data against schema and return structured issues.
        
        Args:
            data: Data to validate (can be dict, list, or XWData instance)
            schema: Schema definition (JSON Schema format)
            path: Current JSON Pointer path (default: "" for root)
            
        Returns:
            List of ValidationIssue objects with node_path and issue_type
        """
        issues: list[ValidationIssue] = []
        
        try:
            # Convert XWData to native if needed
            if XWData and isinstance(data, XWData):
                native_data = data.to_native()
            else:
                native_data = data
            
            # Validate and collect issues
            issues.extend(self._validate_native_issues(native_data, schema, path))
        except Exception as e:
            logger.error(f"Validation error: {e}")
            issues.append(ValidationIssue(
                node_path=path or "/",
                issue_type="validation_error",
                message=f"Validation failed: {str(e)}"
            ))
        
        return issues
    
    def _validate_native_issues(self, data: Any, schema: dict[str, Any], path: str = "") -> list[ValidationIssue]:
        """Validate native Python data structure and return structured issues."""
        issues: list[ValidationIssue] = []
        
        # Get schema type
        schema_type = schema.get('type')
        nullable = schema.get('nullable', False)
        
        # Handle nullable
        if nullable and data is None:
            return issues
        
        if schema_type:
            # Check null when nullable is False
            if not nullable and data is None:
                if schema_type != 'null' and not (isinstance(schema_type, list) and 'null' in schema_type):
                    issues.append(ValidationIssue(
                        node_path=path or "/",
                        issue_type="null_not_allowed",
                        message=f"Value is null but nullable is False and type '{schema_type}' does not include 'null'"
                    ))
                    return issues
            
            # Check type mismatch
            if data is not None and not self._validate_type_value(data, schema_type):
                issues.append(ValidationIssue(
                    node_path=path or "/",
                    issue_type="type_mismatch",
                    message=f"Type mismatch: expected '{schema_type}', got '{type(data).__name__}'"
                ))
                return issues
        
        # Validate enum
        if 'enum' in schema and data not in schema['enum']:
            issues.append(ValidationIssue(
                node_path=path or "/",
                issue_type="enum_violation",
                message=f"Value '{data}' not in enum {schema['enum']}"
            ))
        
        # Validate string constraints
        if schema_type == 'string' and isinstance(data, str):
            if 'minLength' in schema and len(data) < schema['minLength']:
                issues.append(ValidationIssue(
                    node_path=path or "/",
                    issue_type="min_length_violation",
                    message=f"String length {len(data)} < minLength {schema['minLength']}"
                ))
            if 'maxLength' in schema and len(data) > schema['maxLength']:
                issues.append(ValidationIssue(
                    node_path=path or "/",
                    issue_type="max_length_violation",
                    message=f"String length {len(data)} > maxLength {schema['maxLength']}"
                ))
            if 'pattern' in schema:
                if not self.validate_pattern(data, schema['pattern']):
                    issues.append(ValidationIssue(
                        node_path=path or "/",
                        issue_type="pattern_violation",
                        message=f"String does not match pattern '{schema['pattern']}'"
                    ))
        
        # Validate number constraints
        if schema_type in ('number', 'integer') and isinstance(data, (int, float)):
            if 'minimum' in schema and data < schema['minimum']:
                issues.append(ValidationIssue(
                    node_path=path or "/",
                    issue_type="minimum_violation",
                    message=f"Value {data} < minimum {schema['minimum']}"
                ))
            if 'maximum' in schema and data > schema['maximum']:
                issues.append(ValidationIssue(
                    node_path=path or "/",
                    issue_type="maximum_violation",
                    message=f"Value {data} > maximum {schema['maximum']}"
                ))
            if 'multipleOf' in schema:
                if data % schema['multipleOf'] != 0:
                    issues.append(ValidationIssue(
                        node_path=path or "/",
                        issue_type="multiple_of_violation",
                        message=f"Value {data} is not a multiple of {schema['multipleOf']}"
                    ))
        
        # Validate object properties
        if schema_type == 'object' and isinstance(data, dict):
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            additional_properties = schema.get('additionalProperties', True)
            
            # Check minProperties and maxProperties
            num_properties = len(data)
            if 'minProperties' in schema and num_properties < schema['minProperties']:
                issues.append(ValidationIssue(
                    node_path=path or "/",
                    issue_type="min_properties_violation",
                    message=f"Object has {num_properties} properties, but minProperties is {schema['minProperties']}"
                ))
            if 'maxProperties' in schema and num_properties > schema['maxProperties']:
                issues.append(ValidationIssue(
                    node_path=path or "/",
                    issue_type="max_properties_violation",
                    message=f"Object has {num_properties} properties, but maxProperties is {schema['maxProperties']}"
                ))
            
            # Check required fields
            for field in required:
                if field not in data:
                    field_path = f"{path}/{field}" if path else f"/{field}"
                    issues.append(ValidationIssue(
                        node_path=field_path,
                        issue_type="missing_required",
                        message=f"Required field '{field}' is missing"
                    ))
            
            # Validate each property
            for field, field_schema in properties.items():
                if field in data:
                    field_path = f"{path}/{field}" if path else f"/{field}"
                    field_issues = self._validate_native_issues(data[field], field_schema, field_path)
                    issues.extend(field_issues)
            
            # Check additionalProperties
            if additional_properties is False:
                for field in data:
                    if field not in properties:
                        field_path = f"{path}/{field}" if path else f"/{field}"
                        issues.append(ValidationIssue(
                            node_path=field_path,
                            issue_type="additional_property_not_allowed",
                            message=f"Additional property '{field}' is not allowed (additionalProperties: false)"
                        ))
            elif isinstance(additional_properties, dict):
                for field in data:
                    if field not in properties:
                        field_path = f"{path}/{field}" if path else f"/{field}"
                        field_issues = self._validate_native_issues(data[field], additional_properties, field_path)
                        issues.extend(field_issues)
        
        # Validate array items
        if schema_type == 'array' and isinstance(data, list):
            items_schema = schema.get('items', {})
            if 'minItems' in schema and len(data) < schema['minItems']:
                issues.append(ValidationIssue(
                    node_path=path or "/",
                    issue_type="min_items_violation",
                    message=f"Array length {len(data)} < minItems {schema['minItems']}"
                ))
            if 'maxItems' in schema and len(data) > schema['maxItems']:
                issues.append(ValidationIssue(
                    node_path=path or "/",
                    issue_type="max_items_violation",
                    message=f"Array length {len(data)} > maxItems {schema['maxItems']}"
                ))
            if schema.get('uniqueItems', False):
                seen = set()
                for i, item in enumerate(data):
                    try:
                        item_key = (item,) if isinstance(item, (str, int, float, bool, type(None))) else tuple(item) if isinstance(item, (list, tuple)) else str(item)
                    except TypeError:
                        item_key = str(item)
                    if item_key in seen:
                        item_path = f"{path}/{i}" if path else f"/{i}"
                        issues.append(ValidationIssue(
                            node_path=item_path,
                            issue_type="unique_items_violation",
                            message=f"Array item at index {i} is duplicate (uniqueItems constraint violated)"
                        ))
                    seen.add(item_key)
            
            for i, item in enumerate(data):
                item_path = f"{path}/{i}" if path else f"/{i}"
                item_issues = self._validate_native_issues(item, items_schema, item_path)
                issues.extend(item_issues)
        
        return issues
    
    def _validate_with_xwdata(self, data: XWData, schema: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate XWData instance using efficient path navigation."""
        errors: list[str] = []
        
        # Get schema type
        schema_type = schema.get('type')
        if schema_type:
            # Validate root type
            native_data = data.to_native()
            if not self._validate_type_value(native_data, schema_type):
                errors.append(f"Type mismatch: expected '{schema_type}', got '{type(native_data).__name__}'")
        
        # Validate properties for objects
        if schema_type == 'object' or 'properties' in schema:
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            # Check required fields using XWData path navigation
            for field in required:
                try:
                    value = data[field]
                    if value is None:
                        errors.append(f"Required field '{field}' is missing or null")
                except (KeyError, IndexError):
                    errors.append(f"Required field '{field}' is missing")
            
            # Validate each property
            for field, field_schema in properties.items():
                try:
                    value = data[field]  # Efficient XWData path access
                    if value is not None:
                        is_valid, field_errors = self.validate_schema(value, field_schema)
                        if not is_valid:
                            errors.extend([f"{field}.{err}" for err in field_errors])
                except (KeyError, IndexError):
                    # Field not present - only error if required
                    if field in required:
                        errors.append(f"Required field '{field}' is missing")
        
        # Validate items for arrays
        if schema_type == 'array' or 'items' in schema:
            items_schema = schema.get('items', {})
            native_data = data.to_native()
            if isinstance(native_data, list):
                for i, item in enumerate(native_data):
                    is_valid, item_errors = self.validate_schema(item, items_schema)
                    if not is_valid:
                        errors.extend([f"[{i}].{err}" for err in item_errors])
        
        return len(errors) == 0, errors
    
    def _validate_native(self, data: Any, schema: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate native Python data structure."""
        errors: list[str] = []
        
        # Get schema type
        schema_type = schema.get('type')
        nullable = schema.get('nullable', False)
        
        # Handle nullable: if nullable is True, None is always valid
        if nullable and data is None:
            return True, []
        
        if schema_type:
            # If nullable is False and data is None, check if type includes 'null'
            if not nullable and data is None:
                # Check if type is explicitly 'null' or a list containing 'null'
                if schema_type == 'null' or (isinstance(schema_type, list) and 'null' in schema_type):
                    return True, []
                else:
                    errors.append(f"Value is null but nullable is False and type '{schema_type}' does not include 'null'")
                    return False, errors
            
            if not self._validate_type_value(data, schema_type):
                errors.append(f"Type mismatch: expected '{schema_type}', got '{type(data).__name__}'")
                return False, errors
        
        # Validate enum
        if 'enum' in schema:
            if data not in schema['enum']:
                errors.append(f"Value '{data}' not in enum {schema['enum']}")
        
        # Validate string constraints
        if schema_type == 'string' and isinstance(data, str):
            if 'minLength' in schema and len(data) < schema['minLength']:
                errors.append(f"String length {len(data)} < minLength {schema['minLength']}")
            if 'maxLength' in schema and len(data) > schema['maxLength']:
                errors.append(f"String length {len(data)} > maxLength {schema['maxLength']}")
            if 'pattern' in schema:
                if not self.validate_pattern(data, schema['pattern']):
                    errors.append(f"String does not match pattern '{schema['pattern']}'")
        
        # Validate number constraints
        if schema_type in ('number', 'integer') and isinstance(data, (int, float)):
            if 'minimum' in schema and data < schema['minimum']:
                errors.append(f"Value {data} < minimum {schema['minimum']}")
            if 'maximum' in schema and data > schema['maximum']:
                errors.append(f"Value {data} > maximum {schema['maximum']}")
            if 'multipleOf' in schema:
                if data % schema['multipleOf'] != 0:
                    errors.append(f"Value {data} is not a multiple of {schema['multipleOf']}")
        
        # Validate object properties
        if schema_type == 'object' and isinstance(data, dict):
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            additional_properties = schema.get('additionalProperties', True)
            
            # Check minProperties and maxProperties constraints
            num_properties = len(data)
            if 'minProperties' in schema and num_properties < schema['minProperties']:
                errors.append(f"Object has {num_properties} properties, but minProperties is {schema['minProperties']}")
            if 'maxProperties' in schema and num_properties > schema['maxProperties']:
                errors.append(f"Object has {num_properties} properties, but maxProperties is {schema['maxProperties']}")
            
            for field in required:
                if field not in data:
                    errors.append(f"Required field '{field}' is missing")
            
            for field, field_schema in properties.items():
                if field in data:
                    is_valid, field_errors = self.validate_schema(data[field], field_schema)
                    if not is_valid:
                        errors.extend([f"{field}.{err}" for err in field_errors])
            
            # Check additionalProperties constraint
            if additional_properties is False:
                # No additional properties allowed
                for field in data:
                    if field not in properties:
                        errors.append(f"Additional property '{field}' is not allowed (additionalProperties: false)")
            elif isinstance(additional_properties, dict):
                # Additional properties must conform to this schema
                for field in data:
                    if field not in properties:
                        is_valid, field_errors = self.validate_schema(data[field], additional_properties)
                        if not is_valid:
                            errors.extend([f"{field}.{err}" for err in field_errors])
        
        # Validate array items
        if schema_type == 'array' and isinstance(data, list):
            items_schema = schema.get('items', {})
            if 'minItems' in schema and len(data) < schema['minItems']:
                errors.append(f"Array length {len(data)} < minItems {schema['minItems']}")
            if 'maxItems' in schema and len(data) > schema['maxItems']:
                errors.append(f"Array length {len(data)} > maxItems {schema['maxItems']}")
            if schema.get('uniqueItems', False):
                # Check for duplicate items
                seen = set()
                for i, item in enumerate(data):
                    # Use tuple for hashable items, str representation for unhashable
                    try:
                        item_key = (item,) if isinstance(item, (str, int, float, bool, type(None))) else tuple(item) if isinstance(item, (list, tuple)) else str(item)
                    except TypeError:
                        item_key = str(item)
                    if item_key in seen:
                        errors.append(f"Array item at index {i} is duplicate (uniqueItems constraint violated)")
                    seen.add(item_key)
            
            for i, item in enumerate(data):
                is_valid, item_errors = self.validate_schema(item, items_schema)
                if not is_valid:
                    errors.extend([f"[{i}].{err}" for err in item_errors])
        
        return len(errors) == 0, errors
    
    def _validate_type_value(self, value: Any, expected_type: str) -> bool:
        """Validate value type."""
        return self.validate_type(value, expected_type)
    
    def validate_type(self, data: Any, expected_type: str) -> bool:
        """Validate data type."""
        type_map = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': (list, tuple),
            'object': dict,
            'null': type(None)
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return False
        
        if isinstance(expected_python_type, tuple):
            return isinstance(data, expected_python_type)
        return isinstance(data, expected_python_type)
    
    def validate_range(self, data: Any, min_value: Any, max_value: Any) -> bool:
        """Validate data range."""
        if not isinstance(data, (int, float)):
            return False
        return min_value <= data <= max_value
    
    def validate_pattern(self, data: str, pattern: str) -> bool:
        """Validate string pattern using regex."""
        try:
            return bool(re.match(pattern, data))
        except re.error:
            logger.warning(f"Invalid regex pattern: {pattern}")
            return False
    
    def create_schema(self, data: Any) -> dict[str, Any]:
        """
        Create schema from data.
        
        This is a basic implementation. Full schema generation is handled by XWSchemaGenerator.
        """
        if isinstance(data, dict):
            return {
                'type': 'object',
                'properties': {k: self.create_schema(v) for k, v in data.items()}
            }
        elif isinstance(data, (list, tuple)):
            if len(data) > 0:
                return {
                    'type': 'array',
                    'items': self.create_schema(data[0])
                }
            return {'type': 'array'}
        elif isinstance(data, str):
            return {'type': 'string'}
        elif isinstance(data, int):
            return {'type': 'integer'}
        elif isinstance(data, float):
            return {'type': 'number'}
        elif isinstance(data, bool):
            return {'type': 'boolean'}
        elif data is None:
            return {'type': 'null'}
        else:
            return {'type': 'string'}  # Default fallback

