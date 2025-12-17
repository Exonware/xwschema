#!/usr/bin/env python3
"""
🎭 xSchema Facade Module
Main xSchema class implementing the facade pattern for clean, simple schema operations.
"""

import uuid
from typing import Any, Dict, Iterator, Optional, Set, Union, ContextManager, List
from collections.abc import MutableMapping
from pathlib import Path

from .config import xSchemaConfig, SCHEMA_TYPE_MAPPING
from .engine import _xSchemaEngine
from src.xlib.xdata.reference.reference import xReference, RefLoad, RefCopy, RefResolve
from src.xlib.xdata.core.exceptions import SchemaError, SchemaValidationError
from src.xlib.xwsystem.monitoring.performance_monitor import logger
from src.xlib.xwsystem.structures.circular_detector import CircularReferenceDetector
from src.xlib.xdata.standard_abc import xSchemaBase


class xSchemaUtils:
    """🛠️ Utility functions for xSchema operations."""
    
    @staticmethod
    def resolve_base_path(path: Optional[str]) -> Optional[str]:
        """Resolve base path for file operations."""
        if path is None:
            return None
        import os
        return os.path.abspath(path)
    
    @staticmethod
    def looks_like_file_path(source: str) -> bool:
        """Check if string looks like a file path."""
        import os
        # Simple heuristic: contains path separators or has file extension
        return (os.sep in source or '/' in source or '\\' in source or 
                ('.' in source and len(source.split('.')[-1]) <= 5))

    @staticmethod
    def detect_format_from_extension(file_path: str) -> Optional[str]:
        """🔍 Smart format detection from file extension."""
        import os
        from .schema_handler import xSchemaHandlerFactory
        
        _, ext = os.path.splitext(file_path)
        if ext:
            return xSchemaHandlerFactory.get_format_by_extension(ext.lstrip('.'))
        return None


