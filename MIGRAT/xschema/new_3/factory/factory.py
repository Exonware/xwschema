"""
xSchema new_3 Factory

Factory classes for creating xSchema new_3 instances.
"""

from typing import Any, Dict, Optional, Union
from ..model.base import xDataNode
from ..model.schema import xSchemaNode


class xDataFactory:
    """
    Factory for creating xData nodes in xSchema new_3.
    """
    
    @staticmethod
    def create_node(value: Any = None, metadata: Optional[Dict] = None) -> xDataNode:
        """Create a basic xData node."""
        return xDataNode(value, metadata)
    
    @staticmethod
    def create_schema_node(schema_data: Dict[str, Any], metadata: Optional[Dict] = None) -> xSchemaNode:
        """Create a schema node."""
        return xSchemaNode(schema_data, metadata)
    
    @staticmethod
    def create_from_native(data: Any, metadata: Optional[Dict] = None) -> xDataNode:
        """Create a node from native Python data."""
        if isinstance(data, dict):
            return xSchemaNode(data, metadata)
        else:
            return xDataNode(data, metadata)
    
    @staticmethod
    def create_from_file(file_path: str, metadata: Optional[Dict] = None) -> xDataNode:
        """Create a node from file (simplified implementation)."""
        import json
        from pathlib import Path
        
        path = Path(file_path)
        if path.suffix.lower() == '.json':
            with open(path, 'r') as f:
                data = json.load(f)
            return xDataFactory.create_from_native(data, metadata)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
