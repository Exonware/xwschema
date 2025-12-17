#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/registry/base.py

Schema Registry Base Classes

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .schema_registry import SchemaInfo
from .defs import CompatibilityLevel


class ASchemaRegistry(ABC):
    """Abstract base class for schema registries."""
    
    @abstractmethod
    async def register_schema(self, subject: str, schema: str, schema_type: str = "AVRO") -> SchemaInfo:
        """Register a new schema version."""
        pass
    
    @abstractmethod
    async def get_schema(self, schema_id: int) -> SchemaInfo:
        """Get schema by ID."""
        pass
    
    @abstractmethod
    async def get_latest_schema(self, subject: str) -> SchemaInfo:
        """Get latest schema version for subject."""
        pass
    
    @abstractmethod
    async def get_schema_versions(self, subject: str) -> list[int]:
        """Get all versions for a subject."""
        pass
    
    @abstractmethod
    async def check_compatibility(self, subject: str, schema: str) -> bool:
        """Check if schema is compatible with latest version."""
        pass
    
    @abstractmethod
    async def set_compatibility(self, subject: str, level: CompatibilityLevel) -> None:
        """Set compatibility level for subject."""
        pass
