"""
xSchema Handlers Module
======================

This module provides schema handlers for various formats, extracted from xData handlers
for schema-specific operations. It includes handlers for JSON, YAML, TOML, and other formats.
"""

import importlib
import inspect
import logging
from typing import Any, Dict, List, Optional, Type, Union

from src.xlib.xschema.legacy.schema_handler import aSchemaHandler

logger = logging.getLogger(__name__)

# Registry for schema handlers
_schema_handlers: Dict[str, Type[aSchemaHandler]] = {}
_schema_extensions: Dict[str, str] = {}

def register_schema_handler(name: str, handler_class: Type[aSchemaHandler], extensions: Optional[List[str]] = None) -> None:
    """
    Register a schema handler.
    
    Args:
        name: Name of the handler
        handler_class: Handler class to register
        extensions: List of file extensions this handler supports
    """
    if not issubclass(handler_class, aSchemaHandler):
        raise ValueError(f"Handler {name} must inherit from aSchemaHandler")
    
    _schema_handlers[name] = handler_class
    
    if extensions:
        for ext in extensions:
            _schema_extensions[ext.lower()] = name
    
    logger.debug(f"Registered schema handler: {name}")

def get_schema_handler(name: str) -> Optional[Type[aSchemaHandler]]:
    """
    Get a schema handler by name.
    
    Args:
        name: Name of the handler
        
    Returns:
        Handler class or None if not found
    """
    return _schema_handlers.get(name)

def get_schema_handler_by_extension(extension: str) -> Optional[Type[aSchemaHandler]]:
    """
    Get a schema handler by file extension.
    
    Args:
        extension: File extension (without dot)
        
    Returns:
        Handler class or None if not found
    """
    handler_name = _schema_extensions.get(extension.lower())
    if handler_name:
        return _schema_handlers.get(handler_name)
    return None

def get_all_schema_handlers() -> Dict[str, Type[aSchemaHandler]]:
    """
    Get all registered schema handlers.
    
    Returns:
        Dictionary of handler names to handler classes
    """
    return _schema_handlers.copy()

def get_supported_extensions() -> List[str]:
    """
    Get all supported file extensions.
    
    Returns:
        List of supported file extensions
    """
    return list(_schema_extensions.keys())

def discover_schema_handlers() -> None:
    """
    Automatically discover and register schema handlers from this module.
    """
    # Import all handler modules
    handler_modules = [
        'json_schema_handler',
        'yaml_schema_handler', 
        'toml_schema_handler',
        'xml_schema_handler',
        'numpy_schema_handler'
    ]
    
    for module_name in handler_modules:
        try:
            module = importlib.import_module(f'.{module_name}', __name__)
            
            # Find handler classes in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, aSchemaHandler) and 
                    obj != aSchemaHandler):
                    
                    # Register the handler
                    handler_name = name.lower().replace('schemahandler', '')
                    extensions = getattr(obj, 'all_extensions', [])
                    
                    register_schema_handler(handler_name, obj, extensions)
                    logger.info(f"Discovered schema handler: {handler_name}")
                    
        except ImportError as e:
            logger.warning(f"Could not import schema handler module {module_name}: {e}")
        except Exception as e:
            logger.error(f"Error discovering schema handler {module_name}: {e}")

def detect_schema_format(content: Union[str, bytes]) -> Optional[str]:
    """
    Detect the schema format from content.
    
    Args:
        content: Schema content to analyze
        
    Returns:
        Handler name or None if format cannot be detected
    """
    content_str = content.decode('utf-8') if isinstance(content, bytes) else content
    
    # Try each handler's can_handle method
    for handler_name, handler_class in _schema_handlers.items():
        try:
            if handler_class.can_handle_schema(content_str):
                return handler_name
        except Exception as e:
            logger.debug(f"Error checking handler {handler_name}: {e}")
    
    return None

def parse_schema(content: Union[str, bytes], format_hint: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Parse schema content using the appropriate handler.
    
    Args:
        content: Schema content to parse
        format_hint: Optional format hint to use specific handler
        **kwargs: Additional parsing options
        
    Returns:
        Parsed schema as dictionary
        
    Raises:
        ValueError: If no suitable handler is found
    """
    if format_hint:
        handler_class = get_schema_handler(format_hint)
        if not handler_class:
            raise ValueError(f"Unknown schema format: {format_hint}")
    else:
        # Auto-detect format
        detected_format = detect_schema_format(content)
        if not detected_format:
            raise ValueError("Could not detect schema format")
        
        handler_class = get_schema_handler(detected_format)
        if not handler_class:
            raise ValueError(f"Handler not found for format: {detected_format}")
    
    return handler_class.parse_schema(content, **kwargs)

def serialize_schema(schema: Dict[str, Any], format_hint: str, **kwargs) -> str:
    """
    Serialize schema using the specified handler.
    
    Args:
        schema: Schema to serialize
        format_hint: Format to serialize to
        **kwargs: Additional serialization options
        
    Returns:
        Serialized schema as string
        
    Raises:
        ValueError: If handler is not found
    """
    handler_class = get_schema_handler(format_hint)
    if not handler_class:
        raise ValueError(f"Unknown schema format: {format_hint}")
    
    return handler_class.serialize_schema(schema, **kwargs)

def validate_data(data: Any, schema: Dict[str, Any], format_hint: Optional[str] = None, **kwargs) -> bool:
    """
    Validate data against schema using the appropriate handler.
    
    Args:
        data: Data to validate
        schema: Schema to validate against
        format_hint: Optional format hint to use specific handler
        **kwargs: Additional validation options
        
    Returns:
        True if valid, False otherwise
    """
    if format_hint:
        handler_class = get_schema_handler(format_hint)
        if not handler_class:
            return False
    else:
        # Try each handler until one succeeds
        for handler_class in _schema_handlers.values():
            try:
                if handler_class.validate_data(data, schema, **kwargs):
                    return True
            except Exception:
                continue
        return False
    
    return handler_class.validate_data(data, schema, **kwargs)

def generate_schema(data: Any, format_hint: str, **kwargs) -> Dict[str, Any]:
    """
    Generate schema from sample data using the specified handler.
    
    Args:
        data: Sample data to generate schema from
        format_hint: Format to generate schema in
        **kwargs: Additional generation options
        
    Returns:
        Generated schema as dictionary
        
    Raises:
        ValueError: If handler is not found
    """
    handler_class = get_schema_handler(format_hint)
    if not handler_class:
        raise ValueError(f"Unknown schema format: {format_hint}")
    
    return handler_class.generate_schema(data, **kwargs)

# Auto-discover handlers when module is imported
discover_schema_handlers()

__all__ = [
    'register_schema_handler',
    'get_schema_handler', 
    'get_schema_handler_by_extension',
    'get_all_schema_handlers',
    'get_supported_extensions',
    'discover_schema_handlers',
    'detect_schema_format',
    'parse_schema',
    'serialize_schema',
    'validate_data',
    'generate_schema'
]
