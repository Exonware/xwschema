#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/formats/base.py

Abstract Schema Serialization Base

Defines common schema concepts, type mappings, and property conversion
for all schema format serializers. Ensures roundtrip compatibility between
different schema formats while maintaining semantic meaning.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from typing import Any, Optional, Union
from abc import abstractmethod
from pathlib import Path
from exonware.xwsystem.io.serialization.base import ASerialization
from exonware.xwsystem.io.serialization.contracts import EncodeOptions, DecodeOptions
from exonware.xwsystem.io.defs import CodecCapability
from exonware.xwsystem.io.serialization.errors import SerializationError
from exonware.xwsystem import get_logger

logger = get_logger(__name__)


# ==============================================================================
# SCHEMA PRIMITIVE TYPES
# ==============================================================================

class SchemaPrimitiveType:
    """Common primitive types across all schema formats."""
    
    # Core primitives
    NULL = "null"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    NUMBER = "number"
    STRING = "string"
    BYTES = "bytes"
    
    # Extended primitives
    FLOAT = "float"
    DOUBLE = "double"
    LONG = "long"
    INT32 = "int32"
    INT64 = "int64"
    
    @classmethod
    def all_primitives(cls) -> set[str]:
        """Get all primitive type names."""
        return {
            cls.NULL, cls.BOOLEAN, cls.INTEGER, cls.NUMBER, cls.STRING, cls.BYTES,
            cls.FLOAT, cls.DOUBLE, cls.LONG, cls.INT32, cls.INT64
        }


# ==============================================================================
# SCHEMA COMPLEX TYPES
# ==============================================================================

class SchemaComplexType:
    """Common complex types across all schema formats."""
    
    # Object/Record types
    OBJECT = "object"
    RECORD = "record"
    
    # Collection types
    ARRAY = "array"
    MAP = "map"
    
    # Union types
    UNION = "union"
    ANY_OF = "anyOf"
    ONE_OF = "oneOf"
    ALL_OF = "allOf"
    
    # Enumeration
    ENUM = "enum"
    
    # Fixed/Constant
    FIXED = "fixed"
    CONST = "const"
    
    @classmethod
    def all_complex(cls) -> set[str]:
        """Get all complex type names."""
        return {
            cls.OBJECT, cls.RECORD, cls.ARRAY, cls.MAP,
            cls.UNION, cls.ANY_OF, cls.ONE_OF, cls.ALL_OF,
            cls.ENUM, cls.FIXED, cls.CONST
        }


# ==============================================================================
# TYPE MAPPING BETWEEN SCHEMA FORMATS
# ==============================================================================

class SchemaTypeMapper:
    """
    Maps types between different schema formats.
    
    Provides bidirectional conversion between schema format types while
    maintaining semantic meaning.
    """
    
    # Mapping: format_name -> {source_type -> target_type}
    TYPE_MAPPINGS: dict[str, dict[str, str]] = {
        # JSON Schema to others
        'json_schema_to_avro': {
            'null': 'null',
            'boolean': 'boolean',
            'integer': 'int',
            'number': 'double',
            'string': 'string',
            'array': 'array',
            'object': 'record',
        },
        # Avro to JSON Schema
        'avro_to_json_schema': {
            'null': 'null',
            'boolean': 'boolean',
            'int': 'integer',
            'long': 'integer',
            'float': 'number',
            'double': 'number',
            'bytes': 'string',
            'string': 'string',
            'array': 'array',
            'record': 'object',
            'enum': 'enum',
            'map': 'object',
            'union': 'oneOf',
            'fixed': 'string',
        },
        # JSON Schema to OpenAPI
        'json_schema_to_openapi': {
            'null': 'null',
            'boolean': 'boolean',
            'integer': 'integer',
            'number': 'number',
            'string': 'string',
            'array': 'array',
            'object': 'object',
        },
        # XSD to JSON Schema
        'xsd_to_json_schema': {
            'xs:string': 'string',
            'xs:integer': 'integer',
            'xs:decimal': 'number',
            'xs:boolean': 'boolean',
            'xs:date': 'string',
            'xs:dateTime': 'string',
            'xs:time': 'string',
            'xs:base64Binary': 'string',
        },
    }
    
    @classmethod
    def map_type(cls, source_type: str, source_format: str, target_format: str) -> str:
        """
        Map a type from source format to target format.
        
        Args:
            source_type: Type name in source format
            source_format: Source schema format name
            target_format: Target schema format name
            
        Returns:
            Mapped type name in target format
        """
        mapping_key = f"{source_format}_to_{target_format}"
        mapping = cls.TYPE_MAPPINGS.get(mapping_key, {})
        
        if source_type in mapping:
            return mapping[source_type]
        
        # Fallback: return as-is if no mapping found
        logger.debug(f"No mapping found for {source_type} from {source_format} to {target_format}")
        return source_type
    
    @classmethod
    def reverse_map_type(cls, target_type: str, source_format: str, target_format: str) -> str:
        """Reverse map a type (target -> source)."""
        mapping_key = f"{source_format}_to_{target_format}"
        mapping = cls.TYPE_MAPPINGS.get(mapping_key, {})
        
        # Reverse lookup
        for source, target in mapping.items():
            if target == target_type:
                return source
        
        # Fallback
        return target_type