class xSchema(xReference, MutableMapping[str, Any], xSchemaBase):
    """
    Schema definition and validation component, supporting multi-source
    merging, lazy loading, and advanced validation features.
    
    Version: Legacy
    Features: ['multi_format', 'reference_handling', 'validation', 'merging']
    """
    __version__ = "1.0.0"
    __features__ = ['multi_format', 'reference_handling', 'validation', 'merging']
    @staticmethod
    def from_file(
        file_path: str,
        version: Optional[str] = None,
        config: Optional[xSchemaConfig] = None,
        base_path: Optional[str] = None,
        **kwargs: Any
    ) -> "xSchema":
        """
        Creates an xSchema instance from a file.

        Args:
            file_path: Path to the schema file.
            version: Optional version string for this schema.
            config: Pre-configured xSchemaConfig instance.
            base_path: Base directory for resolving relative file references.
            **kwargs: Additional configuration options.

        Returns:
            A new xSchema instance.
        """
        return xSchema(
            file_path,
            version=version,
            config=config,
            base_path=base_path,
            **kwargs
        )

    def __init__(
        self,
        value: str,  # Reference path/URI
        data: Optional[Union[Dict[str, Any], str, Path]] = None,
        version: Optional[str] = None,
        config: Optional[xSchemaConfig] = None,
        base_path: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize xSchema instance with type-safe, efficient configuration.

        Args:
            value: The reference path/URI for this schema, or a file path.
            data: Optional data to initialize the schema
            version: Optional version string for this schema
            config: Pre-configured xSchemaConfig instance for advanced scenarios
            base_path: Base directory for resolving relative file references
            **kwargs: Additional configuration options (see xSchemaConfig.from_kwargs)

        Performance: O(1) initialization with lazy component loading
        Memory: Minimal overhead with demand-driven resource allocation
        Thread Safety: Optional with zero overhead when disabled

        Example:
            >>> # Single schema loading
            >>> schema = xSchema("schema.json", handle_references="lazy")
            >>> 
            >>> # Multi-source merging  
            >>> schema = xSchema("base.json", "overrides.yaml", base_path="/schemas")
            >>> 
            >>> # Security configuration
            >>> config = xSchemaConfig.from_kwargs(
            ...     enable_thread_safety=True,
            ...     enable_path_security=True, 
            ...     enable_performance_monitoring=True
            ... )
            >>> schema = xSchema("schema.json", config=config)
        """
        # Initialize xReference first
        super().__init__(value, **kwargs)
        
        # Configuration management
        if config is None:
            # Create configuration from kwargs with intelligent defaults
            all_config_kwargs = {
                'handle_references': kwargs.get('handle_references'),
                'user_defined_links': kwargs.get('user_defined_links'),
                'wrap_nested_fields': kwargs.get('wrap_nested_fields', False),
                **kwargs
            }
            config = xSchemaConfig.from_kwargs(**all_config_kwargs)
        
        # 🚀 Initialize the internal engine (Facade Pattern)
        self._engine = _xSchemaEngine(config, base_path)
        
        # 🔗 Set facade reference for UUID-based parent lookup
        self._engine.set_facade_reference(self)
        
        # 🎛️ Schema-specific attributes
        self._version = version
        self._base_path = base_path
        
        # 🔗 Reference resolution state
        self._current_resolving_paths_for_load: Set[str] = set()
        
        # 📊 Backward compatibility options (optimized storage)
        # Convert enum values to strings for handler compatibility
        handle_references_str = (
            config.references.handle_references.value 
            if hasattr(config.references.handle_references, 'value') 
            else config.references.handle_references
        )
        resolve_policy_str = (
            config.references.resolve_schema_references.value 
            if hasattr(config.references.resolve_schema_references, 'value') 
            else config.references.resolve_schema_references
        )
        copy_policy_str = (
            kwargs.get('copy_policy', 'default')
        )
        
        self._handler_options: Dict[str, Any] = {
            'handle_references': handle_references_str,
            'resolve_policy': resolve_policy_str,
            'copy_policy': copy_policy_str,
            'encoding': config.encoding,
            'path_delimiter': config.path.path_delimiter,
            **{k: v for k, v in kwargs.items() if k not in {
                'handle_references', 'user_defined_links', 'wrap_nested_fields', 'resolve_policy', 'copy_policy'
            }}
        }
        
        # 🚀 Set base path with intelligent resolution
        if base_path:
            self._base_path = xSchemaUtils.resolve_base_path(base_path)

        logger.debug(
            f"🏆 xSchema initialized (Engine UUID: {self._engine.id}) - "
            f"Security: {config.security.enable_path_security}, "
            f"Threading: {config.threading.enable_thread_safety}, "
            f"Performance: {config.performance.enable_monitoring}, "
            f"Base Path: {self._base_path}"
        )

        # 📥 Load initial data efficiently
        if data is not None:
            self._engine.set_schema_data(self, data if isinstance(data, dict) else {})
        elif xSchemaUtils.looks_like_file_path(self.value):
            # Auto-load file if value looks like a file path and no data provided
            try:
                # The actual loading is now handled by the engine, which can
                # be triggered here or lazily when a property is accessed.
                # For now, let's assume lazy loading by default.
                pass
            except FileNotFoundError:
                raise FileNotFoundError(f"Schema file not found: {self.value}") from None

    # -------------------------------------------------------------------------
    # Schema Attributes (inspired by OpenAPI/JSON Schema)
    # -------------------------------------------------------------------------

    # Metadata Properties
    @property
    def title(self) -> Optional[str]:
        """A title for the schema."""
        return self._engine.get_property('title')

    @title.setter
    def title(self, value: str) -> None:
        self._engine.set_property('title', value)

    @property
    def description(self) -> Optional[str]:
        """A description of the schema."""
        return self._engine.get_property('description')

    @description.setter
    def description(self, value: str) -> None:
        self._engine.set_property('description', value)

    # Value Constraint Properties
    @property
    def type(self) -> Optional[str]:
        """Defines the type of the value (e.g., 'string', 'object')."""
        return self._engine.get_property('type')

    @type.setter
    def type(self, value: str) -> None:
        self._engine.set_property('type', value)

    @property
    def format(self) -> Optional[str]:
        """Specifies the format of the value (e.g., 'date', 'email')."""
        return self._engine.get_property('format')
    
    @format.setter
    def format(self, value: str) -> None:
        self._engine.set_property('format', value)

    @property
    def enum(self) -> Optional[List[Any]]:
        """Lists allowed values."""
        return self._engine.get_property('enum')

    @enum.setter
    def enum(self, value: List[Any]) -> None:
        self._engine.set_property('enum', value)

    @property
    def default(self) -> Any:
        """Provides a default value."""
        return self._engine.get_property('default')

    @default.setter
    def default(self, value: Any) -> None:
        self._engine.set_property('default', value)
        
    @property
    def nullable(self) -> bool:
        """Indicates if the value can be null."""
        return self._engine.get_property('nullable') or False

    @nullable.setter
    def nullable(self, value: bool) -> None:
        self._engine.set_property('nullable', value)

    @property
    def deprecated(self) -> bool:
        """Indicates if the attribute is deprecated."""
        return self._engine.get_property('deprecated') or False
        
    @deprecated.setter
    def deprecated(self, value: bool) -> None:
        self._engine.set_property('deprecated', value)
    
    @property
    def confidential(self) -> bool:
        """Indicates if the attribute is confidential (for UI passwords and DB encryption)."""
        return self._engine.get_property('confidential') or False
        
    @confidential.setter
    def confidential(self, value: bool) -> None:
        self._engine.set_property('confidential', value)

    # Reference Awareness Properties
    @property
    def is_reference(self) -> bool:
        """Check if this xSchema instance is reading a reference."""
        return self._engine._definition.is_reference

    @property
    def reference_uri(self) -> Optional[str]:
        """Get the URI if this xSchema instance is reading a reference."""
        return self._engine._definition.uri

    def get_all_reference_policies(self) -> Dict[str, Any]:
        """Get all reference policies from the internal xData instance."""
        if hasattr(self._engine._definition, 'get_all_reference_policies'):
            return self._engine._definition.get_all_reference_policies()
        # Fallback: return basic reference info
        return {
            'is_reference': self.is_reference,
            'uri': self.reference_uri,
            'load_policy': self.load.value if hasattr(self, 'load') else None,
            'copy_policy': self.copy.value if hasattr(self, 'copy') else None,
            'resolve_policy': self.resolve.value if hasattr(self, 'resolve') else None
        }

    @property
    def _data(self) -> Dict[str, Any]:
        """Get the internal data dictionary (for backward compatibility with tests)."""
        return self._engine.get_schema_data(self)

    # Numeric Constraint Properties
    @property
    def value_min(self) -> Optional[Union[int, float]]:
        """The minimum numeric value allowed."""
        return self._engine.get_property('minimum')

    @value_min.setter
    def value_min(self, value: Union[int, float]) -> None:
        self._engine.set_property('minimum', value)

    @property
    def value_max(self) -> Optional[Union[int, float]]:
        """The maximum numeric value allowed."""
        return self._engine.get_property('maximum')

    @value_max.setter
    def value_max(self, value: Union[int, float]) -> None:
        self._engine.set_property('maximum', value)
        
    @property
    def exclusiveMinimum(self) -> bool:
        """Indicates if the minimum value is exclusive."""
        return self._engine.get_property('exclusiveMinimum') or False

    @exclusiveMinimum.setter
    def exclusiveMinimum(self, value: bool) -> None:
        self._engine.set_property('exclusiveMinimum', value)

    @property
    def exclusiveMaximum(self) -> bool:
        """Indicates if the maximum value is exclusive."""
        return self._engine.get_property('exclusiveMaximum') or False

    @exclusiveMaximum.setter
    def exclusiveMaximum(self, value: bool) -> None:
        self._engine.set_property('exclusiveMaximum', value)

    @property
    def multipleOf(self) -> Optional[Union[int, float]]:
        """Specifies that a value must be a multiple of this number."""
        return self._engine.get_property('multipleOf')

    @multipleOf.setter
    def multipleOf(self, value: Union[int, float]) -> None:
        self._engine.set_property('multipleOf', value)

    # Backward compatibility aliases for numeric constraints
    @property
    def minimum(self) -> Optional[Union[int, float]]:
        """Backward compatibility alias for value_min."""
        return self.value_min

    @minimum.setter
    def minimum(self, value: Union[int, float]) -> None:
        self.value_min = value

    @property
    def maximum(self) -> Optional[Union[int, float]]:
        """Backward compatibility alias for value_max."""
        return self.value_max

    @maximum.setter
    def maximum(self, value: Union[int, float]) -> None:
        self.value_max = value

    # String Constraint Properties
    @property
    def pattern(self) -> Optional[str]:
        """A regex pattern for validating string values."""
        return self._engine.get_property('pattern')

    @pattern.setter
    def pattern(self, value: str) -> None:
        self._engine.set_property('pattern', value)
        
    @property
    def length_min(self) -> Optional[int]:
        """Minimum length of a string."""
        return self._engine.get_property('minLength')

    @length_min.setter
    def length_min(self, value: int) -> None:
        self._engine.set_property('minLength', value)

    @property
    def length_max(self) -> Optional[int]:
        """Maximum length of a string."""
        return self._engine.get_property('maxLength')

    @length_max.setter
    def length_max(self, value: int) -> None:
        self._engine.set_property('maxLength', value)

    # Backward compatibility aliases for string constraints
    @property
    def minLength(self) -> Optional[int]:
        """Backward compatibility alias for length_min."""
        return self.length_min

    @minLength.setter
    def minLength(self, value: int) -> None:
        self.length_min = value

    @property
    def maxLength(self) -> Optional[int]:
        """Backward compatibility alias for length_max."""
        return self.length_max

    @maxLength.setter
    def maxLength(self, value: int) -> None:
        self.length_max = value

    # Array Constraint Properties
    @property
    def items(self) -> Optional['xSchema']:
        """Schema for items in an array."""
        items_data = self._engine.get_property('items')
        if isinstance(items_data, dict):
            return xSchema(value=f"{self.value}/items", data=items_data)
        return None

    @items.setter
    def items(self, value: 'xSchema') -> None:
        self._engine.set_property('items', value.to_native())

    @property
    def items_min(self) -> Optional[int]:
        """Minimum number of items in an array."""
        return self._engine.get_property('minItems')

    @items_min.setter
    def items_min(self, value: int) -> None:
        self._engine.set_property('minItems', value)

    @property
    def items_max(self) -> Optional[int]:
        """Maximum number of items in an array."""
        return self._engine.get_property('maxItems')

    @items_max.setter
    def items_max(self, value: int) -> None:
        self._engine.set_property('maxItems', value)

    # Backward compatibility aliases for array constraints
    @property
    def minItems(self) -> Optional[int]:
        """Backward compatibility alias for items_min."""
        return self.items_min

    @minItems.setter
    def minItems(self, value: int) -> None:
        self.items_min = value

    @property
    def maxItems(self) -> Optional[int]:
        """Backward compatibility alias for items_max."""
        return self.items_max

    @maxItems.setter
    def maxItems(self, value: int) -> None:
        self.items_max = value

    @property
    def uniqueItems(self) -> bool:
        """Indicates if array items must be unique."""
        return self._engine.get_property('uniqueItems') or False

    @uniqueItems.setter
    def uniqueItems(self, value: bool) -> None:
        self._engine.set_property('uniqueItems', value)

    # Object Constraint Properties
    @property
    def properties(self) -> Optional[Dict[str, 'xSchema']]:
        """A dictionary defining the properties of an object."""
        props_data = self._engine.get_property('properties')
        if isinstance(props_data, dict):
            return {
                key: xSchema(value=f"{self.value}/properties/{key}", data=val)
                for key, val in props_data.items()
            }
        return None

    @properties.setter
    def properties(self, value: Dict[str, 'xSchema']) -> None:
        self._engine.set_property('properties', {key: val.to_native() for key, val in value.items()})
        
    @property
    def required(self) -> Optional[List[str]]:
        """Lists required properties."""
        return self._engine.get_property('required')

    @required.setter
    def required(self, value: List[str]) -> None:
        self._engine.set_property('required', value)
        
    @property
    def readOnly(self) -> bool:
        """Indicates if the property is read-only."""
        return self._engine.get_property('readOnly') or False

    @readOnly.setter
    def readOnly(self, value: bool) -> None:
        self._engine.set_property('readOnly', value)

    @property
    def writeOnly(self) -> bool:
        """Indicates if the property is write-only."""
        return self._engine.get_property('writeOnly') or False
        
    @writeOnly.setter
    def writeOnly(self, value: bool) -> None:
        self._engine.set_property('writeOnly', value)

    @property
    def additionalProperties(self) -> Optional[Union[bool, 'xSchema']]:
        """Defines if properties not in 'properties' are allowed."""
        prop = self._engine.get_property('additionalProperties')
        if prop is None:
            return True # Default is True
        if isinstance(prop, bool):
            return prop
        if isinstance(prop, dict):
            return xSchema(value=f"{self.value}/additionalProperties", data=prop)
        return prop

    @additionalProperties.setter
    def additionalProperties(self, value: Union[bool, 'xSchema']) -> None:
        if isinstance(value, bool):
            self._engine.set_property('additionalProperties', value)
        elif isinstance(value, xSchema):
            self._engine.set_property('additionalProperties', value.to_native())
        else:
            raise TypeError("additionalProperties must be a boolean or an xSchema instance")

    @property
    def properties_min(self) -> Optional[int]:
        """Minimum number of properties in an object."""
        return self._engine.get_property('minProperties')

    @properties_min.setter
    def properties_min(self, value: int) -> None:
        self._engine.set_property('minProperties', value)

    @property
    def properties_max(self) -> Optional[int]:
        """Maximum number of properties in an object."""
        return self._engine.get_property('maxProperties')

    @properties_max.setter
    def properties_max(self, value: int) -> None:
        self._engine.set_property('maxProperties', value)

    # Backward compatibility aliases for object constraints
    @property
    def minProperties(self) -> Optional[int]:
        """Backward compatibility alias for properties_min."""
        return self.properties_min

    @minProperties.setter
    def minProperties(self, value: int) -> None:
        self.properties_min = value

    @property
    def maxProperties(self) -> Optional[int]:
        """Backward compatibility alias for properties_max."""
        return self.properties_max

    @maxProperties.setter
    def maxProperties(self, value: int) -> None:
        self.properties_max = value

    # Composition Properties
    @property
    def allOf(self) -> Optional[List['xSchema']]:
        """Combines multiple schemas (must be valid against all)."""
        allof_data = self._engine.get_property('allOf')
        if isinstance(allof_data, list):
            return [xSchema(value=f"{self.value}/allOf/{i}", data=item) for i, item in enumerate(allof_data)]
        return None

    @allOf.setter
    def allOf(self, value: List['xSchema']) -> None:
        self._engine.set_property('allOf', [item.to_native() for item in value])

    @property
    def anyOf(self) -> Optional[List['xSchema']]:
        """Data must be valid against at least one of these schemas."""
        anyof_data = self._engine.get_property('anyOf')
        if isinstance(anyof_data, list):
            return [xSchema(value=f"{self.value}/anyOf/{i}", data=item) for i, item in enumerate(anyof_data)]
        return None

    @anyOf.setter
    def anyOf(self, value: List['xSchema']) -> None:
        self._engine.set_property('anyOf', [item.to_native() for item in value])

    @property
    def oneOf(self) -> Optional[List['xSchema']]:
        """Data must be valid against exactly one of these schemas."""
        oneof_data = self._engine.get_property('oneOf')
        if isinstance(oneof_data, list):
            return [xSchema(value=f"{self.value}/oneOf/{i}", data=item) for i, item in enumerate(oneof_data)]
        return None

    @oneOf.setter
    def oneOf(self, value: List['xSchema']) -> None:
        self._engine.set_property('oneOf', [item.to_native() for item in value])

    @property
    def not_(self) -> Optional['xSchema']:
        """Data must not be valid against this schema."""
        not_data = self._engine.get_property('not')
        if isinstance(not_data, dict):
            return xSchema(value=f"{self.value}/not", data=not_data)
        return None

    @not_.setter
    def not_(self, value: 'xSchema') -> None:
        self._engine.set_property('not', value.to_native())

    # Polymorphism Properties
    @property
    def discriminator(self) -> Optional[Dict[str, Any]]:
        """Identifies which schema to use based on a property value."""
        return self._engine.get_property('discriminator')

    @discriminator.setter
    def discriminator(self, value: Dict[str, Any]) -> None:
        self._engine.set_property('discriminator', value)

    # Conditional Composition Properties
    @property
    def if_(self) -> Optional['xSchema']:
        """If this schema is valid, 'then' must also be valid."""
        if_data = self._engine.get_property('if')
        if isinstance(if_data, dict):
            return xSchema(value=f"{self.value}/if", data=if_data)
        return None

    @if_.setter
    def if_(self, value: 'xSchema') -> None:
        self._engine.set_property('if', value.to_native())

    @property
    def then(self) -> Optional['xSchema']:
        """Applied if 'if' is valid."""
        then_data = self._engine.get_property('then')
        if isinstance(then_data, dict):
            return xSchema(value=f"{self.value}/then", data=then_data)
        return None

    @then.setter
    def then(self, value: 'xSchema') -> None:
        self._engine.set_property('then', value.to_native())

    @property
    def else_(self) -> Optional['xSchema']:
        """Applied if 'if' is not valid."""
        else_data = self._engine.get_property('else')
        if isinstance(else_data, dict):
            return xSchema(value=f"{self.value}/else", data=else_data)
        return None

    @else_.setter
    def else_(self, value: 'xSchema') -> None:
        self._engine.set_property('else', value.to_native())

    # Miscellaneous Properties
    @property
    def example(self) -> Any:
        """An example value."""
        return self._engine.get_property('example')

    @example.setter
    def example(self, value: Any) -> None:
        self._engine.set_property('example', value)

    @property
    def externalDocs(self) -> Optional[Dict[str, Any]]:
        """External documentation for the schema."""
        return self._engine.get_property('externalDocs')
    
    @externalDocs.setter
    def externalDocs(self, value: Dict[str, Any]) -> None:
        self._engine.set_property('externalDocs', value)

    @property
    def examples(self) -> Optional[Dict[str, Any]]:
        """A map of detailed, named examples."""
        return self._engine.get_property('examples')

    @examples.setter
    def examples(self, value: Dict[str, Any]) -> None:
        self._engine.set_property('examples', value)

    @property
    def xml(self) -> Optional[Dict[str, Any]]:
        """XML-specific data representation hints."""
        return self._engine.get_property('xml')

    @xml.setter
    def xml(self, value: Dict[str, Any]) -> None:
        self._engine.set_property('xml', value)

    # ============================================================================
    # 🆕 OPENAPI 3.1.0 ADDITIONAL PROPERTIES
    # ============================================================================

    # Schema Identification Properties
    @property
    def schema_id(self) -> Optional[str]:
        """Schema identifier ($id)."""
        return self._engine.get_property('$id')

    @schema_id.setter
    def schema_id(self, value: str) -> None:
        self._engine.set_property('$id', value)

    @property
    def schema_dialect(self) -> Optional[str]:
        """Schema dialect ($schema)."""
        return self._engine.get_property('$schema')

    @schema_dialect.setter
    def schema_dialect(self, value: str) -> None:
        self._engine.set_property('$schema', value)

    @property
    def anchor(self) -> Optional[str]:
        """Schema anchor ($anchor)."""
        return self._engine.get_property('$anchor')

    @anchor.setter
    def anchor(self, value: str) -> None:
        self._engine.set_property('$anchor', value)

    @property
    def vocabulary(self) -> Optional[Dict[str, bool]]:
        """Schema vocabulary ($vocabulary)."""
        return self._engine.get_property('$vocabulary')

    @vocabulary.setter
    def vocabulary(self, value: Dict[str, bool]) -> None:
        self._engine.set_property('$vocabulary', value)

    @property
    def comment(self) -> Optional[str]:
        """Schema comment ($comment)."""
        return self._engine.get_property('$comment')

    @comment.setter
    def comment(self, value: str) -> None:
        self._engine.set_property('$comment', value)

    @property
    def definitions(self) -> Optional[Dict[str, 'xSchema']]:
        """Schema definitions ($defs)."""
        defs_data = self._engine.get_property('$defs')
        if isinstance(defs_data, dict):
            return {
                key: xSchema(value=f"{self.value}/$defs/{key}", data=val)
                for key, val in defs_data.items()
            }
        return None

    @definitions.setter
    def definitions(self, value: Dict[str, 'xSchema']) -> None:
        self._engine.set_property('$defs', {key: val.to_native() for key, val in value.items()})

    # Reference Properties
    @property
    def uri(self) -> Optional[str]:
        """Reference to another schema ($ref)."""
        return self._engine.get_property('$ref')

    @uri.setter
    def uri(self, value: str) -> None:
        self._engine.set_property('$ref', value)

    @property
    def dynamic_ref(self) -> Optional[str]:
        """Dynamic reference ($dynamicRef)."""
        return self._engine.get_property('$dynamicRef')

    @dynamic_ref.setter
    def dynamic_ref(self, value: str) -> None:
        self._engine.set_property('$dynamicRef', value)

    @property
    def dynamic_anchor(self) -> Optional[str]:
        """Dynamic anchor ($dynamicAnchor)."""
        return self._engine.get_property('$dynamicAnchor')

    @dynamic_anchor.setter
    def dynamic_anchor(self, value: str) -> None:
        self._engine.set_property('$dynamicAnchor', value)

    # Advanced Array Properties
    @property
    def prefix_items(self) -> Optional[List['xSchema']]:
        """Prefix items schema for arrays."""
        prefix_data = self._engine.get_property('prefixItems')
        if isinstance(prefix_data, list):
            return [xSchema(value=f"{self.value}/prefixItems/{i}", data=item) for i, item in enumerate(prefix_data)]
        return None

    @prefix_items.setter
    def prefix_items(self, value: List['xSchema']) -> None:
        self._engine.set_property('prefixItems', [item.to_native() for item in value])

    @property
    def contains(self) -> Optional['xSchema']:
        """Contains schema for arrays."""
        contains_data = self._engine.get_property('contains')
        if isinstance(contains_data, dict):
            return xSchema(value=f"{self.value}/contains", data=contains_data)
        return None

    @contains.setter
    def contains(self, value: 'xSchema') -> None:
        self._engine.set_property('contains', value.to_native())

    @property
    def min_contains(self) -> Optional[int]:
        """Minimum contains count for arrays."""
        return self._engine.get_property('minContains')

    @min_contains.setter
    def min_contains(self, value: int) -> None:
        self._engine.set_property('minContains', value)

    @property
    def max_contains(self) -> Optional[int]:
        """Maximum contains count for arrays."""
        return self._engine.get_property('maxContains')

    @max_contains.setter
    def max_contains(self, value: int) -> None:
        self._engine.set_property('maxContains', value)

    # Advanced Object Properties
    @property
    def property_names(self) -> Optional['xSchema']:
        """Property names schema for objects."""
        names_data = self._engine.get_property('propertyNames')
        if isinstance(names_data, dict):
            return xSchema(value=f"{self.value}/propertyNames", data=names_data)
        return None

    @property_names.setter
    def property_names(self, value: 'xSchema') -> None:
        self._engine.set_property('propertyNames', value.to_native())

    @property
    def pattern_properties(self) -> Optional[Dict[str, 'xSchema']]:
        """Pattern properties for objects."""
        pattern_data = self._engine.get_property('patternProperties')
        if isinstance(pattern_data, dict):
            return {
                key: xSchema(value=f"{self.value}/patternProperties/{key}", data=val)
                for key, val in pattern_data.items()
            }
        return None

    @pattern_properties.setter
    def pattern_properties(self, value: Dict[str, 'xSchema']) -> None:
        self._engine.set_property('patternProperties', {key: val.to_native() for key, val in value.items()})

    @property
    def dependent_required(self) -> Optional[Dict[str, List[str]]]:
        """Dependent required properties."""
        return self._engine.get_property('dependentRequired')

    @dependent_required.setter
    def dependent_required(self, value: Dict[str, List[str]]) -> None:
        self._engine.set_property('dependentRequired', value)

    @property
    def dependent_schemas(self) -> Optional[Dict[str, 'xSchema']]:
        """Dependent schemas for objects."""
        deps_data = self._engine.get_property('dependentSchemas')
        if isinstance(deps_data, dict):
            return {
                key: xSchema(value=f"{self.value}/dependentSchemas/{key}", data=val)
                for key, val in deps_data.items()
            }
        return None

    @dependent_schemas.setter
    def dependent_schemas(self, value: Dict[str, 'xSchema']) -> None:
        self._engine.set_property('dependentSchemas', {key: val.to_native() for key, val in value.items()})

    # Advanced Validation Properties
    @property
    def const(self) -> Any:
        """Constant value validation."""
        return self._engine.get_property('const')

    @const.setter
    def const(self, value: Any) -> None:
        self._engine.set_property('const', value)

    @property
    def dependencies(self) -> Optional[Dict[str, Any]]:
        """Property dependencies (legacy)."""
        return self._engine.get_property('dependencies')

    @dependencies.setter
    def dependencies(self, value: Dict[str, Any]) -> None:
        self._engine.set_property('dependencies', value)

    @property
    def all_errors(self) -> bool:
        """Report all validation errors."""
        return self._engine.get_property('allErrors') or False

    @all_errors.setter
    def all_errors(self, value: bool) -> None:
        self._engine.set_property('allErrors', value)

    @property
    def unevaluated_properties(self) -> Optional[Union[bool, 'xSchema']]:
        """Unevaluated properties schema."""
        prop = self._engine.get_property('unevaluatedProperties')
        if prop is None:
            return True
        if isinstance(prop, bool):
            return prop
        if isinstance(prop, dict):
            return xSchema(value=f"{self.value}/unevaluatedProperties", data=prop)
        return prop

    @unevaluated_properties.setter
    def unevaluated_properties(self, value: Union[bool, 'xSchema']) -> None:
        if isinstance(value, bool):
            self._engine.set_property('unevaluatedProperties', value)
        elif isinstance(value, xSchema):
            self._engine.set_property('unevaluatedProperties', value.to_native())
        else:
            raise TypeError("unevaluatedProperties must be a boolean or an xSchema instance")

    @property
    def unevaluated_items(self) -> Optional[Union[bool, 'xSchema']]:
        """Unevaluated items schema."""
        prop = self._engine.get_property('unevaluatedItems')
        if prop is None:
            return True
        if isinstance(prop, bool):
            return prop
        if isinstance(prop, dict):
            return xSchema(value=f"{self.value}/unevaluatedItems", data=prop)
        return prop

    @unevaluated_items.setter
    def unevaluated_items(self, value: Union[bool, 'xSchema']) -> None:
        if isinstance(value, bool):
            self._engine.set_property('unevaluatedItems', value)
        elif isinstance(value, xSchema):
            self._engine.set_property('unevaluatedItems', value.to_native())
        else:
            raise TypeError("unevaluatedItems must be a boolean or an xSchema instance")

    # Content Validation Properties
    @property
    def content_encoding(self) -> Optional[str]:
        """Content encoding for string values."""
        return self._engine.get_property('contentEncoding')

    @content_encoding.setter
    def content_encoding(self, value: str) -> None:
        self._engine.set_property('contentEncoding', value)

    @property
    def content_media_type(self) -> Optional[str]:
        """Content media type for string values."""
        return self._engine.get_property('contentMediaType')

    @content_media_type.setter
    def content_media_type(self, value: str) -> None:
        self._engine.set_property('contentMediaType', value)

    @property
    def content_schema(self) -> Optional['xSchema']:
        """Content schema for string values."""
        content_data = self._engine.get_property('contentSchema')
        if isinstance(content_data, dict):
            return xSchema(value=f"{self.value}/contentSchema", data=content_data)
        return None

    @content_schema.setter
    def content_schema(self, value: 'xSchema') -> None:
        self._engine.set_property('contentSchema', value.to_native())

    # ============================================================================
    # END OPENAPI 3.1.0 ADDITIONAL PROPERTIES
    # ============================================================================
        
    # ============================================================================
    # 📋 METADATA PROPERTIES
    # ============================================================================
    
    @property
    def uuid(self) -> uuid.UUID:
        """Get the unique identifier for this schema instance."""
        return self._engine.id

    @property
    def id(self) -> Optional[str]:
        """Get the schema identifier (alias for schema_id)."""
        return self.schema_id

    @property
    def notes(self) -> Optional[str]:
        """Get additional notes for the schema."""
        return self._engine.get_property('notes')

    @notes.setter
    def notes(self, value: str) -> None:
        self._engine.set_property('notes', value)

    @property
    def date_created(self) -> Optional[str]:
        """Get the creation date of the schema."""
        return self._engine.get_property('date_created')

    @date_created.setter
    def date_created(self, value: str) -> None:
        self._engine.set_property('date_created', value)

    @property
    def date_updated(self) -> Optional[str]:
        """Get the last update date of the schema."""
        return self._engine.get_property('date_updated')

    @date_updated.setter
    def date_updated(self, value: str) -> None:
        self._engine.set_property('date_updated', value)

    @property
    def date_deleted(self) -> Optional[str]:
        """Get the deletion date of the schema (for soft deletes)."""
        return self._engine.get_property('date_deleted')

    @date_deleted.setter
    def date_deleted(self, value: str) -> None:
        self._engine.set_property('date_deleted', value)

    # ============================================================================
    # END METADATA PROPERTIES
    # ============================================================================

    @property
    def _config(self) -> xSchemaConfig:
        """Get the configuration object."""
        return self._engine.config

    @property 
    def version(self) -> Optional[str]:
        """Get the schema version."""
        return self._version
        
    @version.setter
    def version(self, value: str) -> None:
        """Set the schema version."""
        self._version = value

    # MutableMapping interface implementation
    def __len__(self) -> int:
        """Get the number of top-level schema keys."""
        return len(self._engine)

    def __iter__(self) -> Iterator[str]:
        """Iterate over top-level schema keys."""
        return iter(self._engine)

    def __getitem__(self, key: str) -> Any:
        """Get a schema value by key."""
        return self._engine.get_schema_data(self).get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a schema value by key."""
        data = self._engine.get_schema_data(self)
        data[key] = value
        self._engine.set_schema_data(self, data)

    def __delitem__(self, key: str) -> None:
        """Delete a schema key."""
        data = self._engine.get_schema_data(self)
        if key in data:
            del data[key]
            self._engine.set_schema_data(self, data)
        else:
            raise KeyError(key)

    def clear(self) -> None:
        """Clear all schema data."""
        self._engine.clear()

    def keys(self):
        """Get schema keys view."""
        return self._engine.keys()

    def values(self):
        """Get schema values view."""
        return self._engine.values()

    def items(self):
        """Get schema items view."""
        return self._engine.items()

    def __contains__(self, key: Any) -> bool:
        """Check if schema key exists."""
        return key in self._engine

    # Schema-specific methods
    def validate_data(self, data: Any) -> bool:
        """
        Validate data against this schema.
        
        Args:
            data: The data to validate
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        return self._engine.validate_data(self, data)

    def copy_schema(self, reference: Optional[xReference] = None) -> 'xSchema':
        """
        Creates a copy of this schema instance.
        If a reference is provided, it will be used to determine how to handle the copy.
        
        Args:
            reference: Optional xReference object that defines how this copy should be handled
        """
        # Create new instance with same basic properties
        new_instance = self.__class__(
            value=self.value,
            data=None,  # Will be set based on copy strategy
            version=self._version,
            config=self._config,
            base_path=self._base_path,
            load=self.load,
            copy=self.copy,
            resolve=self.resolve
        )
        
        # Copy schema data based on reference policy
        if reference is None:
            # Simple deep copy if no reference provided
            import copy
            new_instance._engine.set_schema_data(new_instance, copy.deepcopy(self._engine.get_schema_data(self)))
        else:
            # Handle copy based on reference policy
            if reference.copy == RefCopy.LINK:
                # Keep as reference to original
                new_instance._engine.set_schema_data(new_instance, self._engine.get_schema_data(self))
            elif reference.copy == RefCopy.LIVE:
                # Deep copy the data
                import copy
                new_instance._engine.set_schema_data(new_instance, copy.deepcopy(self._engine.get_schema_data(self)))
            else:
                # Default behavior for other copy strategies
                import copy
                new_instance._engine.set_schema_data(new_instance, copy.deepcopy(self._engine.get_schema_data(self)))
        
        return new_instance

    def merge(self, other: 'xSchema', strategy: Optional[str] = None) -> 'xSchema':
        """
        Merge this schema with another schema.
        
        Args:
            other: The schema to merge with
            strategy: Optional merge strategy to use
            
        Returns:
            xSchema: A new schema containing the merged data
        """
        if not isinstance(other, xSchema):
            raise TypeError("Can only merge with another xSchema instance")
            
        # Create new instance
        merged = self.copy_schema()
        
        # Merge data using simple deep merge for now
        data1 = self._engine.get_schema_data(self)
        data2 = other._engine.get_schema_data(other)
        merged_data = self._merge_data(data1, data2, strategy)
        merged._engine.set_schema_data(merged, merged_data)
        
        return merged

    def _merge_data(self, data1: Dict[str, Any], data2: Dict[str, Any], strategy: Optional[str] = None) -> Dict[str, Any]:
        """
        Merge two data dictionaries.
        
        Args:
            data1: First data dictionary
            data2: Second data dictionary
            strategy: Optional merge strategy
            
        Returns:
            Dict containing merged data
        """
        # Simple merge strategy for now
        import copy
        result = copy.deepcopy(data1)
        
        def _deep_merge(target: Dict[str, Any], source: Dict[str, Any]):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    _deep_merge(target[key], value)
                else:
                    target[key] = copy.deepcopy(value)
        
        _deep_merge(result, data2)
        return result

    def to_native(self) -> Dict[str, Any]:
        """
        Convert schema to dictionary format.
        
        Returns:
            Dict containing schema data and metadata
        """
        result = super().to_native()
        
        # Add the actual schema data first
        schema_data = self._engine.get_schema_data(self)
        if isinstance(schema_data, dict):
            result.update(schema_data)
            
        # Then override with xSchema-specific metadata (this takes precedence)
        if self.value:
            result['$schema'] = self.value
        if self._version:
            result['$version'] = self._version
            
        return result



    @classmethod
    def from_native(cls, data: Dict[str, Any]) -> 'xSchema':
        """
        Create schema from dictionary.
        
        Args:
            data: Dictionary containing schema data
            
        Returns:
            xSchema instance
        """
        # Make a copy to avoid modifying the original
        import copy
        data_copy = copy.deepcopy(data)
        value = data_copy.pop('$schema', 'test://schema.json')  # Default value to avoid empty string
        version = data_copy.pop('$version', None)
        return cls(value=value, data=data_copy, version=version)

    def __str__(self) -> str:
        """String representation of the schema."""
        schema_data = self._engine.get_schema_data(self)
        return f"<xSchema(value='{self.value}', version='{self._version}', load={self.load.value}, copy={self.copy.value}, resolve={self.resolve.value}, keys={len(schema_data)})>"

    def __repr__(self) -> str:
        """Detailed string representation of the schema."""
        schema_data = self._engine.get_schema_data(self)
        return f"<xSchema(value='{self.value}', version='{self._version}', load={self.load.value}, copy={self.copy.value}, resolve={self.resolve.value}, keys={len(schema_data)})>"

    # ========================================================================
    # MISSING ABC METHODS
    # ========================================================================

    def validate(self, data: Any) -> bool:
        """Alias for validate_data for ABC compatibility."""
        return self.validate_data(data)

    def to_file(self, file_path: str, format_hint: Optional[str] = None, **kwargs: Any) -> None:
        """Save schema to file."""
        # This is a simplified implementation
        import json
        with open(file_path, 'w') as f:
            json.dump(self.to_native(), f, indent=2) 