#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/formats/schema/wsdl_schema.py

WSDL Schema Serializer

Extends xwsystem.io.serialization for Web Services Description Language (WSDL) support.
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


class WsdlSchemaSerializer(ASchemaSerialization):
    """
    WSDL schema serializer - reuses XmlSerializer.
    
    WSDL is XML-based, so we delegate to XmlSerializer and add WSDL validation.
    """
    
    def __init__(self):
        """Initialize WSDL schema serializer."""
        super().__init__()
        # Reuse XML serializer
        self._xml_serializer = XmlSerializer()
    
    # ========================================================================
    # CODEC METADATA
    # ========================================================================
    
    @property
    def codec_id(self) -> str:
        return "wsdl_schema"
    
    @property
    def media_types(self) -> list[str]:
        return ["application/wsdl+xml", "application/xml", "text/xml"]
    
    @property
    def file_extensions(self) -> list[str]:
        return [".wsdl"]
    
    @property
    def format_name(self) -> str:
        return "WSDL"
    
    @property
    def mime_type(self) -> str:
        return "application/wsdl+xml"
    
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
        return ["wsdl", "WSDL"]
    
    # ========================================================================
    # ASchemaSerialization IMPLEMENTATION
    # ========================================================================
    
    @property
    def schema_format_name(self) -> str:
        """Get schema format name for type/property mapping."""
        return "wsdl"
    
    @property
    def reference_keywords(self) -> list[str]:
        """WSDL uses import, include, and type for references."""
        return ['import', 'include', 'type']  # WSDL uses imports and types
    
    @property
    def definitions_keywords(self) -> list[str]:
        """WSDL uses types, message, portType, binding, service for definitions."""
        return ['types', 'message', 'portType', 'binding', 'service']  # WSDL structure
    
    @property
    def properties_keyword(self) -> str:
        """WSDL uses 'element' or 'part' for properties."""
        return 'element'  # WSDL uses elements, not properties
    
    @property
    def merge_keywords(self) -> dict[str, str]:
        """WSDL doesn't have merge keywords - uses imports and extensions."""
        return {}  # WSDL uses imports/extensions, not allOf/anyOf
    
    def normalize_schema(self, schema: Any) -> dict[str, Any]:
        """Normalize WSDL to internal representation."""
        if isinstance(schema, dict):
            return schema.copy()
        elif isinstance(schema, str):
            # XML string - convert to dict representation
            return {"xml_content": schema, "type": "wsdl"}
        else:
            raise SerializationError(f"Cannot normalize {type(schema).__name__} as WSDL")
    
    def denormalize_schema(self, normalized: dict[str, Any]) -> Any:
        """Convert normalized schema back to WSDL format."""
        if "xml_content" in normalized:
            return normalized["xml_content"]
        return normalized.copy()
    
    # ========================================================================
    # CORE SERIALIZATION (Delegate to XmlSerializer)
    # ========================================================================
    
    def encode(self, value: Any, *, options: Optional[EncodeOptions] = None) -> Union[bytes, str]:
        """
        Encode WSDL schema to string.
        
        Reuses XmlSerializer for encoding.
        """
        # Validate it's a valid WSDL structure
        if isinstance(value, (dict, str)):
            self._validate_wsdl_schema(value)
        
        # Reuse XML serializer
        return self._xml_serializer.encode(value, options=options)
    
    def decode(self, repr: Union[bytes, str], *, options: Optional[DecodeOptions] = None) -> Any:
        """
        Decode WSDL schema from string.
        
        Reuses XmlSerializer for decoding.
        """
        # Reuse XML serializer
        schema = self._xml_serializer.decode(repr, options=options)
        
        # Validate it's a valid WSDL
        if isinstance(schema, (dict, str)):
            self._validate_wsdl_schema(schema)
        
        return schema
    
    # ========================================================================
    # WSDL VALIDATION
    # ========================================================================
    
    def _validate_wsdl_schema(self, schema: Any) -> None:
        """
        Basic validation of WSDL structure.
        
        Full WSDL parser can be added later using lxml or xml.etree.
        """
        if isinstance(schema, str):
            # Check for WSDL namespace
            if 'http://schemas.xmlsoap.org/wsdl/' not in schema and 'wsdl:definitions' not in schema:
                logger.warning("WSDL schema may be invalid - no WSDL namespace found")
        elif isinstance(schema, dict):
            # Check for definitions element
            if 'definitions' not in str(schema).lower():
                logger.warning("WSDL schema may be invalid - no definitions element found")

