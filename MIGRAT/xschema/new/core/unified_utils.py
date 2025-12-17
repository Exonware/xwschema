"""
xSchema new Unified Utils

Utility functions for xSchema new implementation.
"""

from typing import Any, Dict, Optional, Union, Callable
from pathlib import Path
import json

from src.xlib.xwsystem import get_logger
from .config import get_config
from .errors import XSchemaError

logger = get_logger(__name__)


class UnifiedUtils:
    """
    Unified utilities for xSchema new.
    """
    
    # Shared caches - class level for efficiency
    _config_cache = None
    _processor_caches = {}
    
    @classmethod
    def get_config(cls):
        """Get cached configuration."""
        if cls._config_cache is None:
            cls._config_cache = get_config()
        return cls._config_cache
    
    @classmethod
    def get_or_create_processor(cls, processor_key: str, creator_func: Callable):
        """Get or create processor with caching."""
        if processor_key not in cls._processor_caches:
            config = cls.get_config()
            if config.production_mode:
                cls._processor_caches[processor_key] = None
            else:
                cls._processor_caches[processor_key] = creator_func()
        return cls._processor_caches[processor_key]
    
    @staticmethod
    def validate_schema(schema_data: Dict[str, Any]) -> bool:
        """Validate schema data structure."""
        if not isinstance(schema_data, dict):
            return False
        
        # Basic schema validation
        if 'type' in schema_data:
            valid_types = ['object', 'array', 'string', 'integer', 'number', 'boolean']
            if schema_data['type'] not in valid_types:
                return False
        
        return True
    
    @staticmethod
    def merge_schemas(schema1: Dict[str, Any], schema2: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two schemas."""
        result = schema1.copy()
        
        # Merge properties if both are object types
        if (schema1.get('type') == 'object' and 
            schema2.get('type') == 'object' and
            'properties' in schema1 and 'properties' in schema2):
            result['properties'] = {**schema1['properties'], **schema2['properties']}
        
        return result
    
    @staticmethod
    def get_schema_type(schema_data: Dict[str, Any]) -> str:
        """Get the type from schema data."""
        return schema_data.get('type', 'object')
    
    @classmethod
    def fast_validation(
        cls, 
        data: Any, 
        schema: Any, 
        simple_validator: Callable,
        processor,
        normal_validator: Callable = None,
        **kwargs
    ) -> bool:
        """
        Ultra-fast validation logic shared by Data and Schema.
        """
        config = cls.get_config()
        
        # Fast path for minimal validation
        if kwargs.get('fast_validation', False) or not processor or config.production_mode:
            if config.enable_debug_logging:
                logger.debug("⚡ Fast validation path")
            
            result = simple_validator(data, schema)
            
            if config.enable_debug_logging:
                logger.info("⚡ Fast validation completed")
            
            return result
        
        # Normal validation path
        if normal_validator:
            return normal_validator(data, schema, **kwargs)
        else:
            return True  # Fallback
    
    @classmethod
    def clear_all_caches(cls):
        """Clear all shared caches."""
        cls._config_cache = None
        cls._processor_caches.clear()
        
        config = cls.get_config()
        if config and config.enable_debug_logging:
            logger.debug("🔄 All unified caches cleared")
