#!/usr/bin/env python3
"""
✅ xSchema Validation Service
Schema validation logic extracted and adapted to service pattern.
"""

from typing import Any, Dict, List, Optional, Callable, Type
import re
from abc import ABC, abstractmethod

from src.xlib.xdata.core.exceptions import (
    ValidatorError, ValidatorRegistrationError, ValidatorNotFoundError,
    ValidationError, SchemaValidationError
)
from .config import SCHEMA_TYPE_MAPPING


class BaseValidator(ABC):
    """Base class for all validators."""
    
    @abstractmethod
    def validate(self, value: Any, schema: Dict[str, Any], context: 'ValidationContext') -> bool:
        """Validate a value against a schema."""
        pass


class StringValidator(BaseValidator):
    """Validator for string values."""
    
    def validate(self, value: Any, schema: Dict[str, Any], context: 'ValidationContext') -> bool:
        if not isinstance(value, str):
            context.add_error(
                f"Expected string, got {type(value).__name__}",
                value, schema, "type"
            )
            return False
            
        if schema.get('minLength') is not None and len(value) < schema['minLength']:
            context.add_error(
                f"String length {len(value)} is less than minimum {schema['minLength']}",
                value, schema, "min_length"
            )
            return False
            
        if schema.get('maxLength') is not None and len(value) > schema['maxLength']:
            context.add_error(
                f"String length {len(value)} is greater than maximum {schema['maxLength']}",
                value, schema, "max_length"
            )
            return False
            
        if schema.get('pattern') is not None:
            try:
                pattern = re.compile(schema['pattern'])
                if not pattern.match(value):
                    context.add_error(
                        f"String does not match pattern: {schema['pattern']}",
                        value, schema, "pattern"
                    )
                    return False
            except re.error as e:
                context.add_error(
                    f"Invalid pattern: {e}",
                    value, schema, "pattern_error"
                )
                return False
                
        if schema.get('enum') is not None and value not in schema['enum']:
            context.add_error(
                f"Value not in enum: {schema['enum']}",
                value, schema, "enum"
            )
            return False
            
        return True


class NumberValidator(BaseValidator):
    """Validator for number values."""
    
    def validate(self, value: Any, schema: Dict[str, Any], context: 'ValidationContext') -> bool:
        if not isinstance(value, (int, float)):
            context.add_error(
                f"Expected number, got {type(value).__name__}",
                value, schema, "type"
            )
            return False
            
        if schema.get('minimum') is not None:
            if schema.get('exclusiveMinimum', False):
                if value <= schema['minimum']:
                    context.add_error(
                        f"Value {value} is not greater than {schema['minimum']}",
                        value, schema, "minimum_exclusive"
                    )
                    return False
            else:
                if value < schema['minimum']:
                    context.add_error(
                        f"Value {value} is less than minimum {schema['minimum']}",
                        value, schema, "minimum"
                    )
                    return False
                    
        if schema.get('maximum') is not None:
            if schema.get('exclusiveMaximum', False):
                if value >= schema['maximum']:
                    context.add_error(
                        f"Value {value} is not less than {schema['maximum']}",
                        value, schema, "maximum_exclusive"
                    )
                    return False
            else:
                if value > schema['maximum']:
                    context.add_error(
                        f"Value {value} is greater than maximum {schema['maximum']}",
                        value, schema, "maximum"
                    )
                    return False
                    
        if schema.get('multipleOf') is not None:
            if value % schema['multipleOf'] != 0:
                context.add_error(
                    f"Value {value} is not a multiple of {schema['multipleOf']}",
                    value, schema, "multiple_of"
                )
                return False
                
        if schema.get('enum') is not None and value not in schema['enum']:
            context.add_error(
                f"Value not in enum: {schema['enum']}",
                value, schema, "enum"
            )
            return False
            
        return True


