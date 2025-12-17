#!/usr/bin/env python3
"""
🚀 xSchema Engine Module
Core engine implementation for the xSchema facade pattern.
"""

import uuid
import weakref
import threading
from typing import Any, Dict, Iterator, Optional, Set, Union, ContextManager
from collections.abc import MutableMapping

from .config import xSchemaConfig
from .validation import SchemaValidationService
from src.xlib.xdata.core.exceptions import SchemaError, SchemaValidationError
from src.xlib.xwsystem.monitoring.performance_monitor import logger
# Import legacy xData directly to ensure compatibility
from src.xlib.xdata.data.facade import xData

# Forward declarations for type hints
if False:  # TYPE_CHECKING
    from .facade import xSchema


class _xSchemaParentRegistry:
    """🔑 Thread-safe registry for UUID-based parent lookup."""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._registry = {}
        return cls._instance
    
    def register(self, parent_id: uuid.UUID, parent: 'xSchema') -> None:
        """Register a parent instance with its UUID."""
        with self._lock:
            self._registry[parent_id] = weakref.ref(parent)
    
    def lookup(self, parent_id: uuid.UUID) -> Optional['xSchema']:
        """Look up a parent instance by UUID."""
        with self._lock:
            ref = self._registry.get(parent_id)
            return ref() if ref else None
    
    def unregister(self, parent_id: uuid.UUID) -> None:
        """Unregister a parent instance."""
        with self._lock:
            self._registry.pop(parent_id, None)
    
    def clear(self) -> None:
        """Clear all registrations."""
        with self._lock:
            self._registry.clear()


# Global registry instance
_parent_registry = _xSchemaParentRegistry()


def _get_parent_by_id(parent_id: uuid.UUID) -> Optional['xSchema']:
    """Get parent instance by UUID."""
    return _parent_registry.lookup(parent_id)


