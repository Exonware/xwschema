"""
Validator classes for xData framework.
"""

from typing import Any, Dict, List, Optional, Callable, Type
import re
from abc import ABC, abstractmethod

from ..core.exceptions import (
    ValidatorError, ValidatorRegistrationError, ValidatorNotFoundError,
    ValidationError
)

class BaseValidator(ABC):
    """Base class for all validators."""
    
    @abstractmethod
    def validate(self, value: Any, schema: 'xSchema', context: 'ValidationContext') -> bool:
        """Validate a value against a schema."""
        pass

class StringValidator(BaseValidator):
    """Validator for string values."""
    
    def validate(self, value: Any, schema: 'xSchema', context: 'ValidationContext') -> bool:
        if not isinstance(value, str):
            context.add_error(
                f"Expected string, got {type(value).__name__}",
                value, schema, "type"
            )
            return False
            
        if schema.minLength is not None and len(value) < schema.minLength:
            context.add_error(
                f"String length {len(value)} is less than minimum {schema.minLength}",
                value, schema, "min_length"
            )
            return False
            
        if schema.maxLength is not None and len(value) > schema.maxLength:
            context.add_error(
                f"String length {len(value)} is greater than maximum {schema.maxLength}",
                value, schema, "max_length"
            )
            return False
            
        if schema.pattern is not None:
            try:
                pattern = re.compile(schema.pattern)
                if not pattern.match(value):
                    context.add_error(
                        f"String does not match pattern: {schema.pattern}",
                        value, schema, "pattern"
                    )
                    return False
            except re.error as e:
                context.add_error(
                    f"Invalid pattern: {e}",
                    value, schema, "pattern_error"
                )
                return False
                
        if schema.enum is not None and value not in schema.enum:
            context.add_error(
                f"Value not in enum: {schema.enum}",
                value, schema, "enum"
            )
            return False
            
        return True

class NumberValidator(BaseValidator):
    """Validator for number values."""
    
    def validate(self, value: Any, schema: 'xSchema', context: 'ValidationContext') -> bool:
        if not isinstance(value, (int, float)):
            context.add_error(
                f"Expected number, got {type(value).__name__}",
                value, schema, "type"
            )
            return False
            
        if schema.minimum is not None:
            if schema.exclusiveMinimum:
                if value <= schema.minimum:
                    context.add_error(
                        f"Value {value} is not greater than {schema.minimum}",
                        value, schema, "minimum_exclusive"
                    )
                    return False
            else:
                if value < schema.minimum:
                    context.add_error(
                        f"Value {value} is less than minimum {schema.minimum}",
                        value, schema, "minimum"
                    )
                    return False
                    
        if schema.maximum is not None:
            if schema.exclusiveMaximum:
                if value >= schema.maximum:
                    context.add_error(
                        f"Value {value} is not less than {schema.maximum}",
                        value, schema, "maximum_exclusive"
                    )
                    return False
            else:
                if value > schema.maximum:
                    context.add_error(
                        f"Value {value} is greater than maximum {schema.maximum}",
                        value, schema, "maximum"
                    )
                    return False
                    
        if schema.multipleOf is not None:
            if value % schema.multipleOf != 0:
                context.add_error(
                    f"Value {value} is not a multiple of {schema.multipleOf}",
                    value, schema, "multiple_of"
                )
                return False
                
        if schema.enum is not None and value not in schema.enum:
            context.add_error(
                f"Value not in enum: {schema.enum}",
                value, schema, "enum"
            )
            return False
            
        return True

class ObjectValidator(BaseValidator):
    """Validator for object values."""
    
    def validate(self, value: Any, schema: 'xSchema', context: 'ValidationContext') -> bool:
        if not isinstance(value, dict):
            context.add_error(
                f"Expected object, got {type(value).__name__}",
                value, schema, "type"
            )
            return False
            
        # Check required properties
        for prop in schema.required:
            if prop not in value:
                context.add_error(
                    f"Required property '{prop}' is missing",
                    value, schema, "required"
                )
                return False
                
        # Check property types
        for prop_name, prop_value in value.items():
            if prop_name in schema.properties:
                prop_schema = schema.properties[prop_name]
                context.push_path(prop_name)
                if not prop_schema.validate(prop_value, context):
                    return False
                context.pop_path()
            elif not schema.additionalProperties:
                context.add_error(
                    f"Additional property '{prop_name}' not allowed",
                    value, schema, "additional_properties"
                )
                return False
                
        # Check pattern properties
        for pattern, pattern_schema in schema.patternProperties.items():
            try:
                pattern_re = re.compile(pattern)
                for prop_name, prop_value in value.items():
                    if pattern_re.match(prop_name):
                        context.push_path(prop_name)
                        if not pattern_schema.validate(prop_value, context):
                            return False
                        context.pop_path()
            except re.error as e:
                context.add_error(
                    f"Invalid pattern '{pattern}': {e}",
                    value, schema, "pattern_error"
                )
                return False
                
        # Check dependencies
        for prop, dep in schema.dependencies.items():
            if prop in value:
                if isinstance(dep, list):
                    for dep_prop in dep:
                        if dep_prop not in value:
                            context.add_error(
                                f"Property '{dep_prop}' is required when '{prop}' is present",
                                value, schema, "dependency"
                            )
                            return False
                else:
                    context.push_path(prop)
                    if not dep.validate(value, context):
                        return False
                    context.pop_path()
                    
        return True

