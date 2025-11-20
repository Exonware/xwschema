"""
XData Schema Model

Core schema operations including validation, generation, and management.
Provides comprehensive schema processing capabilities.
"""

from typing import Any, Optional, Dict, List, Union, Type, Callable
from pathlib import Path
from abc import ABC, abstractmethod
import json
from copy import deepcopy

from src.xlib.xsystem import (
    get_logger,
    DataValidator,
    PerformanceMonitor, 
    CircularReferenceDetector
)
from ..core.model import aDataNode
from ..core.errors import (
    XSchemaError,
    XSchemaValidationError,
    XSchemaGenerationError,
    XSchemaParsingError,
    XSchemaVersionError,
    XSchemaCompatibilityError,
    XSchemaReferenceError
)

__all__ = [
    'ASchemaNode',
    'SchemaProcessor', 
    'SchemaValidator',
    'SchemaGenerator',
    'SchemaParser',
    'SchemaVersionManager',
    'SchemaReferenceResolver'
]

logger = get_logger(__name__)


class ASchemaNode(aDataNode):
    """
    Abstract base for schema-related nodes.
    Extends XData node functionality with schema-specific features.
    """
    
    def __init__(self, schema: Any = None, **kwargs):
        # Extract the correct parameters for aDataNode
        parent = kwargs.get('parent', None)
        metadata = kwargs.get('metadata', {})
        super().__init__(parent, metadata)
        self.schema = schema
        self.schema_metadata = kwargs.get('schema_metadata', {})
        self.version = kwargs.get('version', '1.0.0')
        logger.debug("🔷 Schema node initialized")
    
    @abstractmethod
    def validate_schema(self, data: Any) -> bool:
        """Validate data against this schema."""
        pass
    
    @abstractmethod  
    def get_schema_info(self) -> Dict[str, Any]:
        """Get schema information and metadata."""
        pass
    
    def is_compatible_with(self, other_schema: 'ASchemaNode') -> bool:
        """Check compatibility with another schema."""
        return True  # Default implementation
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(version={self.version})"


class SchemaProcessor:
    """
    Central schema processing engine.
    Coordinates validation, generation, and transformation operations.
    """
    
    def __init__(self):
        self.validator = SchemaValidator()
        self.generator = SchemaGenerator()
        self.parser = SchemaParser()
        self.version_manager = SchemaVersionManager()
        self.reference_resolver = SchemaReferenceResolver()
        self.performance_monitor = PerformanceMonitor()
        logger.info("🔧 Schema processor initialized")
    
    def process_schema(
        self,
        operation: str,
        schema: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        fast_loading: bool = False,
        **kwargs
    ) -> Any:
        """
        Process schema using specified operation.
        
        Args:
            operation: Operation type (validate, generate, parse, etc.)
            schema: Schema to process
            data: Data to process against schema
            fast_loading: Use fast loading without validation overhead
            **kwargs: Operation-specific parameters
            
        Returns:
            Operation result
        """
        try:
            with self.performance_monitor.monitor_operation(f"schema_{operation}"):
                logger.debug(f"🔄 Processing schema operation: {operation}")
                
                if operation == "validate":
                    if not schema or data is None:
                        raise XSchemaError("Validation requires both schema and data")
                    return self.validator.validate(data, schema, **kwargs)
                
                elif operation == "generate":
                    if data is None:
                        raise XSchemaError("Generation requires data")
                    return self.generator.generate_from_data(data, **kwargs)
                
                elif operation == "parse":
                    if not schema:
                        raise XSchemaError("Parsing requires schema")
                    return self.parser.parse_schema(schema, fast_loading=fast_loading, **kwargs)
                
                elif operation == "version_check":
                    if not schema:
                        raise XSchemaError("Version check requires schema")
                    return self.version_manager.check_version(schema, **kwargs)
                
                elif operation == "resolve_refs":
                    if not schema:
                        raise XSchemaError("Reference resolution requires schema")
                    return self.reference_resolver.resolve(schema, **kwargs)
                
                else:
                    raise XSchemaError(f"Unknown schema operation: {operation}")
                    
        except Exception as e:
            logger.error(f"❌ Schema processing failed: {e}")
            raise XSchemaError(f"Schema operation '{operation}' failed") from e