class _xSchemaEngine:
    """
    🚀 Internal xSchema Engine implementing the Facade Pattern.
    
    This engine aggregates all xSchema components into a single, unified interface.
    It provides UUID-based identification, thread-safe operations, and clean
    component management.
    
    Architecture:
    - Facade Pattern: Provides simplified interface to complex subsystems
    - UUID-based Identification: Safe caching and component references
    - Component Aggregation: Single point of control for all xSchema operations
    - Thread Safety: Coordinated locking across all components
    """
    
    def __init__(self, config: xSchemaConfig, base_path: Optional[str] = None):
        """
        Initialize the xSchema engine with service-based architecture.
        
        Args:
            config: Configuration object for all services
            base_path: Base directory for resolving relative paths
        """
        # 🔑 UUID-based identification for safe caching and references
        self.id = uuid.uuid4()
        self.config = config
        self.base_path = base_path
        
        # 🎯 Initialize services and core components
        # Convert xSchemaConfig to xDataConfig for xData compatibility
        from src.xlib.xdata.core.config import xDataConfig
        xdata_config = xDataConfig.from_kwargs(
            enable_thread_safety=config.threading.enable_thread_safety,
            enable_path_security=config.security.enable_path_security,
            enable_performance_monitoring=config.performance.enable_monitoring,
            handle_references=config.references.handle_references.value if hasattr(config.references.handle_references, 'value') else config.references.handle_references,
            user_defined_links=config.references.user_defined_links,
            wrap_nested_fields=config.wrap_nested_fields if hasattr(config, 'wrap_nested_fields') else False,
            path_delimiter=config.path.path_delimiter,
            encoding=config.encoding.default_encoding if hasattr(config.encoding, 'default_encoding') else 'utf-8'
        )
        
        # Initialize xData with empty data to avoid None source issues
        self._definition = xData({}, config=xdata_config, base_path=base_path)
        self._validation = SchemaValidationService(config)
        
        # 🔗 Parent registry integration for UUID-based lookup
        self._facade_ref: Optional[weakref.ref] = None
        
        logger.debug(f"🚀 xSchema Engine initialized with service architecture (UUID: {self.id})")
    
    def load_schema(self, xschema_instance: 'xSchema', *sources: Union[str, bytes, Dict[Any, Any], 'xSchema'], 
                   format: Optional[str] = None, **kwargs: Any) -> None:
        """Load and merge multiple schema sources into the engine."""
        # TODO: Implement schema loading through loading service
        # For now, just set the first source as data
        if sources:
            first_source = sources[0]
            if isinstance(first_source, dict):
                self._definition.data = first_source
            elif isinstance(first_source, xSchema):
                self._definition.data = first_source._engine.get_schema_data(first_source)
    
    def validate_data(self, xschema_instance: 'xSchema', data: Any, **kwargs: Any) -> bool:
        """Validate data against schema through the validation service."""
        return self._validation.validate_data(xschema_instance, data, **kwargs)
    
    def get_schema_data(self, xschema_instance: 'xSchema') -> Dict[str, Any]:
        """Get schema data from the internal xData object."""
        # Get data directly from storage service
        data = self._definition._engine._storage.get_data()
        if data is None:
            return {}
        return data
    
    def set_schema_data(self, xschema_instance: 'xSchema', data: Any) -> None:
        """Set schema data into the internal xData object."""
        # Clear existing data and set new data
        self._definition._engine._storage.clear_data()
        if isinstance(data, dict):
            # Use the storage service to set data directly
            self._definition._engine._storage.set_data(data)
        elif data is not None:
            # For non-dict data, try to convert or handle appropriately
            self._definition._engine._storage.set_data({})
        
    def get_property(self, key: str) -> Any:
        """Get a property from the schema definition."""
        return self._definition._engine.get(self._definition, key)
        
    def set_property(self, key: str, value: Any) -> None:
        """Set a property in the schema definition."""
        self._definition._engine.set(self._definition, key, value)
    
    def export_schema(self, xschema_instance: 'xSchema', format: str, **kwargs: Any) -> Union[str, bytes]:
        """Export schema in specified format through the serialization service."""
        # TODO: Implement through serialization service
        # For now, return empty string
        return ""
    
    def save_schema_to_file(self, xschema_instance: 'xSchema', file_path: str, format: Optional[str] = None, **kwargs: Any) -> None:
        """Save schema to file through the serialization service."""
        # TODO: Implement through serialization service
        pass
    
    def to_native(self, xschema_instance: 'xSchema', resolve_refs: bool = True) -> Dict[str, Any]:
        """Convert schema to dictionary through the storage service."""
        data = self._definition._engine._storage.get_data()
        if data is None:
            return {}
        if resolve_refs:
            # TODO: Implement reference resolution through processing service
            pass
        return data
    
    def clear(self) -> None:
        """Clear all schema data."""
        self._definition._engine._storage.clear_data()
    
    def __len__(self) -> int:
        """Get number of top-level schema keys."""
        data = self._definition._engine._storage.get_data()
        return len(data) if data is not None else 0
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over top-level schema keys."""
        data = self._definition._engine._storage.get_data()
        return iter(data) if data is not None else iter({})
    
    def __contains__(self, key: Any) -> bool:
        """Check if schema key exists."""
        data = self._definition._engine._storage.get_data()
        return key in data if data is not None else False
    
    def keys(self):
        """Get schema keys view."""
        data = self._definition._engine._storage.get_data()
        return data.keys() if data is not None else {}.keys()
    
    def values(self):
        """Get schema values view."""
        data = self._definition._engine._storage.get_data()
        return data.values() if data is not None else {}.values()
    
    def items(self):
        """Get schema items view."""
        data = self._definition._engine._storage.get_data()
        return data.items() if data is not None else {}.items()
    
    def with_thread_safety(self) -> ContextManager:
        """Get thread safety context manager."""
        # TODO: Implement through threading service
        from contextlib import nullcontext
        return nullcontext()
    
    def with_performance_monitoring(self, operation: str) -> ContextManager:
        """Get performance monitoring context manager."""
        # TODO: Implement through monitoring service
        from contextlib import nullcontext
        return nullcontext()
    
    def set_facade_reference(self, facade: 'xSchema') -> None:
        """🔗 Set reference to the xSchema facade and register with parent registry."""
        self._facade_ref = weakref.ref(facade)
        _parent_registry.register(self.id, facade)
        logger.debug(f"🔗 Facade reference set and registered (UUID: {self.id})")
        
    def get_facade(self) -> Optional['xSchema']:
        """Get the facade reference."""
        return self._facade_ref() if self._facade_ref else None
    
    def cleanup(self) -> None:
        """Clean up engine resources."""
        _parent_registry.unregister(self.id)
        logger.debug(f"🧹 Engine cleaned up (UUID: {self.id})") 