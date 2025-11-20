"""
Schema handler classes for xData framework.
"""

from typing import Any, Dict, List, Optional, Union, Type, TYPE_CHECKING
from abc import ABC, abstractmethod
import logging

from src.xlib.xdata.core.exceptions import (
    ConfigurationError, FormatNotSupportedError
)
from src.xlib.xdata.core.exceptions import (
    ReferenceError, CircularReferenceError, ReferenceResolutionError, ReferenceLoadError, ReferenceCopyError, ReferenceValidationError, ReferenceSecurityError
)
from src.xlib.xdata.core.base_handler import aBaseHandler

if TYPE_CHECKING:
    from .facade import xSchema

logger = logging.getLogger(__name__)

# ======================
# Abstract Schema Handler
# ======================
class aSchemaHandler(aBaseHandler):
    """
    Abstract base class for all xData **schema** handlers.
    
    This class defines the interface for parsing, serializing, validating,
    and generating schemas for a specific format (e.g., JSON Schema, XSD).
    """
    
    # Override format category
    format_category: str = "schema"

    @staticmethod
    @abstractmethod
    def parse_schema(schema_content: Union[str, bytes], **kwargs: Any) -> 'xSchema':
        """Parse schema content into a Python dictionary representation."""

    @staticmethod
    @abstractmethod
    def validate_data(data: Dict[Any, Any], schema: 'xSchema', **kwargs: Any) -> bool:
        """Validate data against the provided schema."""

    @staticmethod
    @abstractmethod
    def generate_schema(data: Dict[Any, Any], **kwargs: Any) -> 'xSchema':
        """Generate schema from sample data."""

    @staticmethod
    @abstractmethod  
    def serialize_schema(schema: 'xSchema', **kwargs: Any) -> Union[str, bytes]:
        """Serialize an xSchema object to string or bytes."""

    # --- Base Handler Interface Implementation ---

    @staticmethod
    def parse(content: Union[str, bytes], **kwargs: Any) -> 'xSchema':
        """
        Base interface implementation - subclasses must override to delegate to parse_schema.
        
        This method provides the common interface required by aBaseHandler.
        Concrete handlers must implement this to call their parse_schema method.
        
        Args:
            content: Raw schema content to parse
            **kwargs: Additional parsing options
            
        Returns:
            xSchema: Parsed schema object
            
        Raises:
            NotImplementedError: If concrete handler doesn't implement delegation
        """
        raise NotImplementedError("Concrete handlers must implement parse() to delegate to parse_schema()")

    @staticmethod  
    def serialize(data: 'xSchema', **kwargs: Any) -> Union[str, bytes]:
        """
        Base interface implementation - subclasses must override to delegate to serialize_schema.
        
        This method provides the common interface required by aBaseHandler.
        Concrete handlers must implement this to call their serialize_schema method.
        
        Args:
            data: xSchema object to serialize
            **kwargs: Additional serialization options
            
        Returns:
            Union[str, bytes]: Serialized schema
            
        Raises:
            NotImplementedError: If concrete handler doesn't implement delegation
        """
        raise NotImplementedError("Concrete handlers must implement serialize() to delegate to serialize_schema()")

    @staticmethod
    def can_handle(content: Union[str, bytes]) -> bool:
        """
        Base interface implementation - concrete handlers should override this.
        
        This provides a common interface. Concrete handlers should override this
        to call their can_handle_schema method or implement custom logic.
        
        Args:
            content: Raw content to check
            
        Returns:
            bool: True if this handler can process the schema content
        """
        # Default implementation returns False
        # Concrete handlers should override this method
        return False

    @staticmethod
    def is_binary_format() -> bool:
        """
        Base interface implementation - concrete handlers should override this.
        
        This provides a common interface. Concrete handlers should override this
        to call their is_binary_schema method or implement custom logic.
        
        Returns:
            bool: True if schema format is binary, False if text
        """
        # Default implementation returns False (text format)
        # Concrete handlers should override this method
        return False

    @staticmethod
    def supports_feature(feature: str) -> bool:
        """
        Schema handler feature support capabilities.
        
        Args:
            feature: Feature name to check support for
            
        Returns:
            bool: True if feature is supported by schema handlers
        """
        # Get base features first
        from ..core.base_handler import aBaseHandler
        if aBaseHandler.supports_feature(feature):
            return True
            
        # Schema-specific features
        schema_features = {
            'validation': True,           # Schema handlers support data validation
            'generation': True,           # Schema handlers can generate schemas
            'references': False,          # Override if supported by specific handler
            'versioning': False,          # Override if supported by specific handler
            'inheritance': False,         # Override if supported (e.g., JSON Schema $ref)
            'composition': False,         # Override if supported (e.g., allOf, anyOf)
            'conditional': False,         # Override if supported (e.g., if/then/else)
            'format_validation': False,   # Override if supported (e.g., date, email formats)
            'custom_keywords': False,     # Override if handler supports custom schema keywords
            'schema_evolution': False,    # Override if supports schema migration/evolution
            'documentation': False,       # Override if supports embedded documentation
            'examples': False,            # Override if supports example values in schema
            'defaults': False,            # Override if supports default values
            'constraints': True,          # Schema handlers support validation constraints
            'type_checking': True,        # Schema handlers support type validation
            'range_validation': False,    # Override if supports min/max constraints
            'pattern_matching': False,    # Override if supports regex/pattern validation
            'enum_validation': False,     # Override if supports enumeration constraints
            'cross_field_validation': False, # Override if supports field interdependencies
            'schema_composition': False,  # Override if supports combining multiple schemas
            'polymorphism': False,        # Override if supports polymorphic schemas
            'schema_introspection': True, # Schema handlers can analyze schema structure
            'error_reporting': True,      # Schema handlers provide validation error details
            'localization': False,        # Override if supports localized error messages
            'performance_validation': False # Override if optimized for high-perf validation
        }
        return schema_features.get(feature, False)

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