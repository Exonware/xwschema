#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/contracts.py

XWSchema Interfaces and Contracts

This module defines all interfaces for the xwschema library following
GUIDELINES_DEV.md standards. All interfaces use 'I' prefix.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Union
from pathlib import Path

# Import enums from defs
from .defs import SchemaFormat, ValidationMode, SchemaGenerationMode


# ==============================================================================
# CORE SCHEMA INTERFACE
# ==============================================================================

class ISchema(ABC):
    """
    Core interface for all XWSchema instances.
    
    This interface defines the fundamental operations that all XWSchema
    implementations must support. Follows GUIDELINES_DEV.md naming:
    ISchema (interface) → ASchema (abstract) → XWSchema (concrete).
    """
    
    @abstractmethod
    async def validate(self, data: Any) -> tuple[bool, list[str]]:
        """
        Validate data against this schema.
        
        Args:
            data: Data to validate (can be dict, list, or XWData instance)
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        pass
    
    @abstractmethod
    def to_native(self) -> dict[str, Any]:
        """Get native Python dict representation of schema."""
        pass
    
    @abstractmethod
    async def serialize(self, format: Union[str, SchemaFormat], **opts) -> Union[str, bytes]:
        """Serialize schema to specified format."""
        pass
    
    @abstractmethod
    async def save(self, path: Union[str, Path], format: Optional[Union[str, SchemaFormat]] = None, **opts) -> 'ISchema':
        """Save schema to file (returns self for chaining)."""
        pass
    
    @abstractmethod
    async def load(self, path: Union[str, Path], format: Optional[Union[str, SchemaFormat]] = None, **opts) -> 'ISchema':
        """Load schema from file (returns self for chaining)."""
        pass
    
    @abstractmethod
    def get_format(self) -> Optional[str]:
        """Get schema format information."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> dict[str, Any]:
        """Get schema metadata dictionary."""
        pass


# ==============================================================================
# SCHEMA ENGINE INTERFACE
# ==============================================================================

class ISchemaEngine(ABC):
    """
    Interface for schema processing engine.
    
    Orchestrates schema validation, generation, and format conversion.
    """
    
    @abstractmethod
    async def validate_data(self, data: Any, schema: dict[str, Any], mode: ValidationMode = ValidationMode.STRICT) -> tuple[bool, list[str]]:
        """Validate data against schema."""
        pass
    
    @abstractmethod
    async def generate_schema(self, data: Any, mode: SchemaGenerationMode = SchemaGenerationMode.INFER) -> dict[str, Any]:
        """Generate schema from data."""
        pass
    
    @abstractmethod
    async def convert_schema(self, schema: dict[str, Any], from_format: SchemaFormat, to_format: SchemaFormat) -> dict[str, Any]:
        """Convert schema between formats."""
        pass
    
    @abstractmethod
    async def load_schema(self, path: Path, format: Optional[SchemaFormat] = None) -> dict[str, Any]:
        """Load schema from file."""
        pass
    
    @abstractmethod
    async def save_schema(self, schema: dict[str, Any], path: Path, format: SchemaFormat) -> None:
        """Save schema to file."""
        pass


# ==============================================================================
# SCHEMA VALIDATOR INTERFACE
# ==============================================================================

class ISchemaValidator(ABC):
    """
    Interface for schema validation operations.
    
    Extends xwsystem.validation.contracts.ISchemaValidator for consistency.
    """
    
    @abstractmethod
    def validate_schema(self, data: Any, schema: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate data against schema.
        
        Args:
            data: Data to validate
            schema: Schema definition
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        pass
    
    @abstractmethod
    def create_schema(self, data: Any) -> dict[str, Any]:
        """
        Create schema from data.
        
        Args:
            data: Data to create schema from
            
        Returns:
            Schema definition
        """
        pass
    
    @abstractmethod
    def validate_type(self, data: Any, expected_type: str) -> bool:
        """Validate data type."""
        pass
    
    @abstractmethod
    def validate_range(self, data: Any, min_value: Any, max_value: Any) -> bool:
        """Validate data range."""
        pass
    
    @abstractmethod
    def validate_pattern(self, data: str, pattern: str) -> bool:
        """Validate string pattern."""
        pass


# ==============================================================================
# SCHEMA GENERATOR INTERFACE
# ==============================================================================

class ISchemaGenerator(ABC):
    """Interface for schema generation operations."""
    
    @abstractmethod
    async def generate_from_data(self, data: Any, mode: SchemaGenerationMode = SchemaGenerationMode.INFER) -> dict[str, Any]:
        """Generate schema from data."""
        pass
    
    @abstractmethod
    async def generate_from_xwdata(self, data: Any, mode: SchemaGenerationMode = SchemaGenerationMode.INFER) -> dict[str, Any]:
        """Generate schema from XWData instance."""
        pass
    
    @abstractmethod
    def infer_type(self, value: Any) -> str:
        """Infer JSON Schema type from Python value."""
        pass

