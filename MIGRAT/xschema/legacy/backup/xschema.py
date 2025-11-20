"""
Core schema functionality for xData framework.
"""

from typing import Any, Dict, List, Optional, Set, Union, Type
from abc import ABC, abstractmethod
import json
import logging
from pathlib import Path
from datetime import datetime, date
import re
from enum import Enum
from threading import Lock
import copy

from .exceptions import (
    ConfigurationError, DataInterchangeError, FormatNotSupportedError,
    ParsingError, SerializationError, ReferenceError, CircularReferenceError, ReferenceResolutionError
)
# Conditional import to avoid circular dependency
# from .xdata import xData
from ..reference.reference import xReference, RefLoad, RefCopy, RefResolve
from .validators import SchemaValidator

logger = logging.getLogger(__name__)

# Import handler classes from separate module
try:
    from .xschema_handler import aSchemaHandler, xSchemaHandlerFactory
except ImportError:
    # Handle case where xschema_handler doesn't exist yet
    aSchemaHandler = None
    xSchemaHandlerFactory = None

type_mapping = {
    "string": str,
    "integer": int,
    "float": float,
    "boolean": bool,
    "array": list,
    "object": dict,
    "number": (int, float),  # To handle both integers and floats
    "date": date,
    "datetime": datetime,
    "byte": bytes,
    "binary": bytes,
    "password": str
}



class _xSchemaPart:
    type: str = "" 
    description: str = "" 
    example: Any = None 
    enum: List[Any] = [] 
    default: Any = None 
    deprecated: bool = False 

    def __init__(self, atts=None, data=None, structure=None, focus_path=None):
        super().__init__(atts, data, structure, focus_path)

    def validate(self, value: Any) -> bool:
        """
        Validate a value against the common attributes.

        Args:
            value (Any): The value to validate.

        Returns:
            bool: True if the value is valid, False otherwise.
        """
        # Assign default value if applicable
        if value is None and self.default is not None:
            value = self.default

        # Check for nullability
        if value is None:
            return self.nullable

        # Validate type
        expected_type = type_mapping.get(self.type)
        if expected_type:
            if isinstance(expected_type, tuple):
                if not any(isinstance(value, t) for t in expected_type):
                    return False
            elif not isinstance(value, expected_type):
                return False

        # Validate enum
        if self.enum and value not in self.enum:
            return False

        # Validate regex pattern
        if self.pattern and isinstance(value, str):
            if not re.match(self.pattern, value):
                return False

        # Validate minimum and maximum values
        if isinstance(value, (int, float)):
            if self.minimum is not None and value < self.minimum:
                return False
            if self.maximum is not None and value > self.maximum:
                return False
            if self.multipleOf is not None and value % self.multipleOf != 0:
                return False

        # Validate minLength and maxLength
        if isinstance(value, (str, list)):
            if self.minLength is not None and len(value) < self.minLength:
                return False
            if self.maxLength is not None and len(value) > self.maxLength:
                return False

        return True
    
