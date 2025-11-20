"""
xSchema new_3 Base Model

Core base classes for xSchema new_3 implementation.
"""

from typing import Any, Dict, Optional, Union
import uuid


class xDataNode:
    """
    Base class for xData nodes in xSchema new_3.
    
    This is a simplified version that provides the basic interface
    needed by xSchema new_3 facade.
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
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value by key."""
        return self._metadata.get(key, default)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value by key."""
        self._metadata[key] = value
    
    def to_native(self) -> Any:
        """Convert node to native Python type."""
        return self._value
    
    def __str__(self) -> str:
        return f"xDataNode(value={self._value})"
    
    def __repr__(self) -> str:
        return f"xDataNode(value={repr(self._value)}, metadata={self._metadata})"
