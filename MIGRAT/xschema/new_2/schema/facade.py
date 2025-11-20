"""Enhanced schema facade for the inheritance API with performance optimizations."""

from typing import Any, Dict, Optional, Union
from pathlib import Path
import json

from src.xlib.xsystem import get_logger
from src.xlib.xdata import xData
from ..core.errors import XSchemaError

logger = get_logger(__name__)

# Global schema cache for performance optimization
_schema_cache = {}

class xSchema:
    """
    Enhanced schema implementation with aggressive performance optimizations.
    
    Features:
    - Schema caching for repeated loads
    - Fast validation paths
    - Optimized schema parsing
    """
    
    def __init__(self, schema_data: Any, base_path: Optional[str] = None):
        """
        Initialize schema with performance optimizations.
        
        Args:
            schema_data: Schema data (dict, xData, or file path)
            base_path: Base path for resolving references
        """
        self._schema_data = schema_data
        self._base_path = base_path
        self._validation_cache = {}  # Cache validation results
        
        # Pre-compile validation rules for faster validation
        self._compiled_rules = self._compile_validation_rules(schema_data)
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path], base_path: Optional[str] = None) -> 'xSchema':
        """
        Load schema from file with caching for performance.
        
        Args:
            file_path: Path to schema file
            base_path: Base path for resolving references
            
        Returns:
            xSchema instance
        """
        file_path = str(file_path)
        
        # Check cache first for massive performance improvement
        cache_key = f"{file_path}:{base_path}"
        if cache_key in _schema_cache:
            logger.debug(f"📋 Schema cache hit for {file_path}")
            return _schema_cache[cache_key]
        
        try:
            # Load schema data
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
            else:
                # Use xData for other formats
                schema_data = xData.from_file(file_path, base_path)
            
            # Create schema instance
            schema = cls(schema_data, base_path)
            
            # Cache the result
            _schema_cache[cache_key] = schema
            logger.debug(f"📋 Schema cached for {file_path}")
            
            return schema
            
        except Exception as e:
            logger.error(f"❌ Failed to load schema from {file_path}: {e}")
            raise XSchemaError(f"Failed to load schema: {e}")
    
    def validate_data(self, data: Any) -> bool:
        """
        Validate data against schema with performance optimizations.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Fast path: check validation cache
        data_hash = hash(str(data)) if hasattr(data, '__hash__') else id(data)
        cache_key = f"{self._schema_hash}:{data_hash}"
        
        if cache_key in self._validation_cache:
            return self._validation_cache[cache_key]
        
        # Fast path: if schema is empty or None, everything is valid
        if not self._schema_data:
            self._validation_cache[cache_key] = True
            return True
        
        # Fast path: if data is None and schema allows it
        if data is None:
            if isinstance(self._schema_data, dict) and self._schema_data.get('type') == 'null':
                self._validation_cache[cache_key] = True
                return True
            else:
                self._validation_cache[cache_key] = False
                return False
        
        try:
            # Use compiled rules for faster validation
            is_valid = self._validate_with_compiled_rules(data)
            
            # Cache the result
            self._validation_cache[cache_key] = is_valid
            
            return is_valid
            
        except Exception as e:
            logger.error(f"❌ Schema validation failed: {e}")
            return False
    
    def _compile_validation_rules(self, schema_data: Any) -> Dict[str, Any]:
        """
        Pre-compile validation rules for faster validation.
        
        Args:
            schema_data: Schema data to compile
            
        Returns:
            Compiled validation rules
        """
        if isinstance(schema_data, dict):
            # Extract common validation patterns
            rules = {
                'type': schema_data.get('type'),
                'required': schema_data.get('required', []),
                'properties': schema_data.get('properties', {}),
                'pattern': schema_data.get('pattern'),
                'min_length': schema_data.get('minLength'),
                'max_length': schema_data.get('maxLength'),
                'minimum': schema_data.get('minimum'),
                'maximum': schema_data.get('maximum'),
            }
            return rules
        return {}
    
    def _validate_with_compiled_rules(self, data: Any) -> bool:
        """
        Fast validation using pre-compiled rules.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid
        """
        return self._validate_recursive(data, self._schema_data)
    
    def _validate_recursive(self, data: Any, schema: Any, ref_cache=None) -> bool:
        """
        Recursively validate data against schema, supporting $ref and oneOf.
        """
        if ref_cache is None:
            ref_cache = {}
        if not isinstance(schema, dict):
            return True  # No schema constraints

        # $ref resolution
        if "$ref" in schema:
            ref = schema["$ref"]
            if ref in ref_cache:
                ref_schema = ref_cache[ref]
            else:
                # Only support local refs for now
                if ref.startswith("#"):
                    # Remove leading '#' and split by '/'
                    path = ref.lstrip('#/').split('/')
                    ref_schema = self._schema_data
                    for p in path:
                        if p:
                            ref_schema = ref_schema.get(p)
                    ref_cache[ref] = ref_schema
                else:
                    # External refs not supported in this minimal validator
                    return False
            return self._validate_recursive(data, ref_schema, ref_cache)

        # oneOf support
        if "oneOf" in schema:
            for option in schema["oneOf"]:
                if self._validate_recursive(data, option, ref_cache):
                    return True
            return False

        # Type validation
        schema_type = schema.get('type')
        if schema_type:
            if schema_type == 'object' and not isinstance(data, dict):
                return False
            elif schema_type == 'array' and not isinstance(data, list):
                return False
            elif schema_type == 'string' and not isinstance(data, str):
                return False
            elif schema_type == 'integer' and not isinstance(data, int):
                return False
            elif schema_type == 'number' and not isinstance(data, (int, float)):
                return False
            elif schema_type == 'boolean' and not isinstance(data, bool):
                return False
            elif schema_type == 'null' and data is not None:
                return False

        # Handle different types
        if schema_type == 'object' and isinstance(data, dict):
            return self._validate_object(data, schema, ref_cache)
        elif schema_type == 'array' and isinstance(data, list):
            return self._validate_array(data, schema, ref_cache)
        elif schema_type == 'string' and isinstance(data, str):
            return self._validate_string(data, schema)
        elif schema_type in ['integer', 'number'] and isinstance(data, (int, float)):
            return self._validate_number(data, schema)
        elif schema_type == 'boolean' and isinstance(data, bool):
            return True  # Boolean validation is just type check

        return True

    def _validate_object(self, data: dict, schema: dict, ref_cache=None) -> bool:
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        # Check required fields
        for field in required:
            if field not in data:
                return False
        # Validate each property
        for field_name, field_value in data.items():
            if field_name in properties:
                field_schema = properties[field_name]
                if not self._validate_recursive(field_value, field_schema, ref_cache):
                    return False
        return True

    def _validate_array(self, data: list, schema: dict, ref_cache=None) -> bool:
        items_schema = schema.get('items')
        min_items = schema.get('minItems')
        max_items = schema.get('maxItems')
        if min_items is not None and len(data) < min_items:
            return False
        if max_items is not None and len(data) > max_items:
            return False
        if items_schema:
            for item in data:
                if not self._validate_recursive(item, items_schema, ref_cache):
                    return False
        return True
    
    def _validate_string(self, data: str, schema: dict) -> bool:
        """Validate string against schema."""
        min_length = schema.get('minLength')
        max_length = schema.get('maxLength')
        pattern = schema.get('pattern')
        
        # Check length constraints
        if min_length is not None and len(data) < min_length:
            return False
        if max_length is not None and len(data) > max_length:
            return False
        
        # Check pattern
        if pattern:
            import re
            if not re.match(pattern, data):
                return False
        
        return True
    
    def _validate_number(self, data: (int, float), schema: dict) -> bool:
        """Validate number against schema."""
        minimum = schema.get('minimum')
        maximum = schema.get('maximum')
        
        # Check range constraints
        if minimum is not None and data < minimum:
            return False
        if maximum is not None and data > maximum:
            return False
        
        return True
    
    @property
    def _schema_hash(self) -> int:
        """Get hash of schema for caching."""
        return hash(str(self._schema_data))
    
    @classmethod
    def clear_cache(cls):
        """Clear schema cache."""
        global _schema_cache
        _schema_cache.clear()
        logger.debug("🗑️ Schema cache cleared") 