class xSchemaType(_xSchemaPart):
    items: 'xSchemaType' = None 
    properties: Dict[str, 'xSchemaProperty'] = {} 
    required: List[str] = [] 
    format: str = "" 
    allOf: List['xSchemaType'] = [] 
    minimum: Union[int, float] = None 
    maximum: Union[int, float] = None 
    oneOf: List['xSchemaType'] = [] 
    additionalProperties: Union[bool, 'xSchemaProperty'] = True 
    readOnly: bool = False 
    writeOnly: bool = False 
    pattern: str = "" 
    nullable: bool = False 
    anyOf: List['xSchemaType'] = [] 
    maxLength: int = 0 
    minLength: int = 0 
    uniqueItems: bool = False 
    maxItems: int = 0 
    minItems: int = 0 
    maxProperties: int = 0 
    minProperties: int = 0 
    discriminator: str = "" 
    exclusiveMaximum: bool = False 
    exclusiveMinimum: bool = False 
    multipleOf: Union[int, float] = None 
    title: str = "" 
    externalDocs: Dict[str, Any] = {} 
    xml: Dict[str, Any] = {} 
    not_: 'xSchemaType' = None 


    def __init__(self, atts=None, data=None, structure=None, focus_path=None):
        super().__init__(atts, data, structure, focus_path)

    def validate(self, value: Any) -> bool:
        """
        Validate a value against the xSchema's attributes.

        Args:
            value (Any): The value to validate.

        Returns:
            bool: True if the value is valid, False otherwise.
        """
        # Assign default value if applicable
        if value is None and self.default is not None:
            value = self.default

        # Check for nullability
        if value is None:
            return self.nullable

        # Validate type
        expected_type = type_mapping.get(self.type)
        if expected_type:
            if isinstance(expected_type, tuple):
                if not any(isinstance(value, t) for t in expected_type):
                    return False
            elif not isinstance(value, expected_type):
                return False

        # Validate against regex
        if self.regex and isinstance(value,
                                     str) and not re.match(self.regex, value):
            return False

        # Validate minvalue and maxvalue
        if isinstance(value, (int, float)):
            if self.minvalue is not None:
                if self.exclusiveMinimum and value <= self.minvalue:
                    return False
                elif not self.exclusiveMinimum and value < self.minvalue:
                    return False
            if self.maxvalue != 0:
                if self.exclusiveMaximum and value >= self.maxvalue:
                    return False
                elif not self.exclusiveMaximum and value > self.maxvalue:
                    return False
            if self.multipleOf is not None and value % self.multipleOf != 0:
                return False

        # Validate minlength and maxlength
        if isinstance(value, str):
            value_length = len(value.strip())  # Handle blanks as zero length
            if self.minlength is not None and value_length < self.minlength:
                return False
            if self.maxlength != 0 and value_length > self.maxlength:
                return False
        elif isinstance(value, (list, dict, set)):
            if self.minlength is not None and len(value) < self.minlength:
                return False
            if self.maxlength != 0 and len(value) > self.maxlength:
                return False

        # Validate enum
        if self.enum and value not in self.enum:
            return False

        # Validate item_schema
        if isinstance(value, list) and self.item_schema:
            for item in value:
                if not self.item_schema.validate(item):
                    return False

        return True
    
class xSchemaProperty(_xSchemaPart):
    items: 'xSchemaType' = None 
    schema: 'xSchemaType' = None 
    required: List[str] = [] 
    format: str = "" 
    minimum: Union[int, float] = None 
    maximum: Union[int, float] = None 
    pattern: str = "" 
    nullable: bool = False 
    maxLength: int = 0 
    minLength: int = 0 
    uniqueItems: bool = False 
    maxItems: int = 0 
    minItems: int = 0 
    exclusiveMaximum: bool = False 
    exclusiveMinimum: bool = False 
    multipleOf: Union[int, float] = None 
    location: str = "" 
    style: str = "" 
    content: Dict[str, Any] = {} 
    examples: Dict[str, Any] = {} 
    allowEmptyValue: bool = False 
    allowReserved: bool = False 
    explode: bool = False 

    def __init__(self, atts=None, data=None, structure=None, focus_path=None):
        super().__init__(atts, data, structure, focus_path)

class xSchemaParameter(_xSchemaPart):
    items: 'xSchemaType' = None 
    schema: 'xSchemaType' = None 
    required: List[str] = [] 
    format: str = "" 
    minimum: Union[int, float] = None 
    maximum: Union[int, float] = None 
    pattern: str = "" 
    nullable: bool = False 
    maxLength: int = 0 
    minLength: int = 0 
    uniqueItems: bool = False 
    maxItems: int = 0 
    minItems: int = 0 
    exclusiveMaximum: bool = False 
    exclusiveMinimum: bool = False 
    multipleOf: Union[int, float] = None 
    location: str = "" 
    style: str = "" 
    content: Dict[str, Any] = {} 
    examples: Dict[str, Any] = {} 
    allowEmptyValue: bool = False 
    allowReserved: bool = False 
    explode: bool = False 

    def __init__(self, atts=None, data=None, structure=None, focus_path=None):
        super().__init__(atts, data, structure, focus_path)

