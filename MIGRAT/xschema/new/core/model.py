"""
xSchema new Core Model

Core model classes for xSchema new implementation.
"""

from typing import Any, Dict, Optional, Union
import uuid


class aDataNode:
    """
    Abstract data node for xSchema new.
    """
    
    def __init__(self, value: Any = None, metadata: Optional[Dict] = None):
        self._value = value
        self._metadata = metadata or {}
        self._id = uuid.uuid4()
    
    @property
    def value(self) -> Any:
        """Get the node value."""
        return self._value
    
    @value.setter
    def value(self, value: Any) -> None:
        """Set the node value."""
        self._value = value
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get node metadata."""
        return self._metadata
    
    @property
    def id(self) -> uuid.UUID:
        """Get node unique identifier."""
        return self._id
    
    def to_native(self) -> Any:
        """Convert node to native Python type."""
        return self._value
    
    def __str__(self) -> str:
        return f"aDataNode(value={self._value})"
    
    def __repr__(self) -> str:
        return f"aDataNode(value={repr(self._value)}, metadata={self._metadata})"
