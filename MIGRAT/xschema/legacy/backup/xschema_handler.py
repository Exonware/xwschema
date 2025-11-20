"""
Schema handler classes for xData framework.
"""

from typing import Any, Dict, List, Optional, Union, Type
from abc import ABC, abstractmethod
import logging

from .exceptions import (
    ConfigurationError, FormatNotSupportedError
)

logger = logging.getLogger(__name__)

# ======================
# Abstract Schema Handler
# ======================
class aSchemaHandler(ABC):
    """Base for format-specific schema parsing and validation logic."""

    @staticmethod
    @abstractmethod
    def parse_schema(schema_content: Union[str, bytes], **kwargs: Any) -> Dict[Any, Any]:
        """Parse schema content into a Python dictionary representation."""

    @staticmethod
    @abstractmethod
    def validate_data(data: Dict[Any, Any], schema: Dict[Any, Any], **kwargs: Any) -> bool:
        """Validate data against the provided schema."""

    @staticmethod
    @abstractmethod
    def generate_schema(data: Dict[Any, Any], **kwargs: Any) -> Dict[Any, Any]:
        """Generate schema from sample data."""

    @staticmethod
    def can_handle_schema(schema_content: Union[str, bytes]) -> bool:
        """Optional: Lightweight check if handler can process schema content."""
        return False

    @staticmethod
    def is_binary_schema() -> bool:
        """Indicates if the schema format is binary (bytes) or text (str)."""
        return False

# ======================
# Schema Handler Factory
# ======================
class xSchemaHandlerFactory:
    _schema_handlers: Dict[str, Type[aSchemaHandler]] = {}
    _schema_extensions: Dict[str, str] = {}

    @classmethod
    def register(cls, name: str, handler_class: Type[aSchemaHandler], extensions: Optional[List[str]] = None) -> None:
        if not issubclass(handler_class, aSchemaHandler):
            raise ConfigurationError(f"Schema handler for '{name}' must be a subclass of aSchemaHandler.")
        name_lower = name.lower()
        cls._schema_handlers[name_lower] = handler_class
        processed_exts: List[str] = []
        if extensions:
            processed_exts = [ext.lower().lstrip('.') for ext in extensions]
        elif name_lower not in processed_exts:
            processed_exts.append(name_lower)
        for ext in processed_exts:
            if ext in cls._schema_extensions and cls._schema_extensions[ext] != name_lower:
                logger.debug(f"Schema extension '.{ext}' registered for both '{cls._schema_extensions[ext]}' and '{name_lower}'. Will use content detection to choose.")
            cls._schema_extensions[ext] = name_lower

    @classmethod
    def get_handler(cls, name: str) -> Type[aSchemaHandler]:
        handler = cls._schema_handlers.get(name.lower())
        if not handler:
            raise FormatNotSupportedError(f"No schema handler registered for format: {name}")
        return handler

    @classmethod
    def get_handler_if_exists(cls, name: str) -> Optional[Type[aSchemaHandler]]:
        return cls._schema_handlers.get(name.lower())

    @classmethod
    def get_format_by_extension(cls, extension: str) -> Optional[str]:
        return cls._schema_extensions.get(extension.lower().lstrip('.'))

    @classmethod
    def detect_format_from_content(cls, schema_content: Union[str, bytes]) -> Optional[str]:
        logger.debug("Attempting to detect schema format from content...")
        for name, handler_class in cls._schema_handlers.items():
            try:
                if handler_class.can_handle_schema(schema_content):
                    logger.info(f"Schema content auto-detected as format: {name}")
                    return name
            except Exception as e:
                logger.warning(f"Error in can_handle_schema for {name} during content detection: {e}", exc_info=True)
        logger.info("Schema content auto-detection failed for all registered handlers.")
        return None

    @classmethod
    def get_available_formats(cls) -> List[str]:
        return list(cls._schema_handlers.keys()) 