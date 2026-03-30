#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/registry/discovery.py
Schema Discovery (Optional BaaS Feature)
Auto-discovers schemas from multiple sources.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.5
Generation Date: 26-Jan-2026
NOTE: This is an OPTIONAL module for BaaS platform integration.
"""

from typing import Any
from pathlib import Path
from exonware.xwsystem import get_logger
from ...errors import XWSchemaError
from ...defs import SchemaFormat
from ...engine import XWSchemaEngine
logger = get_logger(__name__)


class SchemaDiscovery:
    """
    Schema discovery for auto-discovering schemas.
    Auto-discovers schemas from multiple sources like file systems,
    storage backends, etc.
    This is an optional BaaS feature.
    """

    def __init__(self):
        """Initialize schema discovery."""
        self._engine = XWSchemaEngine()
        logger.debug("SchemaDiscovery initialized")

    async def discover_from_directory(
        self,
        directory: Path,
        recursive: bool = True,
        **opts
    ) -> list[dict[str, Any]]:
        """
        Discover schemas from directory.
        Args:
            directory: Directory path to scan
            recursive: Whether to scan recursively
            **opts: Additional discovery options
        Returns:
            List of discovered schemas with metadata
        """
        schemas = []
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return schemas
        pattern = "**/*" if recursive else "*"
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                # Try to detect schema format from extension
                format = self._detect_format_from_extension(file_path.suffix)
                if format:
                    try:
                        schema = await self._engine.load_schema(file_path, format=format)
                        schemas.append({
                            'name': file_path.stem,
                            'path': str(file_path),
                            'format': format,
                            'schema': schema
                        })
                        logger.debug(f"Discovered schema: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to load schema from {file_path}: {e}")
        return schemas

    def _detect_format_from_extension(self, extension: str) -> SchemaFormat | None:
        """Detect schema format from file extension."""
        ext_map = {
            '.json': SchemaFormat.JSON_SCHEMA,
            '.yaml': SchemaFormat.OPENAPI,
            '.yml': SchemaFormat.OPENAPI,
            '.graphql': SchemaFormat.GRAPHQL,
            '.gql': SchemaFormat.GRAPHQL,
            '.proto': SchemaFormat.PROTOBUF,
            '.avsc': SchemaFormat.AVRO,
            '.xsd': SchemaFormat.XSD,
            '.wsdl': SchemaFormat.WSDL,
        }
        return ext_map.get(extension.lower())
__all__ = ['SchemaDiscovery']
