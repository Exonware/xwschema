#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/registry/enhanced_registry.py
Enhanced Schema Registry Manager (Optional BaaS Feature)
Enhances schema registry with BaaS-specific features like discovery and versioning.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.12
Generation Date: 26-Jan-2026
NOTE: This is an OPTIONAL module for BaaS platform integration.
"""

from typing import Any
from pathlib import Path
from exonware.xwsystem import get_logger
from ...errors import XWSchemaError
logger = get_logger(__name__)


class SchemaRegistryManager:
    """
    Enhanced schema registry manager.
    Provides BaaS-specific features:
    - Schema discovery from multiple sources
    - Schema version tracking
    - Dependency resolution
    - Performance caching
    This is an optional BaaS feature.
    NOTE: This is a simplified in-memory implementation.
    For production use, extend this to integrate with actual schema registries.
    """

    def __init__(self):
        """Initialize enhanced registry manager."""
        self._schemas: dict[str, dict[str, Any]] = {}  # name -> schema dict
        self._versions: dict[str, list[str]] = {}  # name -> [versions]
        self._cache: dict[str, Any] = {}
        logger.debug("SchemaRegistryManager initialized")

    async def register_schema(
        self,
        name: str,
        schema: dict[str, Any],
        version: str | None = None,
        **opts
    ) -> None:
        """
        Register schema with version tracking.
        Args:
            name: Schema name
            schema: Schema definition
            version: Optional version identifier
            **opts: Additional registration options
        """
        # Store schema
        cache_key = f"{name}:{version}" if version else name
        self._schemas[cache_key] = schema
        self._cache[cache_key] = schema
        # Track version
        if version:
            if name not in self._versions:
                self._versions[name] = []
            if version not in self._versions[name]:
                self._versions[name].append(version)
                self._versions[name].sort()
        logger.debug(f"Schema registered: {cache_key}")

    async def get_schema(
        self,
        name: str,
        version: str | None = None,
        **opts
    ) -> dict[str, Any]:
        """
        Get schema with caching.
        Args:
            name: Schema name
            version: Optional version identifier
            **opts: Additional options
        Returns:
            Schema definition
        """
        # Check cache first
        cache_key = f"{name}:{version}" if version else name
        if cache_key in self._cache:
            logger.debug(f"Schema cache hit: {cache_key}")
            return self._cache[cache_key]
        # Get from storage
        if cache_key in self._schemas:
            schema = self._schemas[cache_key]
            self._cache[cache_key] = schema
            return schema
        # Try latest version if no version specified
        if not version and name in self._versions:
            versions = self._versions[name]
            if versions:
                latest_version = versions[-1]
                cache_key = f"{name}:{latest_version}"
                if cache_key in self._schemas:
                    schema = self._schemas[cache_key]
                    self._cache[cache_key] = schema
                    return schema
        raise XWSchemaError(f"Schema not found: {cache_key}")

    async def list_schemas(self) -> list[str]:
        """
        List all registered schema names.
        Returns:
            List of schema names
        """
        return list(set(self._versions.keys()))
__all__ = ['SchemaRegistryManager']