class ObjectValidator(BaseValidator):
    """Validator for object values."""
    
    def validate(self, value: Any, schema: Dict[str, Any], context: 'ValidationContext') -> bool:
        if not isinstance(value, dict):
            context.add_error(
                f"Expected object, got {type(value).__name__}",
                value, schema, "type"
            )
            return False
            
        # Check required properties
        required = schema.get('required', [])
        for prop in required:
            if prop not in value:
                context.add_error(
                    f"Required property '{prop}' is missing",
                    value, schema, "required"
                )
                return False
        
        # 🆕 OpenAPI 3.1.0: Validate property names
        property_names_schema = schema.get('propertyNames')
        if property_names_schema:
            for prop_name in value.keys():
                context.push_path(f"<{prop_name}>")
                if not self._validate_value(prop_name, property_names_schema, context):
                    return False
                context.pop_path()
                
        # Check property types
        properties = schema.get('properties', {})
        pattern_properties = schema.get('patternProperties', {})
        
        # Track which properties have been validated
        validated_properties = set()
        
        for prop_name, prop_value in value.items():
            context.push_path(prop_name)
            
            # Check if property matches a pattern
            pattern_matched = False
            for pattern, pattern_schema in pattern_properties.items():
                try:
                    import re
                    if re.match(pattern, prop_name):
                        pattern_matched = True
                        if not self._validate_value(prop_value, pattern_schema, context):
                            return False
                        break
                except re.error:
                    context.add_error(
                        f"Invalid regex pattern in patternProperties: {pattern}",
                        value, schema, "pattern_error"
                    )
                    return False
            
            # Check regular properties
            if prop_name in properties:
                validated_properties.add(prop_name)
                if not self._validate_value(prop_value, properties[prop_name], context):
                    return False
            elif not pattern_matched:
                # Check additional properties
                additional_props = schema.get('additionalProperties', True)
                if additional_props is False:
                    context.add_error(
                        f"Additional property '{prop_name}' not allowed",
                        value, schema, "additional_properties"
                    )
                    return False
                elif isinstance(additional_props, dict):
                    if not self._validate_value(prop_value, additional_props, context):
                        return False
            
            context.pop_path()
        
        # 🆕 OpenAPI 3.1.0: Validate dependent required
        dependent_required = schema.get('dependentRequired', {})
        for prop, required_deps in dependent_required.items():
            if prop in value:
                for dep in required_deps:
                    if dep not in value:
                        context.add_error(
                            f"Property '{dep}' is required when '{prop}' is present",
                            value, schema, "dependent_required"
                        )
                        return False
        
        # 🆕 OpenAPI 3.1.0: Validate dependent schemas
        dependent_schemas = schema.get('dependentSchemas', {})
        for prop, dep_schema in dependent_schemas.items():
            if prop in value:
                context.push_path(f"<dependent:{prop}>")
                if not self._validate_value(value, dep_schema, context):
                    return False
                context.pop_path()
        
        # 🆕 OpenAPI 3.1.0: Validate unevaluated properties
        unevaluated_props = schema.get('unevaluatedProperties')
        if unevaluated_props is False:
            # All properties must have been validated
            if len(validated_properties) != len(value):
                context.add_error(
                    "All properties must be explicitly defined or match patterns",
                    value, schema, "unevaluated_properties"
                )
                return False
        elif isinstance(unevaluated_props, dict):
            # Validate unevaluated properties against schema
            for prop_name, prop_value in value.items():
                if prop_name not in validated_properties:
                    context.push_path(prop_name)
                    if not self._validate_value(prop_value, unevaluated_props, context):
                        return False
                    context.pop_path()
        
        # Check min/max properties
        min_props = schema.get('minProperties')
        if min_props is not None and len(value) < min_props:
            context.add_error(
                f"Object has {len(value)} properties, minimum required is {min_props}",
                value, schema, "min_properties"
            )
            return False
            
        max_props = schema.get('maxProperties')
        if max_props is not None and len(value) > max_props:
            context.add_error(
                f"Object has {len(value)} properties, maximum allowed is {max_props}",
                value, schema, "max_properties"
            )
            return False
                
        return True
    
    def _validate_value(self, value: Any, schema: Dict[str, Any], context: 'ValidationContext') -> bool:
        """Helper method to validate a value against a schema."""
        validator = ValidatorRegistry.get(schema.get('type', 'any'))
        if validator:
            return validator().validate(value, schema, context)
        return True


