"""
xSchema new_2 Unified Utils

Utility functions for xSchema new_2 implementation.
"""

from typing import Any, Dict, Optional, Union


class UnifiedUtils:
    """
    Unified utilities for xSchema new_2.
    """
    
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