class xSchema(xReference):
    """
    Schema class that extends xReference.
    This allows schema to handle references between schemas and manage schema data.
    
    The schema can be used to:
    1. Define data structure and validation rules
    2. Handle references between schemas
    3. Validate data against the schema
    4. Manage schema versions and migrations
    """
    
    def __init__(self, 
                 value: str,  # Reference path/URI
                 data: Optional[Union[Dict[str, Any], str, Path]] = None,
                 version: Optional[str] = None,
                 **kwargs):
        """
        Initialize schema with reference capabilities and data storage.
        
        Args:
            value: The reference path/URI for this schema
            data: Optional data to initialize the schema
            version: Optional version string for this schema
            **kwargs: Additional arguments for xReference initialization
        """
        # Initialize xReference first
        super().__init__(value, **kwargs)
        
        # Schema-specific attributes
        self._version = version
        self._validator = SchemaValidator()
        self._lock = Lock()
        self._data = data or {}
        
        # Parse and extract inline reference policies
        self._inline_ref_policies = self._extract_inline_ref_policies(self._data)
        
    @property
    def version(self) -> Optional[str]:
        """Get the schema version."""
        return self._version
        
    @version.setter
    def version(self, value: str) -> None:
        """Set the schema version."""
        self._version = value
        
    def validate(self, data: Any) -> bool:
        """
        Validate data against this schema.
        
        Args:
            data: The data to validate
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        return self._validator.validate(data, self._data)
        
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
            load=self.load,
            copy=self.copy,
            resolve=self.resolve
        )
        
        # Copy schema-specific attributes
        new_instance._validator = self._validator
        new_instance._lock = Lock()
        
        if reference is None:
            # Simple deep copy if no reference provided
            new_instance._data = copy.deepcopy(self._data)
        else:
            # Handle copy based on reference policy
            if reference.copy == RefCopy.LINK:
                # Keep as reference to original
                new_instance._data = self._data
            elif reference.copy == RefCopy.LIVE:
                # Deep copy the data
                new_instance._data = copy.deepcopy(self._data)
            else:
                # Default behavior for other copy strategies
                new_instance._data = copy.deepcopy(self._data)
        
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
        merged._data = self._merge_data(self._data, other._data, strategy)
        
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
        if isinstance(self._data, dict):
            result.update(self._data)
            
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
        data_copy = copy.deepcopy(data)
        value = data_copy.pop('$schema', 'test://schema.json')  # Default value to avoid empty string
        version = data_copy.pop('$version', None)
        return cls(value=value, data=data_copy, version=version)
        
    def __repr__(self) -> str:
        """Enhanced representation showing it's a schema."""
        return f"<xSchema(value='{self.value}', version='{self._version}', load={self.load.value}, copy={self.copy.value}, resolve={self.resolve.value})>"

    def _extract_inline_ref_policies(self, data: Any) -> Dict[str, Dict[str, str]]:
        """
        Extract inline reference policies from schema data.
        
        Args:
            data: Schema data to scan for inline reference policies
            
        Returns:
            Dict mapping reference URIs to their inline policies
        """
        policies = {}
        
        if isinstance(data, dict):
            self._scan_for_inline_refs(data, policies)
        
        return policies
    
    def _scan_for_inline_refs(self, obj: Dict[str, Any], policies: Dict[str, Dict[str, str]], path: str = ""):
        """
        Recursively scan object for inline reference policies.
        
        Args:
            obj: Dictionary to scan
            policies: Dictionary to store found policies
            path: Current path for debugging
        """
        if not isinstance(obj, dict):
            return
            
        # Check if this object has a $ref with inline policies
        if "$ref" in obj:
            ref_uri = obj["$ref"]
            ref_policies = {}
            
            # Extract inline policy properties
            for policy_key in ["load", "copy", "resolve"]:
                if policy_key in obj:
                    ref_policies[policy_key] = obj[policy_key]
            
            if ref_policies:
                policies[ref_uri] = ref_policies
                
        # Recursively scan all nested objects and arrays
        for key, value in obj.items():
            # Don't skip any keys now - we need to scan everything for nested $refs
            if isinstance(value, dict):
                self._scan_for_inline_refs(value, policies, f"{path}.{key}" if path else key)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._scan_for_inline_refs(item, policies, f"{path}.{key}[{i}]" if path else f"{key}[{i}]")
    
    def get_reference_policy(self, ref_uri: str, policy_type: str) -> Optional[str]:
        """
        Get a specific reference policy for a given reference URI.
        
        Args:
            ref_uri: The reference URI to look up
            policy_type: The type of policy ("load", "copy", "resolve")
            
        Returns:
            The policy value if found, None otherwise
        """
        if ref_uri in self._inline_ref_policies:
            return self._inline_ref_policies[ref_uri].get(policy_type)
        return None
    
    def get_all_reference_policies(self) -> Dict[str, Dict[str, str]]:
        """
        Get all inline reference policies found in this schema.
        
        Returns:
            Dictionary mapping reference URIs to their policies
        """
        return self._inline_ref_policies.copy()