class ArrayValidator(BaseValidator):
    """Validator for array values."""
    
    def validate(self, value: Any, schema: Dict[str, Any], context: 'ValidationContext') -> bool:
        if not isinstance(value, list):
            context.add_error(
                f"Expected array, got {type(value).__name__}",
                value, schema, "type"
            )
            return False
            
        # Check min/max items
        if schema.get('minItems') is not None and len(value) < schema['minItems']:
            context.add_error(
                f"Array length {len(value)} is less than minimum {schema['minItems']}",
                value, schema, "min_items"
            )
            return False
            
        if schema.get('maxItems') is not None and len(value) > schema['maxItems']:
            context.add_error(
                f"Array length {len(value)} is greater than maximum {schema['maxItems']}",
                value, schema, "max_items"
            )
            return False
            
        # Check unique items
        if schema.get('uniqueItems', False):
            if len(value) != len(set(value)):
                context.add_error(
                    "Array items must be unique",
                    value, schema, "unique_items"
                )
                return False
        
        # 🆕 OpenAPI 3.1.0: Validate prefix items
        prefix_items = schema.get('prefixItems')
        if prefix_items and isinstance(prefix_items, list):
            prefix_count = len(prefix_items)
            for i, item in enumerate(value[:prefix_count]):
                context.push_path(f"[{i}]")
                if not self._validate_value(item, prefix_items[i], context):
                    return False
                context.pop_path()
            
            # Validate remaining items with items schema
            items_schema = schema.get('items')
            if items_schema:
                for i, item in enumerate(value[prefix_count:], prefix_count):
                    context.push_path(f"[{i}]")
                    if not self._validate_value(item, items_schema, context):
                        return False
                    context.pop_path()
        else:
            # Standard items validation
            items_schema = schema.get('items')
            if items_schema:
                for i, item in enumerate(value):
                    context.push_path(f"[{i}]")
                    if not self._validate_value(item, items_schema, context):
                        return False
                    context.pop_path()
        
        # 🆕 OpenAPI 3.1.0: Validate contains
        contains_schema = schema.get('contains')
        if contains_schema:
            min_contains = schema.get('minContains', 1)
            max_contains = schema.get('maxContains')
            
            contains_count = 0
            for i, item in enumerate(value):
                context.push_path(f"[{i}]")
                if self._validate_value(item, contains_schema, context):
                    contains_count += 1
                context.pop_path()
            
            if contains_count < min_contains:
                context.add_error(
                    f"Array must contain at least {min_contains} items matching contains schema, found {contains_count}",
                    value, schema, "min_contains"
                )
                return False
            
            if max_contains is not None and contains_count > max_contains:
                context.add_error(
                    f"Array must contain at most {max_contains} items matching contains schema, found {contains_count}",
                    value, schema, "max_contains"
                )
                return False
                
        return True
    
    def _validate_value(self, value: Any, schema: Dict[str, Any], context: 'ValidationContext') -> bool:
        """Helper method to validate a value against a schema."""
        validator = ValidatorRegistry.get(schema.get('type', 'any'))
        if validator:
            return validator().validate(value, schema, context)
        return True


class ConstValidator(BaseValidator):
    """Validator for constant values."""
    
    def validate(self, value: Any, schema: Dict[str, Any], context: 'ValidationContext') -> bool:
        const_value = schema.get('const')
        if const_value is not None and value != const_value:
            context.add_error(
                f"Value must be exactly {const_value}, got {value}",
                value, schema, "const"
            )
            return False
        return True


