#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/formats/schema/xsd_schema.py

XSD Schema Serializer

Extends xwsystem.io.serialization for XML Schema Definition (XSD) support.
Reuses XML serializer from xwsystem.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from typing import Any, Optional, Union

# Reuse xwsystem XML serializer
from exonware.xwsystem.io.serialization.formats.text.xml import XmlSerializer
from exonware.xwsystem.io.serialization.contracts import EncodeOptions, DecodeOptions
from exonware.xwsystem.io.defs import CodecCapability
from exonware.xwsystem.io.serialization.errors import SerializationError
from exonware.xwsystem import get_logger
from ..base import ASchemaSerialization

logger = get_logger(__name__)


class XsdSchemaSerializer(ASchemaSerialization):
    """
    XSD schema serializer - reuses XmlSerializer.
    
    XSD is XML-based, so we delegate to XmlSerializer and add XSD validation.
    """
    
    def __init__(self):
        """Initialize XSD schema serializer."""
        super().__init__()
        # Reuse XML serializer
        self._xml_serializer = XmlSerializer()
    
    # ========================================================================
    # CODEC METADATA
    # ========================================================================
    
    @property
    def codec_id(self) -> str:
        return "xsd_schema"
    
    @property
    def media_types(self) -> list[str]:
        return ["application/xml", "text/xml", "application/xsd+xml"]
    
    @property
    def file_extensions(self) -> list[str]:
        return [".xsd"]
    
    @property
    def format_name(self) -> str:
        return "XSD"
    
    @property
    def mime_type(self) -> str:
        return "application/xsd+xml"
    
    @property
    def is_binary_format(self) -> bool:
        return False
    
    @property
    def supports_streaming(self) -> bool:
        return False
    
    @property
    def capabilities(self) -> CodecCapability:
        return CodecCapability.BIDIRECTIONAL
    
    @property
    def aliases(self) -> list[str]:
        return ["xsd", "xml_schema", "XSD"]
    
    # ========================================================================
    # ASchemaSerialization IMPLEMENTATION
    # ========================================================================
    
    @property
    def schema_format_name(self) -> str:
        """Get schema format name for type/property mapping."""
        return "xsd"
    
    @property
    def reference_keywords(self) -> list[str]:
        """XSD uses ref, type, and href attributes for references."""
        return ['ref', 'type', '@href']  # XSD uses attributes, not JSON-style keys
    
    @property
    def definitions_keywords(self) -> list[str]:
        """XSD uses complexType, simpleType, element, and group for definitions."""
        return ['complexType', 'simpleType', 'element', 'group']  # XSD structure
    
    @property
    def properties_keyword(self) -> str:
        """XSD uses 'element' or 'sequence' for properties."""
        return 'element'  # XSD uses elements, not properties
    
    @property
    def merge_keywords(self) -> dict[str, str]:
        """XSD uses extension, restriction, and union for composition."""
        return {
            'allOf': 'extension',  # XSD extension is similar to allOf
            'anyOf': 'choice',      # XSD choice is similar to anyOf
            'oneOf': 'union'        # XSD union is similar to oneOf
        }
    
    def normalize_schema(self, schema: Any) -> dict[str, Any]:
        """Normalize XSD to internal representation."""
        if isinstance(schema, dict):
            return schema.copy()
        elif isinstance(schema, str):
            # XML string - convert to dict representation
            # For now, return as dict with xml_content key
            return {"xml_content": schema, "type": "xsd"}
        else:
            raise SerializationError(f"Cannot normalize {type(schema).__name__} as XSD")
    
    def denormalize_schema(self, normalized: dict[str, Any]) -> Any:
        """Convert normalized schema back to XSD format."""
        if "xml_content" in normalized:
            return normalized["xml_content"]
        return normalized.copy()
    
    # ========================================================================
    # CORE SERIALIZATION (Delegate to XmlSerializer)
    # ========================================================================
    
    def encode(self, value: Any, *, options: Optional[EncodeOptions] = None) -> Union[bytes, str]:
        """
        Encode XSD schema to string.
        
        Reuses XmlSerializer for encoding.
        """
        # Validate it's a valid XSD structure
        if isinstance(value, (dict, str)):
            self._validate_xsd_schema(value)
        
        # Reuse XML serializer
        return self._xml_serializer.encode(value, options=options)
    
    def decode(self, repr: Union[bytes, str], *, options: Optional[DecodeOptions] = None) -> Any:
        """
        Decode XSD schema from string.
        
        Reuses XmlSerializer for decoding.
        """
        # Reuse XML serializer
        schema = self._xml_serializer.decode(repr, options=options)
        
        # Validate it's a valid XSD
        if isinstance(schema, (dict, str)):
            self._validate_xsd_schema(schema)
        
        return schema
    
    # ========================================================================
    # XSD VALIDATION
    # ========================================================================
    
    def _validate_xsd_schema(self, schema: Any) -> None:
        """
        Basic validation of XSD structure.
        
        Full XSD parser can be added later using lxml or xml.etree.
        """
        if isinstance(schema, str):
            # Check for XSD namespace
            if 'http://www.w3.org/2001/XMLSchema' not in schema and 'xs:schema' not in schema and 'xsd:schema' not in schema:
                logger.warning("XSD schema may be invalid - no XSD namespace found")
        elif isinstance(schema, dict):
            # Check for schema element
            if 'schema' not in str(schema).lower():
                logger.warning("XSD schema may be invalid - no schema element found")