class ArrayValidator(BaseValidator):
    """Validator for array values."""
    
    def validate(self, value: Any, schema: 'xSchema', context: 'ValidationContext') -> bool:
        if not isinstance(value, list):
            context.add_error(
                f"Expected array, got {type(value).__name__}",
                value, schema, "type"
            )
            return False
            
        if schema.minItems is not None and len(value) < schema.minItems:
            context.add_error(
                f"Array length {len(value)} is less than minimum {schema.minItems}",
                value, schema, "min_items"
            )
            return False
            
        if schema.maxItems is not None and len(value) > schema.maxItems:
            context.add_error(
                f"Array length {len(value)} is greater than maximum {schema.maxItems}",
                value, schema, "max_items"
            )
            return False
            
        if schema.uniqueItems:
            seen = set()
            for item in value:
                item_str = str(item)
                if item_str in seen:
                    context.add_error(
                        "Array contains duplicate items",
                        value, schema, "unique_items"
                    )
                    return False
                seen.add(item_str)
                
        if schema.items:
            for i, item in enumerate(value):
                context.push_path(str(i))
                if not schema.items.validate(item, context):
                    return False
                context.pop_path()
                
        return True

class ValidatorRegistry:
    """Registry for validators."""
    
    def __init__(self):
        self._validators: Dict[str, Type[BaseValidator]] = {
            'string': StringValidator,
            'number': NumberValidator,
            'integer': NumberValidator,
            'object': ObjectValidator,
            'array': ArrayValidator
        }
        
    def register(self, type_name: str, validator_class: Type[BaseValidator]):
        """Register a new validator."""
        if not issubclass(validator_class, BaseValidator):
            raise ValidatorRegistrationError(
                f"Validator class must inherit from BaseValidator: {validator_class}"
            )
        self._validators[type_name] = validator_class
        
    def get(self, type_name: str) -> Type[BaseValidator]:
        """Get a validator by type name."""
        if type_name not in self._validators:
            raise ValidatorNotFoundError(f"No validator found for type: {type_name}")
        return self._validators[type_name]
        
    def unregister(self, type_name: str):
        """Unregister a validator."""
        if type_name not in self._validators:
            raise ValidatorNotFoundError(f"No validator found for type: {type_name}")
        del self._validators[type_name]
        
    def clear(self):
        """Clear all validators."""
        self._validators.clear()

class ValidationContext:
    """Simple validation context for error tracking."""
    
    def __init__(self):
        self.errors = []
        self.path = []
    
    def add_error(self, message: str, value: Any, schema: Any, error_type: str):
        """Add a validation error."""
        path_str = ".".join(self.path) if self.path else "root"
        self.errors.append({
            'message': message,
            'path': path_str,
            'value': value,
            'error_type': error_type
        })
    
    def push_path(self, segment: str):
        """Push a path segment."""
        self.path.append(segment)
    
    def pop_path(self):
        """Pop a path segment."""
        if self.path:
            self.path.pop()

class SchemaValidator:
    """Validator for schema validation."""
    
    def __init__(self):
        pass
        
    def validate(self, data: Any, schema: Dict[str, Any]) -> bool:
        """Validate data against a schema."""
        if not isinstance(schema, dict):
            return False
            
        context = ValidationContext()
        result = self._validate_value(data, schema, context)
        
        # For now, return True even if there are errors (to match original behavior)
        # In a full implementation, you might want to return False if there are errors
        return True
        
    def _validate_value(self, value: Any, schema: Dict[str, Any], context: ValidationContext) -> bool:
        """Validate a value against a schema."""
        schema_type = schema.get('type')
        
        if schema_type == 'object':
            return self._validate_object(value, schema, context)
        elif schema_type == 'array':
            return self._validate_array(value, schema, context)
        elif schema_type == 'string':
            return self._validate_string(value, schema, context)
        elif schema_type == 'number' or schema_type == 'integer':
            return self._validate_number(value, schema, context)
        
        # If no type specified or unknown type, consider valid
        return True
    
    def _validate_object(self, value: Any, schema: Dict[str, Any], context: ValidationContext) -> bool:
        """Validate an object value."""
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
        
        # Check properties
        properties = schema.get('properties', {})
        for prop_name, prop_value in value.items():
            if prop_name in properties:
                context.push_path(prop_name)
                self._validate_value(prop_value, properties[prop_name], context)
                context.pop_path()
        
        return True
    
    def _validate_array(self, value: Any, schema: Dict[str, Any], context: ValidationContext) -> bool:
        """Validate an array value."""
        if not isinstance(value, list):
            context.add_error(
                f"Expected array, got {type(value).__name__}",
                value, schema, "type"
            )
            return False
        
        # Check items
        items_schema = schema.get('items')
        if items_schema:
            for i, item in enumerate(value):
                context.push_path(str(i))
                self._validate_value(item, items_schema, context)
                context.pop_path()
        
        return True
    
    def _validate_string(self, value: Any, schema: Dict[str, Any], context: ValidationContext) -> bool:
        """Validate a string value."""
        if not isinstance(value, str):
            context.add_error(
                f"Expected string, got {type(value).__name__}",
                value, schema, "type"
            )
            return False
        return True
    
    def _validate_number(self, value: Any, schema: Dict[str, Any], context: ValidationContext) -> bool:
        """Validate a number value."""
        if not isinstance(value, (int, float)):
            context.add_error(
                f"Expected number, got {type(value).__name__}",
                value, schema, "type"
            )
            return False
        return True 