class ContentValidator(BaseValidator):
    """Validator for content-encoded string values."""
    
    def validate(self, value: Any, schema: Dict[str, Any], context: 'ValidationContext') -> bool:
        if not isinstance(value, str):
            context.add_error(
                f"Expected string for content validation, got {type(value).__name__}",
                value, schema, "type"
            )
            return False
        
        # Check content encoding
        content_encoding = schema.get('contentEncoding')
        if content_encoding:
            # Basic encoding validation
            if content_encoding not in ['7bit', '8bit', 'binary', 'quoted-printable', 'base16', 'base32', 'base64']:
                context.add_error(
                    f"Unsupported content encoding: {content_encoding}",
                    value, schema, "content_encoding"
                )
                return False
        
        # Check content media type
        content_media_type = schema.get('contentMediaType')
        if content_media_type:
            # Basic media type validation
            if not self._is_valid_media_type(content_media_type):
                context.add_error(
                    f"Invalid content media type: {content_media_type}",
                    value, schema, "content_media_type"
                )
                return False
        
        # Check content schema
        content_schema = schema.get('contentSchema')
        if content_schema:
            # Decode content if needed and validate against schema
            try:
                decoded_content = self._decode_content(value, content_encoding)
                if not self._validate_value(decoded_content, content_schema, context):
                    return False
            except Exception as e:
                context.add_error(
                    f"Content decoding failed: {e}",
                    value, schema, "content_decoding"
                )
                return False
        
        return True
    
    def _is_valid_media_type(self, media_type: str) -> bool:
        """Check if media type is valid."""
        import re
        pattern = r'^[a-zA-Z0-9!#$%&\'*+\-.^_`|~]+/[a-zA-Z0-9!#$%&\'*+\-.^_`|~]+(\+[a-zA-Z0-9!#$%&\'*+\-.^_`|~]+)?$'
        return bool(re.match(pattern, media_type))
    
    def _decode_content(self, content: str, encoding: Optional[str]) -> Any:
        """Decode content based on encoding."""
        if not encoding:
            return content
        
        if encoding == 'base64':
            import base64
            return base64.b64decode(content)
        elif encoding == 'base16':
            import base64
            return base64.b16decode(content)
        elif encoding == 'base32':
            import base64
            return base64.b32decode(content)
        elif encoding == 'quoted-printable':
            import quopri
            return quopri.decodestring(content)
        else:
            # For other encodings, return as-is
            return content
    
    def _validate_value(self, value: Any, schema: Dict[str, Any], context: 'ValidationContext') -> bool:
        """Helper method to validate a value against a schema."""
        validator = ValidatorRegistry.get(schema.get('type', 'any'))
        if validator:
            return validator().validate(value, schema, context)
        return True


class ValidatorRegistry:
    """Registry for schema validators."""
    
    _validators: Dict[str, Type[BaseValidator]] = {}
    
    @classmethod
    def register(cls, type_name: str, validator_class: Type[BaseValidator]):
        """Register a validator for a type."""
        if not issubclass(validator_class, BaseValidator):
            raise ValidatorRegistrationError(f"Validator must be a subclass of BaseValidator")
        cls._validators[type_name] = validator_class
    
    @classmethod
    def get(cls, type_name: str) -> Optional[Type[BaseValidator]]:
        """Get a validator for a type."""
        return cls._validators.get(type_name)
    
    @classmethod
    def unregister(cls, type_name: str):
        """Unregister a validator."""
        cls._validators.pop(type_name, None)
    
    @classmethod
    def clear(cls):
        """Clear all validators."""
        cls._validators.clear()


class ValidationContext:
    """Context for validation operations."""
    
    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.path_stack: List[str] = []
    
    def add_error(self, message: str, value: Any, schema: Dict[str, Any], error_type: str):
        """Add a validation error."""
        self.errors.append({
            'message': message,
            'value': value,
            'schema': schema,
            'type': error_type,
            'path': '.'.join(self.path_stack) if self.path_stack else '/'
        })
    
    def push_path(self, segment: str):
        """Push a path segment."""
        self.path_stack.append(segment)
    
    def pop_path(self):
        """Pop a path segment."""
        if self.path_stack:
            self.path_stack.pop()