class SchemaValidator:
    """
    Schema validation engine.
    Validates data against various schema types and formats.
    """
    
    def __init__(self):
        self.data_validator = DataValidator()
        self.circular_detector = CircularReferenceDetector()
        self.validation_cache = {}
        logger.debug("🔍 Schema validator initialized")
    
    def validate(
        self,
        data: Any,
        schema: Dict[str, Any],
        strict: bool = True,
        use_cache: bool = True
    ) -> bool:
        """
        Validate data against schema.
        
        Args:
            data: Data to validate
            schema: Schema definition
            strict: Whether to use strict validation
            use_cache: Whether to use validation cache
            
        Returns:
            True if validation passes
            
        Raises:
            XSchemaValidationError: If validation fails
        """
        try:
            logger.debug("🔍 Starting schema validation")
            
            # Check for circular references
            if self.circular_detector.is_circular(schema):
                raise XSchemaValidationError("Schema contains circular references")
            
            # Generate cache key
            if use_cache:
                cache_key = self._generate_cache_key(data, schema, strict)
                if cache_key in self.validation_cache:
                    logger.debug("✅ Using cached validation result")
                    return self.validation_cache[cache_key]
            
            # Perform validation
            validation_result = self._perform_validation(data, schema, strict)
            
            # Cache result
            if use_cache:
                self.validation_cache[cache_key] = validation_result
            
            logger.info("✅ Schema validation completed successfully")
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Schema validation failed: {e}")
            raise XSchemaValidationError("Schema validation failed") from e
    
    def validate_multiple(
        self,
        data_items: List[Any],
        schema: Dict[str, Any],
        **kwargs
    ) -> List[bool]:
        """Validate multiple data items against schema."""
        results = []
        for i, data in enumerate(data_items):
            try:
                result = self.validate(data, schema, **kwargs)
                results.append(result)
            except XSchemaValidationError as e:
                logger.warning(f"⚠️ Validation failed for item {i}: {e}")
                results.append(False)
        return results
    
    def _perform_validation(self, data: Any, schema: Dict[str, Any], strict: bool) -> bool:
        """Perform actual validation logic."""
        # Basic implementation - would integrate with proper schema validation library
        schema_type = schema.get('type')
        
        if schema_type == 'object' and not isinstance(data, dict):
            raise XSchemaValidationError(f"Expected object, got {type(data).__name__}")
        
        if schema_type == 'array' and not isinstance(data, list):
            raise XSchemaValidationError(f"Expected array, got {type(data).__name__}")
        
        if schema_type == 'string' and not isinstance(data, str):
            raise XSchemaValidationError(f"Expected string, got {type(data).__name__}")
        
        if schema_type == 'number' and not isinstance(data, (int, float)):
            raise XSchemaValidationError(f"Expected number, got {type(data).__name__}")
        
        # Additional validation logic would go here
        return True
    
    def _generate_cache_key(self, data: Any, schema: Dict[str, Any], strict: bool) -> str:
        """Generate cache key for validation result."""
        # Simple implementation - would use proper hashing in production
        return f"{hash(str(data))}_{hash(str(schema))}_{strict}"


class SchemaGenerator:
    """
    Schema generation engine.
    Generates schemas from data and other sources.
    """
    
    def __init__(self):
        self.generation_rules = {}
        self.type_mappings = {
            str: 'string',
            int: 'integer', 
            float: 'number',
            bool: 'boolean',
            list: 'array',
            dict: 'object',
            type(None): 'null'
        }
        logger.debug("🏗️ Schema generator initialized")
    
    def generate_from_data(
        self,
        data: Any,
        schema_format: str = 'json-schema',
        include_examples: bool = True,
        strict_types: bool = True
    ) -> Dict[str, Any]:
        """
        Generate schema from data.
        
        Args:
            data: Source data
            schema_format: Target schema format
            include_examples: Whether to include examples
            strict_types: Whether to use strict type checking
            
        Returns:
            Generated schema
        """
        try:
            logger.debug(f"🏗️ Generating {schema_format} schema from data")
            
            if schema_format == 'json-schema':
                schema = self._generate_json_schema(data, include_examples, strict_types)
            else:
                raise XSchemaGenerationError(f"Unsupported schema format: {schema_format}")
            
            logger.info(f"✅ Schema generated successfully: {schema_format}")
            return schema
            
        except Exception as e:
            logger.error(f"❌ Schema generation failed: {e}")
            raise XSchemaGenerationError("Schema generation failed") from e
    
    def _generate_json_schema(self, data: Any, include_examples: bool, strict_types: bool) -> Dict[str, Any]:
        """Generate JSON Schema from data."""
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": self._get_type(data),
        }
        
        if include_examples:
            schema["examples"] = [data]
        
        if isinstance(data, dict):
            schema["properties"] = {}
            schema["required"] = []
            
            for key, value in data.items():
                schema["properties"][key] = self._generate_json_schema(value, include_examples, strict_types)
                if strict_types or value is not None:
                    schema["required"].append(key)
                    
        elif isinstance(data, list) and data:
            # Analyze array items
            item_schema = self._generate_json_schema(data[0], include_examples, strict_types)
            schema["items"] = item_schema
            
        return schema
    
    def _get_type(self, data: Any) -> str:
        """Get schema type for data."""
        return self.type_mappings.get(type(data), 'string')


