#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/base.py
XWSchema Abstract Base Classes
This module defines abstract base classes that extend interfaces from contracts.py.
Following GUIDELINES_DEV.md: All abstract classes start with 'A' and extend 'I' interfaces.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.14
Generation Date: 09-Nov-2025
"""

from abc import ABC, abstractmethod
from typing import Any
from pathlib import Path
from datetime import datetime
# Fully reuse xwsystem for logging
from exonware.xwsystem import get_logger
from exonware.xwsystem.shared import XWObject
# Reuse xwdata: _data (XWData) is the engine; do not re-implement IData methods
from exonware.xwdata import XWData
from .contracts import (
    ISchema, ISchemaEngine, ISchemaGenerator
)
from .defs import SchemaFormat, ValidationMode, SchemaGenerationMode
from .config import XWSchemaConfig
logger = get_logger(__name__)
# ==============================================================================
# ABSTRACT SCHEMA
# ==============================================================================


class ASchema(XWObject, ISchema):
    """
    Abstract base class for schema implementations.
    Provides common functionality for XWSchema implementations.
    Extends XWObject and ISchema interface.
    """

    def __init__(self, config: XWSchemaConfig | None = None, object_id: str | None = None):
        """Initialize abstract schema."""
        super().__init__(object_id=object_id)
        now = datetime.now()
        self._created_at = now
        self._updated_at = now
        self._config = config or XWSchemaConfig.default()
        self._engine: ISchemaEngine | None = None
        self._metadata: dict[str, Any] = {}
        self._format: SchemaFormat | None = None
        self._data: XWData | None = None
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
        """Get metadata dictionary (delegate to _data when set)."""
        if self._data is not None:
            return self._data.get_metadata()
        return self._metadata

    def get_format(self) -> str | None:
        """Get schema format information (delegate to _data when set)."""
        if self._data is not None:
            return self._data.get_format()
        return self._format.name if self._format else None

    def to_native(self) -> dict[str, Any]:
        """Get native Python dict (delegate to _data when set; do not re-implement)."""
        if self._data is not None:
            return self._data.to_native()
        return {}
    # IData delegation: async get/set/delete/exists/serialize/save/merge/transform

    async def get(self, path: str, default: Any = None) -> Any:
        if self._data is not None:
            return await self._data.get(path, default)
        return default

    async def set(self, path: str, value: Any) -> ISchema:
        if self._data is not None:
            self._data = await self._data.set(path, value)
        return self

    async def delete(self, path: str) -> ISchema:
        if self._data is not None:
            self._data = await self._data.delete(path)
        return self

    async def exists(self, path: str) -> bool:
        if self._data is not None:
            return await self._data.exists(path)
        return False

    async def serialize(self, format: str | Any, **opts) -> str | bytes:
        if self._data is not None:
            return await self._data.serialize(format, **opts)
        raise RuntimeError("ASchema.serialize requires _data (XWData) to be set")

    async def save(self, path: str | Path, format: str | None = None, **opts) -> ISchema:
        if self._data is not None:
            await self._data.save(path, format=format, **opts)
        return self

    async def merge(self, other: Any, strategy: str = 'deep') -> ISchema:
        if self._data is not None and other is not None and hasattr(other, '_data'):
            await self._data.merge(other._data, strategy=strategy)
        return self

    async def transform(self, transformer: Any) -> ISchema:
        if self._data is not None:
            await self._data.transform(transformer)
        return self

    def to_format(self, format: str | Any, **opts) -> str | bytes:
        """Synchronously serialize to format (delegate to _data)."""
        if self._data is not None:
            return self._data.to_format(format, **opts)
        raise RuntimeError("ASchema.to_format requires _data (XWData) to be set")

    def to_file(self, path: str | Path, format: str | None = None, **opts) -> ISchema:
        """Synchronously save to file (delegate to _data)."""
        if self._data is not None:
            self._data.to_file(path, format=format, **opts)
        return self
    @abstractmethod

    def _ensure_engine(self) -> ISchemaEngine:
        """Ensure schema engine is initialized."""
        pass
    # ============================================================================
    # XWObject Implementation (required abstract methods)
    # ============================================================================
    @property

    def created_at(self) -> datetime:
        """Get the creation timestamp."""
        return self._created_at
    @property

    def updated_at(self) -> datetime:
        """Get the last update timestamp."""
        return self._updated_at

    def to_dict(self) -> dict[str, Any]:
        """
        Export schema as dictionary.
        Includes XWObject fields (id, uid, created_at, updated_at, title, description)
        and schema-specific data.
        """
        result = {
            "id": self.id,
            "uid": self.uid,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "format": self._format.name if self._format else None,
        }
        if self.title:
            result["title"] = self.title
        if self.description:
            result["description"] = self.description
        if self._metadata:
            result["metadata"] = self._metadata
        return result

    def save_metadata(self, *args, **kwargs) -> None:
        """
        Save schema metadata to storage.
        This saves the schema object metadata (id, uid, timestamps, etc.).
        For saving schema definition to file, use async save(path, format).
        """
        # Update timestamp before saving
        self._updated_at = datetime.now()
        # Schema metadata persistence would be implemented here
        logger.debug(f"Saving schema metadata: {self.uid}")

    def load(self, *args, **kwargs) -> None:
        """
        Load schema metadata from storage.
        This loads the schema object metadata.
        For loading schema definition from file, use async load(path).
        """
        # Schema metadata loading would be implemented here
        logger.debug(f"Loading schema metadata: {self.uid}")
# ==============================================================================
# ABSTRACT SCHEMA ENGINE
# ==============================================================================


class ASchemaEngine(ISchemaEngine):
    """
    Abstract base class for schema engine implementations.
    Provides common functionality for XWSchemaEngine.
    Extends ISchemaEngine interface.
    """

    def __init__(self, config: XWSchemaConfig | None = None):
        """Initialize abstract schema engine."""
        self._config = config or XWSchemaConfig.default()
        logger.debug("ASchemaEngine initialized")