class SchemaValidationService:
    """Service for schema validation operations."""
    
    def __init__(self, config):
        self.config = config
        self._initialize_validators()
    
    def _initialize_validators(self):
        """Initialize built-in validators."""
        ValidatorRegistry.register('string', StringValidator)
        ValidatorRegistry.register('integer', NumberValidator)
        ValidatorRegistry.register('number', NumberValidator)
        ValidatorRegistry.register('object', ObjectValidator)
        ValidatorRegistry.register('array', ArrayValidator)
        ValidatorRegistry.register('const', ConstValidator)
        ValidatorRegistry.register('content', ContentValidator)
    
    def validate_data(self, xschema_instance, data: Any, **kwargs: Any) -> bool:
        """Validate data against schema."""
        schema_data = xschema_instance._engine.get_schema_data(xschema_instance)
        context = ValidationContext()
        
        # 🆕 OpenAPI 3.1.0: Check for allErrors configuration
        all_errors = schema_data.get('allErrors', False) or kwargs.get('all_errors', False)
        
        try:
            is_valid = self._validate_value(data, schema_data, context)
            
            # Handle error limits based on allErrors configuration
            max_errors = self.config.validation.max_validation_errors
            if not all_errors and max_errors > 0:
                if len(context.errors) > max_errors:
                    context.errors = context.errors[:max_errors]
                    context.errors.append({
                        'message': f"Validation stopped after {max_errors} errors (allErrors: false)",
                        'value': None,
                        'schema': schema_data,
                        'type': 'max_errors',
                        'path': '/'
                    })
            elif all_errors and len(context.errors) > 0:
                # With allErrors: true, we continue validation but may still hit limits
                if max_errors > 0 and len(context.errors) > max_errors:
                    context.errors = context.errors[:max_errors]
                    context.errors.append({
                        'message': f"Validation stopped after {max_errors} errors (allErrors: true)",
                        'value': None,
                        'schema': schema_data,
                        'type': 'max_errors',
                        'path': '/'
                    })
            
            if context.errors:
                raise SchemaValidationError(
                    f"Schema validation failed with {len(context.errors)} errors",
                    context.errors
                )
            
            return is_valid
            
        except Exception as e:
            if isinstance(e, SchemaValidationError):
                raise
            raise SchemaValidationError(f"Validation error: {e}", [])
    
    def _validate_value(self, value: Any, schema: Dict[str, Any], context: ValidationContext) -> bool:
        """Validate a value against a schema."""
        # 🆕 OpenAPI 3.1.0: Check for const validation first
        if 'const' in schema:
            const_validator = ConstValidator()
            if not const_validator.validate(value, schema, context):
                return False
        
        # Check for nullability
        if value is None:
            return schema.get('nullable', False)
        
        # 🆕 OpenAPI 3.1.0: Check for content validation
        if 'contentEncoding' in schema or 'contentMediaType' in schema or 'contentSchema' in schema:
            content_validator = ContentValidator()
            if not content_validator.validate(value, schema, context):
                return False
        
        # Get schema type
        schema_type = schema.get('type')
        if not schema_type:
            return True  # No type specified, assume valid
        
        # Get validator for type
        validator = ValidatorRegistry.get(schema_type)
        if validator:
            return validator().validate(value, schema, context)
        
        # Check if type is in our mapping
        expected_type = SCHEMA_TYPE_MAPPING.get(schema_type)
        if expected_type:
            if isinstance(expected_type, tuple):
                if not any(isinstance(value, t) for t in expected_type):
                    context.add_error(
                        f"Expected one of {expected_type}, got {type(value).__name__}",
                        value, schema, "type"
                    )
                    return False
            elif not isinstance(value, expected_type):
                context.add_error(
                    f"Expected {expected_type.__name__}, got {type(value).__name__}",
                    value, schema, "type"
                )
                return False
        
        return True 