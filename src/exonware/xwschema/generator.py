#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/generator.py

XWSchema Generator Implementation

This module provides schema generation that reuses:
- XWData for efficient data structure analysis
- XWSystem utilities

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from typing import Any, Optional
from collections import Counter
from exonware.xwsystem import get_logger

# Reuse XWData for data analysis
try:
    from exonware.xwdata import XWData
except ImportError:
    XWData = None

from .contracts import ISchemaGenerator
from .errors import XWSchemaGenerationError
from .defs import SchemaGenerationMode
from .config import GenerationConfig

logger = get_logger(__name__)


class XWSchemaGenerator(ISchemaGenerator):
    """
    Schema generator implementation.
    
    Reuses XWData for efficient data structure analysis.
    """
    
    def __init__(self, config: Optional[GenerationConfig] = None):
        """Initialize generator."""
        self._config = config or GenerationConfig()
        logger.debug(f"XWSchemaGenerator initialized (mode: {config.mode if config else 'default'})")
    
    async def generate_from_data(self, data: Any, mode: SchemaGenerationMode = SchemaGenerationMode.INFER) -> dict[str, Any]:
        """
        Generate schema from data.
        
        Args:
            data: Data to generate schema from (can be dict, list, or XWData instance)
            mode: Generation mode
            
        Returns:
            Schema definition (JSON Schema format)
        """
        try:
            # Convert XWData to native if needed
            if XWData and isinstance(data, XWData):
                return await self.generate_from_xwdata(data, mode)
            else:
                return self._generate_from_native(data, mode)
        except Exception as e:
            raise XWSchemaGenerationError(f"Schema generation failed: {e}") from e
    
    async def generate_from_xwdata(self, data: XWData, mode: SchemaGenerationMode = SchemaGenerationMode.INFER) -> dict[str, Any]:
        """
        Generate schema from XWData instance.
        
        Reuses XWData's efficient navigation for structure analysis.
        """
        native_data = data.to_native()
        return self._generate_from_native(native_data, mode)
    
    def _generate_from_native(self, data: Any, mode: SchemaGenerationMode) -> dict[str, Any]:
        """Generate schema from native Python data."""
        if mode == SchemaGenerationMode.MINIMAL:
            return self._generate_minimal(data)
        elif mode == SchemaGenerationMode.COMPREHENSIVE:
            return self._generate_comprehensive(data)
        else:  # INFER or STRICT
            return self._generate_infer(data)
    
    def _generate_minimal(self, data: Any) -> dict[str, Any]:
        """Generate minimal schema (types only)."""
        schema = {'type': self.infer_type(data)}
        
        if isinstance(data, dict):
            schema['properties'] = {k: self._generate_minimal(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)) and len(data) > 0:
            schema['items'] = self._generate_minimal(data[0])
        
        return schema
    
    def _generate_infer(self, data: Any) -> dict[str, Any]:
        """Generate inferred schema with basic constraints."""
        schema = {'type': self.infer_type(data)}
        
        if isinstance(data, dict):
            properties = {}
            required = []
            
            for key, value in data.items():
                if value is not None:
                    properties[key] = self._generate_infer(value)
                    if self._config.infer_required:
                        required.append(key)
            
            schema['properties'] = properties
            if required:
                schema['required'] = required
                
        elif isinstance(data, (list, tuple)):
            if len(data) > 0:
                # Analyze all items to find common schema
                item_schemas = [self._generate_infer(item) for item in data]
                schema['items'] = self._merge_item_schemas(item_schemas)
            else:
                schema['items'] = {}
            
            if self._config.infer_ranges:
                schema['minItems'] = len(data)
        
        elif isinstance(data, str):
            if self._config.infer_ranges:
                schema['minLength'] = len(data)
                schema['maxLength'] = len(data)
        
        elif isinstance(data, (int, float)):
            if self._config.infer_ranges:
                schema['minimum'] = data
                schema['maximum'] = data
        
        return schema
    
    def _generate_comprehensive(self, data: Any) -> dict[str, Any]:
        """Generate comprehensive schema with examples and descriptions."""
        schema = self._generate_infer(data)
        
        if self._config.include_examples:
            schema['example'] = data
        
        if isinstance(data, dict):
            # Add examples for each property
            if 'properties' in schema:
                for key, value in data.items():
                    if key in schema['properties']:
                        if self._config.include_examples:
                            schema['properties'][key]['example'] = value
        
        elif isinstance(data, (list, tuple)) and len(data) > 0:
            if self._config.include_examples:
                schema['items']['example'] = data[0]
        
        return schema
    
    def _merge_item_schemas(self, schemas: list[dict[str, Any]]) -> dict[str, Any]:
        """Merge multiple item schemas into a common schema."""
        if not schemas:
            return {}
        
        # Find common type
        types = [s.get('type') for s in schemas]
        common_type = types[0] if all(t == types[0] for t in types) else None
        
        if common_type:
            merged = {'type': common_type}
            # Merge constraints
            if common_type == 'string':
                lengths = [s.get('minLength', 0) for s in schemas if 'minLength' in s]
                if lengths:
                    merged['minLength'] = min(lengths)
                    merged['maxLength'] = max(lengths)
            elif common_type in ('number', 'integer'):
                values = [s.get('minimum', float('-inf')) for s in schemas if 'minimum' in s]
                if values:
                    merged['minimum'] = min(values)
                    merged['maximum'] = max(values)
            return merged
        
        # Use first schema as base if types differ
        return schemas[0]
    
    def infer_type(self, value: Any) -> str:
        """Infer JSON Schema type from Python value."""
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'number'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, (list, tuple)):
            return 'array'
        elif isinstance(value, dict):
            return 'object'
        else:
            return 'string'  # Default fallback