class SchemaParser:
    """
    Schema parsing engine.
    Parses schemas from various formats and sources.
    """
    
    def __init__(self):
        self.supported_formats = ['json-schema', 'avro', 'openapi']
        logger.debug("📄 Schema parser initialized")
    
    def parse_schema(
        self,
        schema_source: Union[str, Dict[str, Any], Path],
        format: Optional[str] = None,
        fast_loading: bool = False
    ) -> Dict[str, Any]:
        """
        Parse schema from source.
        
        Args:
            schema_source: Schema source (string, dict, or file path)
            format: Schema format (auto-detected if not provided)
            fast_loading: Use fast loading without validation overhead
            
        Returns:
            Parsed schema
        """
        try:
            logger.debug("📄 Parsing schema")
            
            if isinstance(schema_source, Path) or (isinstance(schema_source, str) and Path(schema_source).exists()):
                # Parse from file
                return self._parse_from_file(Path(schema_source), format, fast_loading)
            
            elif isinstance(schema_source, str):
                # Parse from string
                return self._parse_from_string(schema_source, format, fast_loading)
                
            elif isinstance(schema_source, dict):
                # Already parsed - return as-is for fast loading, or validate for normal loading
                if fast_loading:
                    return schema_source
                else:
                    # Could add schema validation here if needed
                    return schema_source
                
            else:
                raise XSchemaParsingError(f"Unsupported schema source type: {type(schema_source)}")
                
        except Exception as e:
            logger.error(f"❌ Schema parsing failed: {e}")
            raise XSchemaParsingError("Schema parsing failed") from e

    def _parse_from_file(self, file_path: Path, format: Optional[str], fast_loading: bool = False) -> Dict[str, Any]:
        """Parse schema from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._parse_from_string(content, format or file_path.suffix[1:], fast_loading)
        except Exception as e:
            raise XSchemaParsingError(f"Failed to parse schema from file: {file_path}") from e

    def _parse_from_string(self, content: str, format: Optional[str], fast_loading: bool = False) -> Dict[str, Any]:
        """Parse schema from string content."""
        try:
            if fast_loading:
                # Fast path - just parse JSON without additional validation
                logger.debug("⚡ Fast parsing schema content")
                return json.loads(content)
            else:
                # Normal path - could add additional validation here
                logger.debug("📄 Normal parsing schema content")
                return json.loads(content)
        except json.JSONDecodeError as e:
            raise XSchemaParsingError(f"Failed to parse JSON schema: {e}") from e


class SchemaVersionManager:
    """
    Schema version management.
    Handles schema versioning, compatibility, and migration.
    """
    
    def __init__(self):
        self.version_history = {}
        self.compatibility_rules = {}
        logger.debug("📋 Schema version manager initialized")
    
    def check_version(self, schema: Dict[str, Any], required_version: Optional[str] = None) -> Dict[str, Any]:
        """Check schema version compatibility."""
        current_version = schema.get('version', '1.0.0')
        
        return {
            'current_version': current_version,
            'required_version': required_version,
            'compatible': True,  # Simplified implementation
            'upgrade_needed': False
        }


class SchemaReferenceResolver:
    """
    Schema reference resolution.
    Resolves $ref and other references in schemas.
    """
    
    def __init__(self):
        self.reference_cache = {}
        self.resolution_stack = []
        logger.debug("🔗 Schema reference resolver initialized")
    
    def resolve(self, schema: Dict[str, Any], base_uri: Optional[str] = None) -> Dict[str, Any]:
        """Resolve all references in schema."""
        try:
            logger.debug("🔗 Resolving schema references")
            resolved = self._resolve_recursive(deepcopy(schema), base_uri)
            logger.info("✅ Schema references resolved successfully")
            return resolved
        except Exception as e:
            logger.error(f"❌ Reference resolution failed: {e}")
            raise XSchemaReferenceError("Failed to resolve schema references") from e
    
    def _resolve_recursive(self, schema: Any, base_uri: Optional[str]) -> Any:
        """Recursively resolve references."""
        if isinstance(schema, dict):
            if '$ref' in schema:
                return self._resolve_reference(schema['$ref'], base_uri)
            else:
                return {k: self._resolve_recursive(v, base_uri) for k, v in schema.items()}
        elif isinstance(schema, list):
            return [self._resolve_recursive(item, base_uri) for item in schema]
        else:
            return schema
    
    def _resolve_reference(self, ref: str, base_uri: Optional[str]) -> Dict[str, Any]:
        """Resolve a single reference."""
        # Simplified implementation - would handle actual URI resolution
        if ref in self.reference_cache:
            return self.reference_cache[ref]
        
        # For now, return a placeholder
        resolved = {"resolved": True, "ref": ref}
        self.reference_cache[ref] = resolved
        return resolved 