# ==============================================================================
# PROPERTY MAPPING BETWEEN SCHEMA FORMATS
# ==============================================================================

class SchemaPropertyMapper:
    """
    Maps properties between different schema formats.
    
    Converts schema properties (constraints, metadata, etc.) between formats
    while maintaining semantic meaning.
    """
    
    # Property mappings: format_name -> {source_prop -> target_prop}
    PROPERTY_MAPPINGS: dict[str, dict[str, str]] = {
        # JSON Schema to Avro
        'json_schema_to_avro': {
            'type': 'type',
            'properties': 'fields',
            'required': 'required',  # Avro doesn't have required, but we can use it
            'enum': 'symbols',
            'items': 'items',
            'minLength': 'minLength',  # Not in Avro, but preserved
            'maxLength': 'maxLength',
            'minimum': 'minimum',
            'maximum': 'maximum',
            'default': 'default',
            'description': 'doc',
            'title': 'name',
        },
        # Avro to JSON Schema
        'avro_to_json_schema': {
            'type': 'type',
            'fields': 'properties',
            'symbols': 'enum',
            'items': 'items',
            'doc': 'description',
            'name': 'title',
            'default': 'default',
        },
        # JSON Schema to OpenAPI
        'json_schema_to_openapi': {
            'type': 'type',
            'properties': 'properties',
            'required': 'required',
            'enum': 'enum',
            'items': 'items',
            'minLength': 'minLength',
            'maxLength': 'maxLength',
            'minimum': 'minimum',
            'maximum': 'maximum',
            'default': 'default',
            'description': 'description',
            'title': 'title',
        },
    }
    
    @classmethod
    def map_property(cls, source_prop: str, source_format: str, target_format: str) -> str:
        """
        Map a property name from source format to target format.
        
        Args:
            source_prop: Property name in source format
            source_format: Source schema format name
            target_format: Target schema format name
            
        Returns:
            Mapped property name in target format
        """
        mapping_key = f"{source_format}_to_{target_format}"
        mapping = cls.PROPERTY_MAPPINGS.get(mapping_key, {})
        
        if source_prop in mapping:
            return mapping[source_prop]
        
        # Fallback: return as-is if no mapping found
        return source_prop
    
    @classmethod
    def map_schema(cls, schema: dict[str, Any], source_format: str, target_format: str) -> dict[str, Any]:
        """
        Convert entire schema from source format to target format.
        
        Args:
            schema: Schema dictionary in source format
            source_format: Source schema format name
            target_format: Target schema format name
            
        Returns:
            Schema dictionary in target format
        """
        if source_format == target_format:
            return schema.copy()
        
        mapped_schema = {}
        
        for key, value in schema.items():
            mapped_key = cls.map_property(key, source_format, target_format)
            
            # Recursively map nested schemas
            if isinstance(value, dict):
                mapped_value = cls.map_schema(value, source_format, target_format)
            elif isinstance(value, list):
                mapped_value = [
                    cls.map_schema(item, source_format, target_format) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                mapped_value = value
            
            # Map type if present
            if mapped_key == 'type' and isinstance(mapped_value, str):
                mapped_value = SchemaTypeMapper.map_type(mapped_value, source_format, target_format)
            
            mapped_schema[mapped_key] = mapped_value
        
        return mapped_schema


# ==============================================================================
# ABSTRACT SCHEMA SERIALIZATION BASE
# ==============================================================================

class ASchemaSerialization(ASerialization):
    """
    Abstract base class for all schema format serializers.
    
    Provides:
    - Common schema type definitions (primitives, complex types)
    - Type mapping between schema formats
    - Property mapping between schema formats
    - Roundtrip conversion support
    
    All schema serializers must extend this class.
    """
    
    # ========================================================================
    # ABSTRACT METHODS (Must implement in subclasses)
    # ========================================================================
    
    @property
    @abstractmethod
    def schema_format_name(self) -> str:
        """
        Get the schema format name (e.g., 'json_schema', 'avro', 'openapi').
        
        Used for type and property mapping.
        """
        pass
    
    @abstractmethod
    def normalize_schema(self, schema: Any) -> dict[str, Any]:
        """
        Normalize schema to a common internal representation.
        
        Args:
            schema: Schema in format-specific representation
            
        Returns:
            Normalized schema dictionary
        """
        pass
    
    @abstractmethod
    def denormalize_schema(self, normalized: dict[str, Any]) -> Any:
        """
        Convert normalized schema back to format-specific representation.
        
        Args:
            normalized: Normalized schema dictionary
            
        Returns:
            Schema in format-specific representation
        """
        pass
    
    # ========================================================================
    # FORMAT-SPECIFIC KEYWORD DEFINITIONS (Must implement in subclasses)
    # ========================================================================
    
    @property
    @abstractmethod
    def reference_keywords(self) -> list[str]:
        """
        Get format-specific reference keywords (e.g., ['$ref'] for JSON Schema).
        
        Returns:
            List of keywords that indicate references in this format
        """
        pass
    
    @property
    @abstractmethod
    def definitions_keywords(self) -> list[str]:
        """
        Get format-specific definitions keywords (e.g., ['$defs', 'definitions'] for JSON Schema).
        
        Returns:
            List of keywords that contain schema definitions
        """
        pass
    
    @property
    @abstractmethod
    def properties_keyword(self) -> str:
        """
        Get format-specific properties keyword (e.g., 'properties' for JSON Schema, 'fields' for Avro).
        
        Returns:
            Keyword for object properties/fields
        """
        pass
    
    @property
    @abstractmethod
    def merge_keywords(self) -> dict[str, str]:
        """
        Get format-specific merge keywords (e.g., {'allOf': 'allOf', 'anyOf': 'anyOf'} for JSON Schema).
        
        Returns:
            Dictionary mapping merge strategy names to format-specific keywords
        """
        pass
    
    # ========================================================================
    # TYPE AND PROPERTY MAPPING
    # ========================================================================
    
    def map_type_to(self, source_type: str, target_format: str) -> str:
        """Map a type from this format to target format."""
        return SchemaTypeMapper.map_type(
            source_type,
            self.schema_format_name,
            target_format
        )
    
    def map_type_from(self, target_type: str, source_format: str) -> str:
        """Map a type from source format to this format."""
        return SchemaTypeMapper.reverse_map_type(
            target_type,
            source_format,
            self.schema_format_name
        )
    
    def map_property_to(self, source_prop: str, target_format: str) -> str:
        """Map a property from this format to target format."""
        return SchemaPropertyMapper.map_property(
            source_prop,
            self.schema_format_name,
            target_format
        )
    
    def convert_to_format(self, schema: Any, target_format: str) -> Any:
        """
        Convert schema from this format to target format.
        
        Args:
            schema: Schema in this format
            target_format: Target schema format name
            
        Returns:
            Schema in target format
        """
        # Normalize to internal representation
        normalized = self.normalize_schema(schema)
        
        # Map to target format
        mapped = SchemaPropertyMapper.map_schema(
            normalized,
            self.schema_format_name,
            target_format
        )
        
        # Get target serializer and denormalize
        # Note: This requires access to serializer registry
        # For now, return mapped dict - subclasses can override
        return mapped
    
    # ========================================================================
    # ROUNDTRIP SUPPORT
    # ========================================================================
    
    def roundtrip_convert(self, schema: Any, via_format: str) -> Any:
        """
        Convert schema through an intermediate format and back.
        
        Useful for testing roundtrip compatibility.
        
        Args:
            schema: Schema in this format
            via_format: Intermediate format to convert through
            
        Returns:
            Schema converted back to this format
        """
        # Convert to intermediate format
        intermediate = self.convert_to_format(schema, via_format)
        
        # Convert back from intermediate format
        # This requires the intermediate format serializer
        # For now, return intermediate - subclasses can implement full roundtrip
        return intermediate
    
    # ========================================================================
    # SCHEMA VALIDATION HELPERS
    # ========================================================================
    
    def is_primitive_type(self, type_name: str) -> bool:
        """Check if type is a primitive type."""
        return type_name in SchemaPrimitiveType.all_primitives()
    
    def is_complex_type(self, type_name: str) -> bool:
        """Check if type is a complex type."""
        return type_name in SchemaComplexType.all_complex()
    
    def validate_schema_structure(self, schema: Any) -> None:
        """
        Validate basic schema structure.
        
        Subclasses should override for format-specific validation.
        """
        if not isinstance(schema, (dict, str)):
            raise SerializationError(f"Schema must be dict or string, got {type(schema).__name__}")
    
    # ========================================================================
    # REFERENCE RESOLUTION
    # ========================================================================
    
    def detect_references(self, schema: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Detect all references in schema using format-specific keywords.
        
        Args:
            schema: Schema to scan for references
            
        Returns:
            List of detected references with their paths and URIs
        """
        refs = []
        ref_keywords = self.reference_keywords
        
        def _scan_for_refs(obj: Any, path: str = "") -> None:
            """Recursively scan for references using format-specific keywords."""
            if isinstance(obj, dict):
                # Check for format-specific reference keywords
                for ref_keyword in ref_keywords:
                    if ref_keyword in obj:
                        refs.append({
                            'type': ref_keyword,
                            'uri': obj[ref_keyword],
                            'path': path,
                            'value': obj[ref_keyword]
                        })
                
                # Recursively scan nested objects
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    _scan_for_refs(value, new_path)
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    new_path = f"{path}[{idx}]" if path else f"[{idx}]"
                    _scan_for_refs(item, new_path)
        
        _scan_for_refs(schema)
        return refs
    
    def resolve_references(
        self, 
        schema: dict[str, Any], 
        base_path: Optional[Path] = None,
        **opts
    ) -> dict[str, Any]:
        """
        Resolve all references in schema.
        
        Args:
            schema: Schema with references
            base_path: Base path for relative references
            **opts: Resolution options
            
        Returns:
            Schema with resolved references (references may still exist if resolution fails)
        """
        # Default implementation - subclasses should override for format-specific resolution
        # For now, return schema as-is (references preserved)
        # Full resolution requires loading external files, which is complex
        return schema.copy()
    
    def resolve_reference(
        self,
        reference: dict[str, Any],
        base_path: Optional[Path] = None,
        **opts
    ) -> Any:
        """
        Resolve a single reference.
        
        Args:
            reference: Reference dict with 'uri', 'type', 'path'
            base_path: Base path for relative references
            **opts: Resolution options
            
        Returns:
            Resolved schema fragment
        """
        # Default implementation - subclasses should override
        uri = reference.get('uri', '')
        ref_type = reference.get('type', self.reference_keywords[0] if self.reference_keywords else 'ref')
        logger.debug(f"Resolving reference: {uri}")
        # Return reference as-is (placeholder) using format-specific keyword
        return {ref_type: uri}
    
    # ========================================================================
    # SCHEMA COMPOSITION AND MERGING
    # ========================================================================
    
    def merge_schemas(
        self, 
        schemas: list[dict[str, Any]], 
        strategy: str = 'allOf'
    ) -> dict[str, Any]:
        """
        Merge multiple schemas using format-specific keywords.
        
        Args:
            schemas: List of schemas to merge
            strategy: Merge strategy ('allOf', 'anyOf', 'oneOf', 'deep', 'shallow')
            
        Returns:
            Merged schema
        """
        if not schemas:
            return {}
        if len(schemas) == 1:
            return schemas[0].copy()
        
        merge_keywords = self.merge_keywords
        
        if strategy in merge_keywords:
            # Use format-specific merge keyword
            keyword = merge_keywords[strategy]
            merged = {keyword: [s.copy() for s in schemas]}
        elif strategy == 'deep':
            # Deep merge properties
            merged = schemas[0].copy()
            for schema in schemas[1:]:
                merged = self._deep_merge_schema(merged, schema)
        else:  # shallow
            # Shallow merge (last wins)
            merged = schemas[-1].copy()
        
        return merged
    
    def _deep_merge_schema(self, schema1: dict[str, Any], schema2: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two schemas."""
        merged = schema1.copy()
        
        for key, value in schema2.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge_schema(merged[key], value)
            elif key in merged and isinstance(merged[key], list) and isinstance(value, list):
                # Merge lists (combine unique items)
                merged[key] = list(set(merged[key] + value))
            else:
                merged[key] = value
        
        return merged
    
    def flatten_schema(
        self, 
        schema: dict[str, Any], 
        inline_refs: bool = True
    ) -> dict[str, Any]:
        """
        Flatten schema by inlining references using format-specific keywords.
        
        Args:
            schema: Schema to flatten
            inline_refs: Whether to inline references
            
        Returns:
            Flattened schema
        """
        if not inline_refs:
            return schema.copy()
        
        # Get format-specific keywords
        ref_keywords = self.reference_keywords
        def_keywords = self.definitions_keywords
        
        # Extract definitions from all possible keywords
        definitions = {}
        for def_key in def_keywords:
            if def_key in schema:
                def_value = schema[def_key]
                if isinstance(def_value, dict):
                    definitions.update(def_value)
        
        # Recursively inline references
        def _inline_refs(obj: Any) -> Any:
            if isinstance(obj, dict):
                # Check for format-specific reference keywords
                for ref_keyword in ref_keywords:
                    if ref_keyword in obj:
                        ref_path = obj[ref_keyword]
                        # Handle JSON Pointer-style references (#/path/to/def)
                        if isinstance(ref_path, str) and ref_path.startswith('#/'):
                            # Local reference
                            ref_key = ref_path[2:].replace('/', '.')
                            if ref_key in definitions:
                                return _inline_refs(definitions[ref_key])
                        elif isinstance(ref_path, str) and ref_path.startswith('#'):
                            # Anchor reference
                            anchor = ref_path[1:]
                            if anchor in definitions:
                                return _inline_refs(definitions[anchor])
                
                # Recursively process nested objects
                return {k: _inline_refs(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_inline_refs(item) for item in obj]
            else:
                return obj
        
        flattened = _inline_refs(schema)
        # Remove definitions if all references are inlined
        for def_key in def_keywords:
            if def_key in flattened:
                del flattened[def_key]
        
        return flattened
    
    # ========================================================================
    # SCHEMA GENERATION
    # ========================================================================
    
    def generate_from_data(self, data: Any, **opts) -> dict[str, Any]:
        """
        Generate schema from sample data.
        
        Args:
            data: Sample data
            **opts: Generation options (title, description, etc.)
            
        Returns:
            Generated schema
        """
        schema: dict[str, Any] = {}
        
        # Infer type
        if data is None:
            schema['type'] = 'null'
        elif isinstance(data, bool):
            schema['type'] = 'boolean'
        elif isinstance(data, int):
            schema['type'] = 'integer'
        elif isinstance(data, float):
            schema['type'] = 'number'
        elif isinstance(data, str):
            schema['type'] = 'string'
        elif isinstance(data, list):
            schema['type'] = 'array'
            if data:
                schema['items'] = self.generate_from_data(data[0], **opts)
        elif isinstance(data, dict):
            schema['type'] = 'object'
            if data:
                schema['properties'] = {
                    k: self.generate_from_data(v, **opts) 
                    for k, v in data.items()
                }
        
        # Add metadata from options
        if 'title' in opts:
            schema['title'] = opts['title']
        if 'description' in opts:
            schema['description'] = opts['description']
        
        return schema
    
    def infer_schema(self, data: Any, **opts) -> dict[str, Any]:
        """Alias for generate_from_data."""
        return self.generate_from_data(data, **opts)
    
    # ========================================================================
    # SCHEMA VALIDATION (Schema Structure)
    # ========================================================================
    
    def validate_schema(self, schema: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate schema structure against meta-schema.
        
        Args:
            schema: Schema to validate
            
        Returns:
            (is_valid, errors) tuple
        """
        errors: list[str] = []
        
        # Basic structure validation
        if not isinstance(schema, dict):
            errors.append("Schema must be a dictionary")
            return False, errors
        
        # Check for required fields (format-specific, subclasses should override)
        # For now, just check basic structure
        self.validate_schema_structure(schema)
        
        return len(errors) == 0, errors
    
    # ========================================================================
    # SCHEMA COMPARISON
    # ========================================================================
    
    def compare_schemas(
        self, 
        schema1: dict[str, Any], 
        schema2: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Compare two schemas.
        
        Args:
            schema1: First schema
            schema2: Second schema
            
        Returns:
            Comparison result with differences
        """
        differences: dict[str, Any] = {
            'identical': False,
            'added': {},
            'removed': {},
            'modified': {},
            'compatible': True
        }
        
        def _compare_dicts(d1: dict, d2: dict, path: str = "") -> None:
            """Recursively compare dictionaries."""
            all_keys = set(d1.keys()) | set(d2.keys())
            
            for key in all_keys:
                new_path = f"{path}.{key}" if path else key
                
                if key not in d1:
                    differences['added'][new_path] = d2[key]
                elif key not in d2:
                    differences['removed'][new_path] = d1[key]
                elif isinstance(d1[key], dict) and isinstance(d2[key], dict):
                    _compare_dicts(d1[key], d2[key], new_path)
                elif d1[key] != d2[key]:
                    differences['modified'][new_path] = {
                        'old': d1[key],
                        'new': d2[key]
                    }
        
        _compare_dicts(schema1, schema2)
        differences['identical'] = (
            not differences['added'] and 
            not differences['removed'] and 
            not differences['modified']
        )
        
        return differences
    
    def is_compatible(
        self, 
        schema1: dict[str, Any], 
        schema2: dict[str, Any]
    ) -> bool:
        """
        Check if schemas are compatible (schema2 can validate data valid for schema1).
        
        Args:
            schema1: Source schema
            schema2: Target schema
            
        Returns:
            True if compatible
        """
        # Basic compatibility check - subclasses should override
        # For now, check if types match
        type1 = schema1.get('type')
        type2 = schema2.get('type')
        
        if type1 and type2:
            return type1 == type2
        
        return True  # Assume compatible if types not specified
    
    # ========================================================================
    # SCHEMA EXTRACTION
    # ========================================================================
    
    def extract_definitions(self, schema: dict[str, Any]) -> dict[str, Any]:
        """
        Extract definitions from schema using format-specific keywords.
        
        Args:
            schema: Schema with definitions
            
        Returns:
            Extracted definitions
        """
        definitions = {}
        def_keywords = self.definitions_keywords
        
        # Check format-specific definition keys
        for key in def_keywords:
            if key in schema:
                def_value = schema[key]
                if isinstance(def_value, dict):
                    definitions.update(def_value)
        
        return definitions
    
    def extract_properties(self, schema: dict[str, Any]) -> dict[str, Any]:
        """
        Extract all properties recursively using format-specific keywords.
        
        Args:
            schema: Schema to extract from
            
        Returns:
            All properties with their paths
        """
        properties: dict[str, Any] = {}
        props_keyword = self.properties_keyword
        
        def _extract(obj: Any, path: str = "") -> None:
            """Recursively extract properties using format-specific keyword."""
            if isinstance(obj, dict):
                if props_keyword in obj:
                    props_value = obj[props_keyword]
                    if isinstance(props_value, dict):
                        # JSON Schema style: {"properties": {"name": {...}}}
                        for prop_name, prop_schema in props_value.items():
                            new_path = f"{path}.{prop_name}" if path else prop_name
                            properties[new_path] = prop_schema
                            _extract(prop_schema, new_path)
                    elif isinstance(props_value, list):
                        # Avro style: {"fields": [{"name": "...", "type": "..."}]}
                        for field in props_value:
                            if isinstance(field, dict):
                                field_name = field.get('name', '')
                                new_path = f"{path}.{field_name}" if path else field_name
                                properties[new_path] = field
                                _extract(field, new_path)
                
                # Recursively process nested schemas
                for key, value in obj.items():
                    if key not in [props_keyword, 'items']:
                        _extract(value, path)
            elif isinstance(obj, list):
                for item in obj:
                    _extract(item, path)
        
        _extract(schema)
        return properties
    
    def extract_types(self, schema: dict[str, Any]) -> set[str]:
        """
        Extract all types used in schema.
        
        Args:
            schema: Schema to extract from
            
        Returns:
            Set of type names
        """
        types: set[str] = set()
        
        def _extract_types(obj: Any) -> None:
            """Recursively extract types."""
            if isinstance(obj, dict):
                if 'type' in obj:
                    type_val = obj['type']
                    if isinstance(type_val, str):
                        types.add(type_val)
                    elif isinstance(type_val, list):
                        types.update(type_val)
                
                # Recursively process nested objects
                for value in obj.values():
                    _extract_types(value)
            elif isinstance(obj, list):
                for item in obj:
                    _extract_types(item)
        
        _extract_types(schema)
        return types
    
    # ========================================================================
    # SCHEMA METADATA HANDLING
    # ========================================================================
    
    def extract_metadata(self, schema: dict[str, Any]) -> dict[str, Any]:
        """
        Extract schema metadata (title, description, examples, etc.).
        
        Args:
            schema: Schema to extract from
            
        Returns:
            Extracted metadata
        """
        metadata_keys = [
            'title', 'description', 'default', 'examples', 'example',
            '$id', '$schema', '$anchor', 'deprecated', 'readOnly', 'writeOnly'
        ]
        
        metadata = {}
        for key in metadata_keys:
            if key in schema:
                metadata[key] = schema[key]
        
        return metadata
    
    def preserve_metadata(
        self, 
        source_schema: dict[str, Any], 
        target_schema: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Preserve metadata from source schema in target schema.
        
        Args:
            source_schema: Source schema with metadata
            target_schema: Target schema to add metadata to
            
        Returns:
            Target schema with preserved metadata
        """
        metadata = self.extract_metadata(source_schema)
        result = target_schema.copy()
        result.update(metadata)
        return result
    
    def merge_metadata(
        self, 
        schemas: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Merge metadata from multiple schemas.
        
        Args:
            schemas: List of schemas to merge metadata from
            
        Returns:
            Merged metadata
        """
        merged: dict[str, Any] = {}
        
        for schema in schemas:
            metadata = self.extract_metadata(schema)
            # Last schema wins for conflicts
            merged.update(metadata)
        
        return merged

