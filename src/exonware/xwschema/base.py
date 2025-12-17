#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/base.py

XWSchema Abstract Base Classes

This module defines abstract base classes that extend interfaces from contracts.py.
Following GUIDELINES_DEV.md: All abstract classes start with 'A' and extend 'I' interfaces.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Union
from pathlib import Path
from exonware.xwsystem import get_logger

from .contracts import (
    ISchema, ISchemaEngine, ISchemaValidator, ISchemaGenerator
)
from .defs import SchemaFormat, ValidationMode, SchemaGenerationMode
from .config import XWSchemaConfig

logger = get_logger(__name__)


# ==============================================================================
# ABSTRACT SCHEMA
# ==============================================================================

class ASchema(ISchema):
    """
    Abstract base class for schema implementations.
    
    Provides common functionality for XWSchema implementations.
    Extends ISchema interface.
    """
    
    def __init__(self, config: Optional[XWSchemaConfig] = None):
        """Initialize abstract schema."""
        self._config = config or XWSchemaConfig.default()
        self._engine: Optional[ISchemaEngine] = None
        self._metadata: dict[str, Any] = {}
        self._format: Optional[SchemaFormat] = None
        
        logger.debug("ASchema initialized")
    
    @property
    def config(self) -> XWSchemaConfig:
        """Get configuration."""
        return self._config
    
    @property
    def metadata(self) -> dict[str, Any]:
        """Get metadata dictionary."""
        return self._metadata
    
    def get_metadata(self) -> dict[str, Any]:
        """Get metadata dictionary."""
        return self._metadata
    
    def get_format(self) -> Optional[str]:
        """Get schema format information."""
        return self._format.name if self._format else None
    
    @abstractmethod
    def _ensure_engine(self) -> ISchemaEngine:
        """Ensure schema engine is initialized."""
        pass


# ==============================================================================
# ABSTRACT SCHEMA ENGINE
# ==============================================================================

class ASchemaEngine(ISchemaEngine):
    """
    Abstract base class for schema engine implementations.
    
    Provides common functionality for XWSchemaEngine.
    Extends ISchemaEngine interface.
    """
    
    def __init__(self, config: Optional[XWSchemaConfig] = None):
        """Initialize abstract schema engine."""
        self._config = config or XWSchemaConfig.default()
        logger.debug("ASchemaEngine initialized")

