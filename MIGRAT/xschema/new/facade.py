"""
xData Schema Facade

High-level interface for schema operations including validation, generation,
and management. Provides simplified access to schema functionality.
"""

from typing import Any, Optional, Dict, List, Union
from pathlib import Path
import json

from src.xlib.xsystem import get_logger
from .core.unified_utils import UnifiedUtils
from .model import SchemaProcessor, ASchemaNode
from .core.errors import XSchemaError, XSchemaValidationError, XSchemaGenerationError

__all__ = ['XSchema']

logger = get_logger(__name__)


class xSchema:
    """
    XSchema facade providing comprehensive schema operations.
    
    Features:
    - Schema validation and generation
    - Multi-format schema support
    - Reference resolution
    - Version management
    - Performance optimization
    
    Uses unified static utilities for better code reuse without inheritance overhead.
    """
    
    def __init__(self, schema: Any = None, **kwargs):
        """Initialize XSchema with optional schema definition."""
        # Use unified configuration and processor management
        config = UnifiedUtils.get_config()
        self._processor = UnifiedUtils.get_or_create_processor(
            "schema_processor",
            lambda: SchemaProcessor()
        )
        
        # Schema-specific initialization
        self.schema = schema
        self.schema_metadata = kwargs.get('schema_metadata', {})
        self.version = kwargs.get('version', '1.0.0')
        self.format = kwargs.get('format', 'json-schema')
        self.strict_mode = kwargs.get('strict_mode', True)
        
        if not config.production_mode and config.enable_logging:
            logger.info(f"🔷 XSchema initialized (format: {self.format})")
    
    # Core Schema Operations
    def validate_schema(self, data: Any, **kwargs) -> bool:
        """
        Validate data against this schema.
        
        Args:
            data: Data to validate
            **kwargs: Validation options
            
        Returns:
            True if validation passes
            
        Raises:
            XSchemaValidationError: If validation fails
        """
        try:
            logger.debug("🔍 Validating data against schema")
            
            if not self.schema:
                raise XSchemaError("No schema defined for validation")
            
            result = self._processor.process_schema(
                "validate",
                schema=self.schema,
                data=data,
                strict=kwargs.get('strict', self.strict_mode),
                **kwargs
            )
            
            logger.info("✅ Data validation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Schema validation failed: {e}")
            raise XSchemaValidationError("Schema validation failed") from e
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get comprehensive schema information."""
        return {
            'format': self.format,
            'version': self.version,
            'strict_mode': self.strict_mode,
            'schema_size': len(str(self.schema)) if self.schema else 0,
            'has_references': self._has_references(),
            'metadata': self.schema_metadata
        }
    
    # Schema Generation
    @classmethod
    def from_data(
        cls,
        data: Any,
        format: str = 'json-schema',
        **kwargs
    ) -> 'XSchema':
        """
        Generate schema from data.
        
        Args:
            data: Source data
            format: Schema format
            **kwargs: Generation options
            
        Returns:
            New XSchema instance with generated schema
        """
        try:
            logger.debug(f"🏗️ Generating {format} schema from data")
            
            processor = SchemaProcessor()
            schema = processor.process_schema(
                "generate",
                data=data,
                schema_format=format,
                **kwargs
            )
            
            instance = cls(schema, format=format, **kwargs)
            logger.info(f"✅ Schema generated successfully: {format}")
            return instance
            
        except Exception as e:
            logger.error(f"❌ Schema generation failed: {e}")
            raise XSchemaGenerationError("Schema generation from data failed") from e
    
    @classmethod
    def from_file(
        cls,
        file_path: Union[str, Path],
        format: Optional[str] = None,
        fast_loading: bool = True,
        **kwargs
    ) -> 'XSchema':
        """
        Load schema from file using unified fast loading.
        
        Args:
            file_path: Path to schema file
            format: Schema format (auto-detected if not provided)
            fast_loading: Use fast loading without validation overhead
            **kwargs: Load options
            
        Returns:
            New XSchema instance with loaded schema
        """
        try:
            # FAST PATH: Use unified fast file loading utility
            if fast_loading:
                def create_minimal_schema(schema_data):
                    """Create minimal schema instance."""
                    instance = cls.__new__(cls)
                    instance.schema = schema_data
                    instance.format = format or 'json-schema'
                    instance.version = '1.0.0'
                    instance.strict_mode = True
                    instance.schema_metadata = {}
                    instance._processor = None  # Skip processor for speed
                    return instance
                
                # Use unified fast file loading utility
                return UnifiedUtils.fast_file_loading(
                    file_path,
                    json.load,  # JSON loader function
                    create_minimal_schema
                )
            
            # Normal loading path
            processor = SchemaProcessor()
            schema = processor.process_schema(
                "parse",
                schema=file_path,
                format=format,
                fast_loading=fast_loading,
                **kwargs
            )
            
            instance = cls(schema, format=format or 'json-schema', **kwargs)
            config = UnifiedUtils.get_config()
            if not config.production_mode and config.enable_debug_logging:
                logger.info(f"✅ Schema loaded successfully from: {file_path}")
            return instance
            
        except Exception as e:
            config = UnifiedUtils.get_config()
            if not config.production_mode and config.enable_debug_logging:
                logger.error(f"❌ Schema loading failed: {e}")
            raise XSchemaError(f"Failed to load schema from {file_path}") from e
    
    # Schema Operations
    def validate_data(self, data: Any, **kwargs) -> bool:
        """Validate data using unified validation pattern."""
        def simple_schema_validator(data_obj, schema_obj):
            """Simple schema validator for fast path."""
            if not schema_obj:
                return True  # No schema, consider valid
            
            # Basic type checking only
            schema_type = schema_obj.get('type') if isinstance(schema_obj, dict) else None
            if schema_type:
                if schema_type == 'object' and not isinstance(data_obj, dict):
                    return False
                if schema_type == 'array' and not isinstance(data_obj, list):
                    return False
                if schema_type == 'string' and not isinstance(data_obj, str):
                    return False
                if schema_type == 'number' and not isinstance(data_obj, (int, float)):
                    return False
            
            return True
        
        def normal_schema_validator(data_obj, schema_obj, **kw):
            """Normal schema validator using processor."""
            if self._processor:
                result = self._processor.process_schema(
                    "validate",
                    schema=schema_obj,
                    data=data_obj,
                    strict=kw.get('strict', True),
                    **kw
                )
                return result
            return True
        
        return UnifiedUtils.fast_validation(
            data,
            self.schema,
            simple_schema_validator,
            self._processor,
            normal_schema_validator,
            **kwargs
        )
    
    def validate_multiple(self, data_list: List[Any], **kwargs) -> List[bool]:
        """
        Validate multiple data items.
        
        Args:
            data_list: List of data to validate
            **kwargs: Validation options
            
        Returns:
            List of validation results
        """
        try:
            logger.debug(f"🔍 Validating {len(data_list)} data items")
            
            results = []
            for i, data in enumerate(data_list):
                try:
                    result = self.validate_schema(data, **kwargs)
                    results.append(result)
                except XSchemaValidationError:
                    logger.warning(f"⚠️ Validation failed for item {i}")
                    results.append(False)
            
            success_count = sum(results)
            logger.info(f"✅ Batch validation completed: {success_count}/{len(data_list)} passed")
            return results
            
        except Exception as e:
            logger.error(f"❌ Batch validation failed: {e}")
            raise XSchemaValidationError("Batch validation failed") from e
    
    def merge_with(self, other_schema: 'XSchema', strategy: str = "deep") -> 'XSchema':
        """
        Merge with another schema using unified merge pattern.
        
        Args:
            other_schema: Schema to merge with
            strategy: Merge strategy
            
        Returns:
            New XSchema with merged schemas
        """
        def merge_operation():
            if self.format != other_schema.format:
                raise XSchemaError(f"Cannot merge schemas with different formats: {self.format} vs {other_schema.format}")
            
            # Use unified merge logic from utilities
            merged_schema = UnifiedUtils.merge_data_structures(self.schema, other_schema.schema, strategy)
            
            return XSchema(
                merged_schema,
                format=self.format,
                version=self._merge_versions(self.version, other_schema.version)
            )
        
        return UnifiedUtils.error_handling_wrapper(
            "schema merge",
            merge_operation
        )
    
    def resolve_references(self, base_uri: Optional[str] = None) -> 'XSchema':
        """
        Resolve all schema references.
        
        Args:
            base_uri: Base URI for reference resolution
            
        Returns:
            New XSchema with resolved references
        """
        try:
            logger.debug("🔗 Resolving schema references")
            
            resolved_schema = self._processor.process_schema(
                "resolve_refs",
                schema=self.schema,
                base_uri=base_uri
            )
            
            result = XSchema(
                resolved_schema,
                format=self.format,
                version=self.version
            )
            
            logger.info("✅ Schema references resolved successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Reference resolution failed: {e}")
            raise XSchemaError("Reference resolution failed") from e
    
    # Schema Analysis
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze schema structure and properties.
        
        Returns:
            Analysis results
        """
        try:
            logger.debug("📊 Analyzing schema")
            
            analysis = {
                'format': self.format,
                'version': self.version,
                'complexity': self._calculate_complexity(),
                'properties_count': self._count_properties(),
                'max_depth': self._calculate_max_depth(),
                'has_references': self._has_references(),
                'required_fields': self._get_required_fields(),
                'optional_fields': self._get_optional_fields(),
                'data_types': self._get_data_types()
            }
            
            logger.info("📊 Schema analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Schema analysis failed: {e}")
            raise XSchemaError("Schema analysis failed") from e
    
    def is_compatible_with(self, other_schema: 'XSchema') -> bool:
        """Check compatibility with another schema."""
        try:
            logger.debug("🔍 Checking schema compatibility")
            
            if self.format != other_schema.format:
                return False
            
            # Simple compatibility check - would be more sophisticated in production
            compatibility = self._check_basic_compatibility(self.schema, other_schema.schema)
            
            logger.info(f"✅ Compatibility check completed: {compatibility}")
            return compatibility
            
        except Exception as e:
            logger.warning(f"⚠️ Compatibility check failed: {e}")
            return False
    
    # File Operations
    def to_file(self, file_path: Union[str, Path], **kwargs) -> None:
        """Save schema to file."""
        try:
            logger.debug(f"💾 Saving schema to: {file_path}")
            
            # Save schema directly as JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.schema, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Schema saved successfully to: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ Schema save failed: {e}")
            raise XSchemaError(f"Failed to save schema to {file_path}") from e
    
    # Helper Methods
    def _has_references(self) -> bool:
        """Check if schema contains references."""
        if not self.schema:
            return False
        return '$ref' in str(self.schema)
    
    def _calculate_complexity(self) -> int:
        """Calculate schema complexity score."""
        if not self.schema:
            return 0
        
        # Simple complexity calculation
        schema_str = str(self.schema)
        return (
            schema_str.count('properties') * 2 +
            schema_str.count('required') +
            schema_str.count('$ref') * 3 +
            schema_str.count('allOf') * 4 +
            schema_str.count('oneOf') * 4 +
            schema_str.count('anyOf') * 3
        )
    
    def _count_properties(self) -> int:
        """Count number of properties in schema."""
        if not isinstance(self.schema, dict):
            return 0
        
        count = 0
        if 'properties' in self.schema:
            count += len(self.schema['properties'])
        
        return count
    
    def _calculate_max_depth(self, schema: Any = None, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        if schema is None:
            schema = self.schema
        
        if not isinstance(schema, dict):
            return current_depth
        
        max_depth = current_depth
        for value in schema.values():
            if isinstance(value, dict):
                depth = self._calculate_max_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _get_required_fields(self) -> List[str]:
        """Get list of required fields."""
        if not isinstance(self.schema, dict):
            return []
        return self.schema.get('required', [])
    
    def _get_optional_fields(self) -> List[str]:
        """Get list of optional fields."""
        if not isinstance(self.schema, dict) or 'properties' not in self.schema:
            return []
        
        all_fields = set(self.schema['properties'].keys())
        required_fields = set(self._get_required_fields())
        return list(all_fields - required_fields)
    
    def _get_data_types(self) -> List[str]:
        """Get list of data types used in schema."""
        types = set()
        self._collect_types(self.schema, types)
        return list(types)
    
    def _collect_types(self, schema: Any, types: set) -> None:
        """Recursively collect types from schema."""
        if isinstance(schema, dict):
            if 'type' in schema:
                types.add(schema['type'])
            for value in schema.values():
                self._collect_types(value, types)
        elif isinstance(schema, list):
            for item in schema:
                self._collect_types(item, types)
    

    
    def _merge_versions(self, version1: str, version2: str) -> str:
        """Merge version numbers."""
        # Simple version merging - would use proper semver in production
        return max(version1, version2)
    
    def _check_basic_compatibility(self, schema1: Dict[str, Any], schema2: Dict[str, Any]) -> bool:
        """Check basic compatibility between schemas."""
        # Simple compatibility check
        if not isinstance(schema1, dict) or not isinstance(schema2, dict):
            return schema1 == schema2
        
        # Check if types are compatible
        type1 = schema1.get('type')
        type2 = schema2.get('type')
        
        if type1 and type2 and type1 != type2:
            return False
        
        return True
    
    # Required abstract method implementations from ADataNode
    def _get_child(self, key: str):
        """Get child element from schema."""
        if not isinstance(self.schema, dict):
            raise KeyError(f"Schema is not a dict, cannot get child '{key}'")
        if key not in self.schema:
            raise KeyError(f"Key '{key}' not found in schema")
        return self.schema[key]
    
    def _to_native(self) -> Any:
        """Convert schema to Python object."""
        return self.schema
    
    def to_xdata_dict(self) -> Dict[str, Any]:
        """Convert to xData dictionary format."""
        return {
            'type': 'schema',
            'value': self.schema,
            'metadata': {
                'format': self.format,
                'version': self.version,
                'schema_metadata': self.schema_metadata
            }
        }

    def __repr__(self) -> str:
        """String representation of XSchema."""
        info = self.get_schema_info()
        return f"XSchema(format={info['format']}, version={info['version']}, size={info['schema_size']})" 