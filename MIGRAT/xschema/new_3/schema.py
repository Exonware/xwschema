#!/usr/bin/env python3
"""
🔐 xSchema - Schema Definition and Validation (OpenAPI Standard Naming)
Supports both class and decorator usage with confidential property for sensitive data.
Reuses xData from new_3 to eliminate repetition.
Extends aSchema interface for advanced functionality.
"""

import uuid
from typing import Any, Dict, Optional, List, Union, Callable, get_type_hints, get_origin, get_args, Type
from functools import wraps
from datetime import datetime

from src.xlib.xsystem import get_logger
from src.xlib.xdata import xData

logger = get_logger(__name__)


class xSchema:
    """
    xSchema - Schema definition and validation component with OpenAPI standard naming.
    
    Features:
    - Class and decorator usage
    - Confidential property for sensitive data (passwords, encryption)
    - Full JSON Schema compatibility
    - Validation and type checking
    - Reuses xData from new_3 to eliminate repetition
    - Extends aSchema interface for advanced functionality
    - Accepts Python types directly (handlers handle format conversion)
    - OpenAPI/JSON Schema standard parameter naming
    
    Usage as class:
        schema = xSchema(
            type=str,  # Python type directly
            length_min=8,
            pattern=r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$",
            confidential=True
        )
    
    Usage as decorator:
        @xSchema(confidential=True)  # type auto-detected from return hint
        def password_field(self) -> str:
            return self._password
    """
    
    def __init__(self, 
                 type: Optional[Type] = None,  # Python type or JSON schema type string
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 format: Optional[str] = None,
                 enum: Optional[List[Any]] = None,
                 default: Any = None,
                 nullable: bool = False,
                 deprecated: bool = False,
                 confidential: bool = False,
                 
                 # Field control
                 strict: bool = False,              # Strict type checking
                 alias: Optional[str] = None,       # Field alias for serialization
                 exclude: bool = False,             # Exclude from serialization
                 
                 # String constraints (OpenAPI standard naming)
                 pattern: Optional[str] = None,
                 length_min: Optional[int] = None,
                 length_max: Optional[int] = None,
                 strip_whitespace: bool = False,    # Auto-strip whitespace
                 to_upper: bool = False,           # Convert to uppercase
                 to_lower: bool = False,           # Convert to lowercase
                 
                 # Numeric constraints (OpenAPI standard naming)
                 value_min: Optional[Union[int, float]] = None,
                 value_max: Optional[Union[int, float]] = None,
                 value_min_exclusive: Union[bool, float, int] = False,  # Can be bool or value
                 value_max_exclusive: Union[bool, float, int] = False,  # Can be bool or value
                 value_multiple_of: Optional[Union[int, float]] = None,
                 
                 # Array constraints (OpenAPI standard naming)
                 items: Optional['xSchema'] = None,
                 items_min: Optional[int] = None,
                 items_max: Optional[int] = None,
                 items_unique: bool = False,
                 
                 # Object constraints (OpenAPI standard naming)
                 properties: Optional[Dict[str, 'xSchema']] = None,
                 required: Optional[List[str]] = None,
                 properties_additional: Optional[Union[bool, 'xSchema']] = None,
                 properties_min: Optional[int] = None,
                 properties_max: Optional[int] = None,
                 
                 # Logical constraints (OpenAPI standard naming)
                 schema_all_of: Optional[List['xSchema']] = None,
                 schema_any_of: Optional[List['xSchema']] = None,
                 schema_one_of: Optional[List['xSchema']] = None,
                 schema_not: Optional['xSchema'] = None,
                 
                 # Conditional constraints (OpenAPI standard naming)
                 schema_if: Optional['xSchema'] = None,
                 schema_then: Optional['xSchema'] = None,
                 schema_else: Optional['xSchema'] = None,
                 
                 # Content constraints
                 content_encoding: Optional[str] = None,
                 content_media_type: Optional[str] = None,
                 content_schema: Optional['xSchema'] = None,
                 
                 # Metadata
                 example: Any = None,
                 examples: Optional[Dict[str, Any]] = None,
                 
                 # References
                 ref: Optional[str] = None,
                 anchor: Optional[str] = None,
                 
                 # Custom properties
                 **kwargs):
        
        # Backward-compatibility aliases (map legacy JSON Schema names to new ones)
        if 'min_length' in kwargs and kwargs.get('length_min') is None:
            kwargs['length_min'] = kwargs.pop('min_length')
        if 'max_length' in kwargs and kwargs.get('length_max') is None:
            kwargs['length_max'] = kwargs.pop('max_length')
        if 'minimum' in kwargs and kwargs.get('value_min') is None:
            kwargs['value_min'] = kwargs.pop('minimum')
        if 'maximum' in kwargs and kwargs.get('value_max') is None:
            kwargs['value_max'] = kwargs.pop('maximum')
        if 'min_items' in kwargs and kwargs.get('items_min') is None:
            kwargs['items_min'] = kwargs.pop('min_items')
        if 'max_items' in kwargs and kwargs.get('items_max') is None:
            kwargs['items_max'] = kwargs.pop('max_items')
        if 'additional_properties' in kwargs and kwargs.get('properties_additional') is None:
            kwargs['properties_additional'] = kwargs.pop('additional_properties')
        if 'all_of' in kwargs and kwargs.get('schema_all_of') is None:
            kwargs['schema_all_of'] = kwargs.pop('all_of')
        if 'any_of' in kwargs and kwargs.get('schema_any_of') is None:
            kwargs['schema_any_of'] = kwargs.pop('any_of')
        if 'one_of' in kwargs and kwargs.get('schema_one_of') is None:
            kwargs['schema_one_of'] = kwargs.pop('one_of')
        if 'not_' in kwargs and kwargs.get('schema_not') is None:
            kwargs['schema_not'] = kwargs.pop('not_')

        # Store original parameters for easy access (using new names)
        self._type = type  # Python type directly
        self._title = title
        self._description = description
        self._format = format
        self._enum = enum
        self._default = default
        self._nullable = nullable
        self._deprecated = deprecated
        self._confidential = confidential
        
        # Field control parameters
        self._strict = strict
        self._alias = alias
        self._exclude = exclude
        
        # String constraints (OpenAPI naming)
        self._pattern = pattern
        self._length_min = length_min if length_min is not None else kwargs.get('length_min')
        self._length_max = length_max if length_max is not None else kwargs.get('length_max')
        self._strip_whitespace = strip_whitespace
        self._to_upper = to_upper
        self._to_lower = to_lower
        
        # Numeric constraints (OpenAPI naming)
        # Fallback for legacy 'minimum'/'maximum' mapped earlier into kwargs
        if value_min is None:
            value_min = kwargs.get('value_min')
        if value_max is None:
            value_max = kwargs.get('value_max')

        if isinstance(value_min_exclusive, (int, float)) and not isinstance(value_min_exclusive, bool):
            self._value_min = value_min_exclusive
            self._value_min_exclusive = True
        else:
            self._value_min = value_min
            self._value_min_exclusive = value_min_exclusive
            
        if isinstance(value_max_exclusive, (int, float)) and not isinstance(value_max_exclusive, bool):
            self._value_max = value_max_exclusive
            self._value_max_exclusive = True
        else:
            self._value_max = value_max
            self._value_max_exclusive = value_max_exclusive
            
        self._value_multiple_of = value_multiple_of
        
        # Array constraints (OpenAPI naming)
        self._items = items
        self._items_min = items_min if items_min is not None else kwargs.get('items_min')
        self._items_max = items_max if items_max is not None else kwargs.get('items_max')
        self._items_unique = items_unique
        
        # Object constraints (OpenAPI naming)
        self._properties = properties or {}
        self._required = required or []
        self._properties_additional = (
            properties_additional if properties_additional is not None else kwargs.get('properties_additional')
        )
        self._properties_min = properties_min if properties_min is not None else kwargs.get('properties_min')
        self._properties_max = properties_max if properties_max is not None else kwargs.get('properties_max')
        
        # Logical constraints (OpenAPI naming)
        self._schema_all_of = (schema_all_of if schema_all_of is not None else kwargs.get('schema_all_of') or [])
        self._schema_any_of = (schema_any_of if schema_any_of is not None else kwargs.get('schema_any_of') or [])
        self._schema_one_of = (schema_one_of if schema_one_of is not None else kwargs.get('schema_one_of') or [])
        self._schema_not = schema_not if schema_not is not None else kwargs.get('schema_not')
        
        # Conditional constraints (OpenAPI naming)
        self._schema_if = schema_if if schema_if is not None else kwargs.get('schema_if')
        self._schema_then = schema_then if schema_then is not None else kwargs.get('schema_then')
        self._schema_else = schema_else if schema_else is not None else kwargs.get('schema_else')
        
        # Content constraints
        self._content_encoding = content_encoding
        self._content_media_type = content_media_type
        self._content_schema = content_schema
        
        # Metadata
        self._example = example
        self._examples = examples or {}
        self._ref = ref
        self._anchor = anchor
        self._custom_properties = kwargs
        self._created_at = datetime.now().isoformat()
        
        # Performance optimization settings
        self._cache_enabled = False
        self._validation_cache = {}
        self._performance_stats = {
            'validations': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Build schema data (native Python representation)
        schema_data = {}
        
        # Basic properties
        if type:
            schema_data["type"] = type  # Store Python type directly
        if title:
            schema_data["title"] = title
        if description:
            schema_data["description"] = description
        if format:
            schema_data["format"] = format
        if enum:
            schema_data["enum"] = enum
        if default is not None:
            schema_data["default"] = default
        if nullable:
            schema_data["nullable"] = nullable
        if deprecated:
            schema_data["deprecated"] = deprecated
        if confidential:
            schema_data["confidential"] = confidential
        
        # String constraints
        if pattern:
            schema_data["pattern"] = pattern
        if length_min is not None:
            schema_data["lengthMin"] = length_min
        if length_max is not None:
            schema_data["lengthMax"] = length_max
        
        # Numeric constraints
        if value_min is not None:
            schema_data["valueMin"] = value_min
        if value_max is not None:
            schema_data["valueMax"] = value_max
        if self._value_min_exclusive:
            schema_data["valueMinExclusive"] = self._value_min_exclusive
        if self._value_max_exclusive:
            schema_data["valueMaxExclusive"] = self._value_max_exclusive
        if value_multiple_of is not None:
            schema_data["valueMultipleOf"] = value_multiple_of
        
        # Array constraints
        if items:
            schema_data["items"] = items.to_native()
        if items_min is not None:
            schema_data["itemsMin"] = items_min
        if items_max is not None:
            schema_data["itemsMax"] = items_max
        if items_unique:
            schema_data["itemsUnique"] = items_unique
        
        # Object constraints
        if properties:
            schema_data["properties"] = {key: val.to_native() for key, val in properties.items()}
        if required:
            schema_data["required"] = required
        if properties_additional is not None:
            if isinstance(properties_additional, xSchema):
                schema_data["propertiesAdditional"] = properties_additional.to_native()
            else:
                schema_data["propertiesAdditional"] = properties_additional
        if properties_min is not None:
            schema_data["propertiesMin"] = properties_min
        if properties_max is not None:
            schema_data["propertiesMax"] = properties_max
        
        # Logical constraints
        if schema_all_of:
            schema_data["schemaAllOf"] = [schema.to_native() for schema in schema_all_of]
        if schema_any_of:
            schema_data["schemaAnyOf"] = [schema.to_native() for schema in schema_any_of]
        if schema_one_of:
            schema_data["schemaOneOf"] = [schema.to_native() for schema in schema_one_of]
        if schema_not:
            schema_data["schemaNot"] = schema_not.to_native()
        
        # Conditional constraints
        if schema_if:
            schema_data["schemaIf"] = schema_if.to_native()
        if schema_then:
            schema_data["schemaThen"] = schema_then.to_native()
        if schema_else:
            schema_data["schemaElse"] = schema_else.to_native()
        
        # Content constraints
        if content_encoding:
            schema_data["contentEncoding"] = content_encoding
        if content_media_type:
            schema_data["contentMediaType"] = content_media_type
        if content_schema:
            schema_data["contentSchema"] = content_schema.to_native()
        
        # Metadata
        if example is not None:
            schema_data["example"] = example
        if examples:
            schema_data["examples"] = examples
        
        # References
        if ref:
            schema_data["$ref"] = ref
        if anchor:
            schema_data["$anchor"] = anchor
        
        # Custom properties
        schema_data.update(kwargs)
        
        # Use xData internally to eliminate repetition
        self._xdata = xData(schema_data, metadata={
            'schema_type': 'xSchema',
            'created_at': self._created_at,
            'confidential': confidential
        })
        
        logger.debug(f"🔷 xSchema created (type: {type}, confidential: {confidential})")
    
    def __call__(self, func_or_value: Optional[Union[Callable, Any]] = None):
        """
        Support both decorator and validation usage.
        
        Decorator usage:
            @xSchema(confidential=True)  # type auto-detected from return hint
            def password_field(self) -> str:
                return self._password
        
        Validation usage:
            schema = xSchema(type=str)
            is_valid = schema(value)
        """
        if callable(func_or_value):
            return self._decorate(func_or_value)
        else:
            return self.validate(func_or_value)
    
    def _decorate(self, func: Callable) -> Callable:
        """Create decorated function with schema validation."""
        # Auto-detect type from return annotation if not provided
        if not self._type:
            try:
                return_hint = get_type_hints(func).get('return')
                if return_hint:
                    self._type = return_hint
                    logger.debug(f"🔍 Auto-detected type '{self._type}' from return hint for {func.__name__}")
            except Exception as e:
                logger.debug(f"⚠️ Could not auto-detect type for {func.__name__}: {e}")
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the return value
            result = func(*args, **kwargs)
            
            # Validate the result against the schema
            if not self.validate(result):
                raise ValueError(f"Function {func.__name__} returned invalid value: {result}")
            
            return result
        
        # Store schema metadata on the function
        wrapper._schema = self
        wrapper._is_schema_decorated = True
        
        return wrapper
    
    def validate(self, value: Any) -> bool:
        """
        Validate a value against this schema.
        
        Args:
            value: Value to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check cache if enabled
            if self._cache_enabled:
                value_hash = hash(str(value))
                if value_hash in self._validation_cache:
                    self._performance_stats['cache_hits'] += 1
                    return self._validation_cache[value_hash]
                else:
                    self._performance_stats['cache_misses'] += 1
            
            # Perform validation
            result = self._validate_value(value)
            
            # Cache result if enabled
            if self._cache_enabled:
                value_hash = hash(str(value))
                self._validation_cache[value_hash] = result
            
            self._performance_stats['validations'] += 1
            return result
            
        except Exception as e:
            logger.debug(f"🔍 Validation failed: {e}")
            return False
    
    def _validate_value(self, value: Any) -> bool:
        """Internal validation logic using OpenAPI standard parameter names."""
        # Handle null values
        if value is None:
            return self._nullable or self._type == "null"
        # If explicit null schema, only None is valid
        if self._type == "null":
            return False
        
        # Type validation - only if type is explicitly set
        inferred_type = None
        if self._type:
            inferred_type = self._type
        else:
            # Infer type from constraints
            if self._length_min is not None or self._length_max is not None or self._pattern is not None:
                inferred_type = "string"
            elif self._value_min is not None or self._value_max is not None:
                inferred_type = "number"
            elif self._items is not None or self._items_min is not None or self._items_max is not None:
                inferred_type = "array"
            elif self._properties or self._required:
                inferred_type = "object"
        if inferred_type and not self._validate_type(value, inferred_type):
            return False
        
        # Enum validation
        if self._enum and value not in self._enum:
            return False
        
        # String validation with processing
        if self._type == str or self._type == "string":
            if not isinstance(value, str):
                return False
            
            # Apply string processing
            processed_value = value
            if self._strip_whitespace:
                processed_value = processed_value.strip()
            if self._to_upper:
                processed_value = processed_value.upper()
            elif self._to_lower:
                processed_value = processed_value.lower()
            
            # Validate processed value using OpenAPI naming
            if self._length_min is not None and len(processed_value) < self._length_min:
                return False
            
            if self._length_max is not None and len(processed_value) > self._length_max:
                return False
            
            if self._pattern:
                import re
                if not re.match(self._pattern, processed_value):
                    return False
        
        # Number validation using OpenAPI naming
        elif (self._type in [int, float, "number", "integer"]) or inferred_type in ["number", "integer"]:
            if not isinstance(value, (int, float)):
                return False
            
            if (self._type == int or self._type == "integer") and not isinstance(value, int):
                return False
            
            if self._value_min is not None:
                if self._value_min_exclusive:
                    if value <= self._value_min:
                        return False
                else:
                    if value < self._value_min:
                        return False
            
            if self._value_max is not None:
                if self._value_max_exclusive:
                    if value >= self._value_max:
                        return False
                else:
                    if value > self._value_max:
                        return False
            
            if self._value_multiple_of is not None:
                if value % self._value_multiple_of != 0:
                    return False
        
        # Boolean validation
        elif self._type == bool or self._type == "boolean":
            if not isinstance(value, bool):
                return False
        
        # Array validation using OpenAPI naming
        elif (self._type == list or self._type == "array") or inferred_type == "array":
            if not isinstance(value, (list, tuple)):
                return False
            
            if self._items_min is not None and len(value) < self._items_min:
                return False
            
            if self._items_max is not None and len(value) > self._items_max:
                return False
            
            if self._items_unique and len(value) != len(set(value)):
                return False
            
            if self._items:
                for item in value:
                    if not self._items.validate(item):
                        return False
        
        # Object validation using OpenAPI naming
        elif (self._type == dict or self._type == "object") or inferred_type == "object":
            if not isinstance(value, dict):
                return False
            
            if self._properties_min is not None and len(value) < self._properties_min:
                return False
            
            if self._properties_max is not None and len(value) > self._properties_max:
                return False
            
            # Required properties
            for prop in self._required:
                if prop not in value:
                    return False
            
            # Properties validation
            for prop_name, prop_value in value.items():
                if prop_name in self._properties:
                    if not self._properties[prop_name].validate(prop_value):
                        return False
                elif self._properties_additional is False:
                    return False
                elif isinstance(self._properties_additional, xSchema):
                    if not self._properties_additional.validate(prop_value):
                        return False
        
        # Logical validation using OpenAPI naming
        if self._schema_all_of:
            # Validate against each sub-schema
            for schema in self._schema_all_of:
                if not schema.validate(value):
                    return False
            # Additionally, if combined constraints imply a string with min/max length, enforce them
            # This covers cases where parent has no explicit type but sub-schemas define string length
            if isinstance(value, str):
                min_len = None
                max_len = None
                for schema in self._schema_all_of:
                    if hasattr(schema, 'min_length') and schema.min_length is not None:
                        min_len = max(min_len or 0, schema.min_length)
                    if hasattr(schema, 'max_length') and schema.max_length is not None:
                        max_len = min(max_len if max_len is not None else float('inf'), schema.max_length)
                if min_len is not None and len(value) < min_len:
                    return False
                if max_len is not None and len(value) > max_len:
                    return False
        
        if self._schema_any_of:
            for schema in self._schema_any_of:
                if schema.validate(value):
                    break
            else:
                return False
        
        if self._schema_one_of:
            valid_count = 0
            for schema in self._schema_one_of:
                if schema.validate(value):
                    valid_count += 1
                    if valid_count > 1:
                        break
            if valid_count != 1:
                return False
        
        if self._schema_not and self._schema_not.validate(value):
            return False
        
        return True
    
    def _validate_type(self, value: Any, schema_type: Type) -> bool:
        """Validate value type."""
        if schema_type == str or schema_type == "string":
            return isinstance(value, str)
        elif schema_type == int or schema_type == "integer":
            # Treat bool as not integer for strictness
            return isinstance(value, int) and not isinstance(value, bool)
        elif schema_type == float or schema_type == "number":
            return (isinstance(value, (int, float)) and not isinstance(value, bool))
        elif schema_type == bool or schema_type == "boolean":
            return isinstance(value, bool)
        elif schema_type == list or schema_type == "array":
            return isinstance(value, (list, tuple))
        elif schema_type == dict or schema_type == "object":
            return isinstance(value, dict)
        elif schema_type == datetime:
            return isinstance(value, datetime)
        elif schema_type == type(None):
            return value is None
        return True
    
    # ========================================================================
    # PERFORMANCE OPTIMIZATIONS
    # ========================================================================
    
    def enable_caching(self) -> None:
        """Enable validation result caching."""
        self._cache_enabled = True
        logger.debug("🔧 Validation caching enabled")
    
    def disable_caching(self) -> None:
        """Disable validation result caching."""
        self._cache_enabled = False
        logger.debug("🔧 Validation caching disabled")
    
    def clear_cache(self) -> None:
        """Clear validation cache."""
        self._validation_cache.clear()
        logger.debug("🧹 Validation cache cleared")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = self._performance_stats.copy()
        stats['cache_size'] = len(self._validation_cache)
        stats['cache_enabled'] = self._cache_enabled
        return stats
    
    # ========================================================================
    # CONVENIENCE METHODS
    # ========================================================================
    
    def is_required(self) -> bool:
        """Check if schema is required (not nullable and no default)."""
        return not self._nullable and self._default is None
    
    def get_default_value(self) -> Any:
        """Get default value or None if not set."""
        return self._default
    
    # ========================================================================
    # PROPERTIES WITH OPENAPI NAMING
    # ========================================================================
    
    @property
    def id(self) -> str:
        """Get schema ID from xData."""
        return str(self._xdata.id)

    @property
    def created_at(self) -> str:
        """Creation timestamp for compatibility with tests."""
        return self._created_at
    
    @property
    def type(self) -> Optional[Type]:
        """Get schema type."""
        mapping = {str: "string", int: "integer", float: "number", bool: "boolean", dict: "object", list: "array", type(None): "null"}
        if isinstance(self._type, str):
            return self._type
        return mapping.get(self._type, str(self._type))
    
    @property
    def title(self) -> Optional[str]:
        """Get schema title."""
        return self._title
    
    @property
    def description(self) -> Optional[str]:
        """Get schema description."""
        return self._description
    
    @property
    def format(self) -> Optional[str]:
        """Get schema format."""
        return self._format
    
    @property
    def confidential(self) -> bool:
        """Get confidential property."""
        return self._confidential
    
    # String constraints (OpenAPI naming)
    @property
    def length_min(self) -> Optional[int]:
        """Get minimum string length."""
        return self._length_min
    # Backward-compatible alias
    @property
    def min_length(self) -> Optional[int]:
        return self._length_min
    
    @property
    def length_max(self) -> Optional[int]:
        """Get maximum string length."""
        return self._length_max
    @property
    def max_length(self) -> Optional[int]:
        return self._length_max

    @property
    def pattern(self) -> Optional[str]:
        return self._pattern
    
    # Numeric constraints (OpenAPI naming)
    @property
    def value_min(self) -> Optional[Union[int, float]]:
        """Get minimum value."""
        return self._value_min
    @property
    def minimum(self) -> Optional[Union[int, float]]:
        return self._value_min
    
    @property
    def value_max(self) -> Optional[Union[int, float]]:
        """Get maximum value."""
        return self._value_max
    @property
    def maximum(self) -> Optional[Union[int, float]]:
        return self._value_max
    
    @property
    def value_min_exclusive(self) -> bool:
        """Get exclusive minimum flag."""
        return self._value_min_exclusive
    
    @property
    def value_max_exclusive(self) -> bool:
        """Get exclusive maximum flag."""
        return self._value_max_exclusive
    
    @property
    def value_multiple_of(self) -> Optional[Union[int, float]]:
        """Get multiple of constraint."""
        return self._value_multiple_of
    
    # Array constraints (OpenAPI naming)
    @property
    def items_min(self) -> Optional[int]:
        """Get minimum items count."""
        return self._items_min
    @property
    def min_items(self) -> Optional[int]:
        return self._items_min
    
    @property
    def items_max(self) -> Optional[int]:
        """Get maximum items count."""
        return self._items_max
    @property
    def max_items(self) -> Optional[int]:
        return self._items_max

    @property
    def items(self) -> Optional['xSchema']:
        return self._items
    
    # Object constraints (OpenAPI naming)
    @property
    def properties_min(self) -> Optional[int]:
        """Get minimum properties count."""
        return self._properties_min
    
    @property
    def properties_max(self) -> Optional[int]:
        """Get maximum properties count."""
        return self._properties_max
    
    @property
    def properties_additional(self) -> Optional[Union[bool, 'xSchema']]:
        """Get additional properties constraint."""
        return self._properties_additional

    # Legacy accessors for tests
    @property
    def properties(self) -> Dict[str, 'xSchema']:
        return self._properties
    
    @property
    def required(self) -> List[str]:
        return self._required
    
    # Logical constraints (OpenAPI naming)
    @property
    def schema_all_of(self) -> List['xSchema']:
        """Get all-of schemas."""
        return self._schema_all_of
    
    @property
    def schema_any_of(self) -> List['xSchema']:
        """Get any-of schemas."""
        return self._schema_any_of
    
    @property
    def schema_one_of(self) -> List['xSchema']:
        """Get one-of schemas."""
        return self._schema_one_of
    
    @property
    def schema_not(self) -> Optional['xSchema']:
        """Get not schema."""
        return self._schema_not
    
    # Conditional constraints (OpenAPI naming)
    @property
    def schema_if(self) -> Optional['xSchema']:
        """Get if schema."""
        return self._schema_if
    
    @property
    def schema_then(self) -> Optional['xSchema']:
        """Get then schema."""
        return self._schema_then
    
    @property
    def schema_else(self) -> Optional['xSchema']:
        """Get else schema."""
        return self._schema_else
    
    # ========================================================================
    # SERIALIZATION
    # ========================================================================
    
    def to_native(self) -> Dict[str, Any]:
        """Convert schema to dictionary using xData."""
        return self._xdata.to_native()

    # Compatibility helpers expected by tests
    def to_dict(self) -> Dict[str, Any]:
        """Legacy-style serialization for tests (JSON Schema-like)."""
        def _map_type(t: Any) -> Optional[str]:
            mapping = {str: "string", int: "integer", float: "number", bool: "boolean", dict: "object", "array": list, type(None): "null"}
            if isinstance(t, str):
                return t
            return mapping.get(t, None)
        data: Dict[str, Any] = {}
        if self._type is not None:
            mapped = _map_type(self._type)
            data["type"] = mapped if mapped is not None else str(self._type)
        if self._title is not None:
            data["title"] = self._title
        if self._description is not None:
            data["description"] = self._description
        if self._format is not None:
            data["format"] = self._format
        if self._enum is not None:
            data["enum"] = list(self._enum)
        if self._default is not None:
            data["default"] = self._default
        if self._nullable:
            data["nullable"] = True
        if self._deprecated:
            data["deprecated"] = True
        if self._confidential:
            data["confidential"] = True
        # String constraints
        if self._length_min is not None:
            data["min_length"] = self._length_min
        if self._length_max is not None:
            data["max_length"] = self._length_max
        if self._pattern is not None:
            data["pattern"] = self._pattern
        # Number constraints
        if self._value_min is not None:
            data["minimum"] = self._value_min
        if self._value_max is not None:
            data["maximum"] = self._value_max
        # Array constraints
        if self._items is not None:
            data["items"] = self._items.to_dict()
        if self._items_min is not None:
            data["min_items"] = self._items_min
        if self._items_max is not None:
            data["max_items"] = self._items_max
        # Object constraints
        if self._properties:
            data["properties"] = {k: v.to_dict() for k, v in self._properties.items()}
        if self._required:
            data["required"] = list(self._required)
        # Custom properties
        if self._custom_properties:
            data.update(self._custom_properties)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'xSchema':
        """Legacy-style constructor from JSON-like dict for tests."""
        py_type = data.get("type")
        # Build properties recursively if provided
        props = None
        if isinstance(data.get("properties"), dict):
            props = {k: cls.from_dict(v) for k, v in data["properties"].items()}
        items = None
        if isinstance(data.get("items"), dict):
            items = cls.from_dict(data["items"])
        return cls(
            type=py_type,
            title=data.get("title"),
            description=data.get("description"),
            format=data.get("format"),
            enum=data.get("enum"),
            default=data.get("default"),
            nullable=data.get("nullable", False),
            deprecated=data.get("deprecated", False),
            confidential=data.get("confidential", False),
            length_min=data.get("min_length"),
            length_max=data.get("max_length"),
            value_min=data.get("minimum"),
            value_max=data.get("maximum"),
            items=items,
            items_min=data.get("min_items"),
            items_max=data.get("max_items"),
            properties=props,
            required=data.get("required", [])
        )
    
    # ========================================================================
    # STRING REPRESENTATION
    # ========================================================================
    
    def __str__(self) -> str:
        """String representation."""
        return f"xSchema(type={self._type}, confidential={self._confidential})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"xSchema(id={self._xdata.id}, type={self._type}, confidential={self._confidential})"


# ========================================================================
# CONVENIENCE FUNCTIONS WITH OPENAPI NAMING
# ========================================================================

def string_schema(**kwargs) -> xSchema:
    """Create a string schema."""
    return xSchema(type="string", **kwargs)


def number_schema(**kwargs) -> xSchema:
    """Create a number schema."""
    return xSchema(type="number", **kwargs)


def integer_schema(**kwargs) -> xSchema:
    """Create an integer schema."""
    return xSchema(type="integer", **kwargs)


def boolean_schema(**kwargs) -> xSchema:
    """Create a boolean schema."""
    return xSchema(type="boolean", **kwargs)


def object_schema(**kwargs) -> xSchema:
    """Create an object schema."""
    return xSchema(type="object", **kwargs)


def array_schema(**kwargs) -> xSchema:
    """Create an array schema."""
    return xSchema(type="array", **kwargs)


def password_schema(**kwargs) -> xSchema:
    """Create a password schema with confidential flag."""
    return xSchema(
        type="string",
        confidential=True,
        length_min=8,
        pattern=r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$",
        **kwargs
    )


def email_schema(**kwargs) -> xSchema:
    """Create an email schema."""
    return xSchema(
        type="string",
        format="email",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        **kwargs
    )


def url_schema(**kwargs) -> xSchema:
    """Create a URL schema."""
    return xSchema(
        type="string",
        format="uri",
        **kwargs
    )


def date_schema(**kwargs) -> xSchema:
    """Create a date schema."""
    return xSchema(
        type="string",
        format="date",
        **kwargs
    )


def datetime_schema(**kwargs) -> xSchema:
    """Create a datetime schema."""
    return xSchema(
        type="string",
        format="date-time",
        **kwargs
    )
