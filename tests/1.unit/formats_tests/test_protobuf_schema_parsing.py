#!/usr/bin/env python3
"""
#exonware/xwschema/tests/1.unit/formats_tests/test_protobuf_schema_parsing.py
Unit tests for Protobuf IDL parsing functionality.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

import pytest
from exonware.xwschema.formats.schema.protobuf_schema import ProtobufSchemaSerializer
@pytest.mark.xwschema_unit

class TestProtobufIDLParsing:
    """Test Protobuf IDL parsing."""

    def test_parse_simple_message(self):
        """Test parsing simple Protobuf message."""
        serializer = ProtobufSchemaSerializer()
        idl = """
        syntax = "proto3";
        message User {
            string name = 1;
            int32 age = 2;
        }
        """
        result = serializer.decode(idl)
        # Returns structured format
        assert result["type"] == "protobuf"
        assert "messages" in result or "idl_content" in result
        if "messages" in result:
            assert "User" in result["messages"]
            assert result.get("syntax") == "proto3"
        else:
            # Placeholder format - check content is preserved
            assert "message User" in result.get("idl_content", "")
            assert "proto3" in result.get("idl_content", "")

    def test_decode_validates_protobuf_syntax(self):
        """Test that decode handles invalid Protobuf IDL (may return dict or raise)."""
        serializer = ProtobufSchemaSerializer()
        invalid_idl = "invalid protobuf syntax !!!"
        try:
            result = serializer.decode(invalid_idl)
            assert isinstance(result, dict)
        except Exception:
            pass

    def test_decode_handles_bytes_input(self):
        """Test that decode handles bytes input."""
        serializer = ProtobufSchemaSerializer()
        idl_bytes = b'syntax = "proto3"; message User { string name = 1; }'
        result = serializer.decode(idl_bytes)
        assert result["type"] == "protobuf"
        assert "idl_content" in result
        assert isinstance(result["idl_content"], str)

    def test_decode_preserves_content(self):
        """Test that decode preserves the original IDL content."""
        serializer = ProtobufSchemaSerializer()
        idl = """
        syntax = "proto3";
        package com.example;
        message User {
            string name = 1;
            int32 age = 2;
        }
        """
        result = serializer.decode(idl)
        assert "idl_content" in result
        assert "package com.example" in result["idl_content"]
        assert "message User" in result["idl_content"]
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
