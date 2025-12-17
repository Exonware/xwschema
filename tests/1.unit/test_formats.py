#!/usr/bin/env python3
"""
Unit tests for schema format serializers.

Tests individual format serializers:
- JSON Schema
- Avro Schema
- XSD Schema
- OpenAPI Schema
- Protobuf Schema
- GraphQL Schema
- Swagger Schema
- WSDL Schema

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.1
Generation Date: 09-Nov-2025
"""

import pytest
from exonware.xwschema.formats.schema.json_schema import JsonSchemaSerializer
from exonware.xwschema.formats.schema.avro_schema import AvroSchemaSerializer
from exonware.xwschema.formats.schema.xsd_schema import XsdSchemaSerializer
from exonware.xwschema.formats.schema.openapi_schema import OpenApiSchemaSerializer
from exonware.xwschema.formats.schema.protobuf_schema import ProtobufSchemaSerializer
from exonware.xwschema.formats.schema.graphql_schema import GraphQLSchemaSerializer
from exonware.xwschema.formats.schema.swagger_schema import SwaggerSchemaSerializer
from exonware.xwschema.formats.schema.wsdl_schema import WsdlSchemaSerializer


@pytest.mark.xwschema_unit
class TestJsonSchemaSerializer:
    """Test JSON Schema serializer."""
    
    @pytest.fixture
    def serializer(self):
        """Create JSON Schema serializer."""
        return JsonSchemaSerializer()
    
    def test_schema_format_name(self, serializer):
        """Test schema_format_name property."""
        assert serializer.schema_format_name == 'json_schema'
    
    def test_reference_keywords(self, serializer):
        """Test reference_keywords property."""
        keywords = serializer.reference_keywords
        assert isinstance(keywords, list)
        assert '$ref' in keywords
    
    def test_definitions_keywords(self, serializer):
        """Test definitions_keywords property."""
        keywords = serializer.definitions_keywords
        assert isinstance(keywords, list)
        assert '$defs' in keywords or 'definitions' in keywords
    
    def test_properties_keyword(self, serializer):
        """Test properties_keyword property."""
        assert serializer.properties_keyword == 'properties'
    
    def test_merge_keywords(self, serializer):
        """Test merge_keywords property."""
        keywords = serializer.merge_keywords
        assert 'allOf' in keywords
        assert 'anyOf' in keywords
        assert 'oneOf' in keywords
    
    def test_normalize_schema_from_dict(self, serializer):
        """Test normalize_schema from dict."""
        schema = {'type': 'string'}
        normalized = serializer.normalize_schema(schema)
        assert normalized == schema
    
    def test_normalize_schema_from_string(self, serializer):
        """Test normalize_schema from string."""
        schema = 'string'
        normalized = serializer.normalize_schema(schema)
        assert normalized == {'type': 'string'}
    
    def test_denormalize_schema(self, serializer):
        """Test denormalize_schema."""
        normalized = {'type': 'string'}
        denormalized = serializer.denormalize_schema(normalized)
        assert denormalized == normalized
    
    def test_encode_decode_roundtrip(self, serializer):
        """Test encode/decode roundtrip."""
        schema = {'type': 'string', 'title': 'Test'}
        encoded = serializer.encode(schema)
        decoded = serializer.decode(encoded)
        assert decoded['type'] == 'string'
        assert decoded['title'] == 'Test'


@pytest.mark.xwschema_unit
class TestAvroSchemaSerializer:
    """Test Avro Schema serializer."""
    
    @pytest.fixture
    def serializer(self):
        """Create Avro Schema serializer."""
        return AvroSchemaSerializer()
    
    def test_schema_format_name(self, serializer):
        """Test schema_format_name property."""
        assert serializer.schema_format_name == 'avro'
    
    def test_reference_keywords(self, serializer):
        """Test reference_keywords property."""
        keywords = serializer.reference_keywords
        assert isinstance(keywords, list)
        # Avro uses named types, not $ref
    
    def test_properties_keyword(self, serializer):
        """Test properties_keyword property."""
        assert serializer.properties_keyword == 'fields'
    
    def test_normalize_schema(self, serializer):
        """Test normalize_schema."""
        schema = {'type': 'string'}
        normalized = serializer.normalize_schema(schema)
        assert normalized == schema
    
    def test_denormalize_schema(self, serializer):
        """Test denormalize_schema."""
        normalized = {'type': 'string'}
        denormalized = serializer.denormalize_schema(normalized)
        assert denormalized == normalized


@pytest.mark.xwschema_unit
class TestXsdSchemaSerializer:
    """Test XSD Schema serializer."""
    
    @pytest.fixture
    def serializer(self):
        """Create XSD Schema serializer."""
        return XsdSchemaSerializer()
    
    def test_schema_format_name(self, serializer):
        """Test schema_format_name property."""
        assert serializer.schema_format_name == 'xsd'
    
    def test_reference_keywords(self, serializer):
        """Test reference_keywords property."""
        keywords = serializer.reference_keywords
        assert isinstance(keywords, list)
        # XSD uses ref, type, @href
    
    def test_properties_keyword(self, serializer):
        """Test properties_keyword property."""
        assert serializer.properties_keyword == 'element'
    
    def test_normalize_schema_from_dict(self, serializer):
        """Test normalize_schema from dict."""
        schema = {'type': 'xsd'}
        normalized = serializer.normalize_schema(schema)
        assert normalized == schema
    
    def test_normalize_schema_from_string(self, serializer):
        """Test normalize_schema from XML string."""
        schema = '<xs:schema>...</xs:schema>'
        normalized = serializer.normalize_schema(schema)
        assert 'xml_content' in normalized or 'type' in normalized


@pytest.mark.xwschema_unit
class TestOpenApiSchemaSerializer:
    """Test OpenAPI Schema serializer."""
    
    @pytest.fixture
    def serializer(self):
        """Create OpenAPI Schema serializer."""
        return OpenApiSchemaSerializer()
    
    def test_schema_format_name(self, serializer):
        """Test schema_format_name property."""
        assert serializer.schema_format_name == 'openapi'
    
    def test_reference_keywords(self, serializer):
        """Test reference_keywords property."""
        keywords = serializer.reference_keywords
        assert '$ref' in keywords
    
    def test_definitions_keywords(self, serializer):
        """Test definitions_keywords property."""
        keywords = serializer.definitions_keywords
        assert 'components' in keywords or 'schemas' in keywords
    
    def test_properties_keyword(self, serializer):
        """Test properties_keyword property."""
        assert serializer.properties_keyword == 'properties'


@pytest.mark.xwschema_unit
class TestProtobufSchemaSerializer:
    """Test Protobuf Schema serializer."""
    
    @pytest.fixture
    def serializer(self):
        """Create Protobuf Schema serializer."""
        return ProtobufSchemaSerializer()
    
    def test_schema_format_name(self, serializer):
        """Test schema_format_name property."""
        assert serializer.schema_format_name == 'protobuf_schema'
    
    def test_reference_keywords(self, serializer):
        """Test reference_keywords property."""
        keywords = serializer.reference_keywords
        assert 'import' in keywords or 'package' in keywords
    
    def test_properties_keyword(self, serializer):
        """Test properties_keyword property."""
        assert serializer.properties_keyword == 'field'
    
    def test_normalize_schema_from_string(self, serializer):
        """Test normalize_schema from Protobuf IDL string."""
        schema = 'message Test { string name = 1; }'
        normalized = serializer.normalize_schema(schema)
        assert 'idl_content' in normalized or 'type' in normalized


@pytest.mark.xwschema_unit
class TestGraphQLSchemaSerializer:
    """Test GraphQL Schema serializer."""
    
    @pytest.fixture
    def serializer(self):
        """Create GraphQL Schema serializer."""
        return GraphQLSchemaSerializer()
    
    def test_schema_format_name(self, serializer):
        """Test schema_format_name property."""
        assert serializer.schema_format_name == 'graphql_schema'
    
    def test_reference_keywords(self, serializer):
        """Test reference_keywords property."""
        keywords = serializer.reference_keywords
        assert 'type' in keywords or 'implements' in keywords
    
    def test_properties_keyword(self, serializer):
        """Test properties_keyword property."""
        assert serializer.properties_keyword == 'field'
    
    def test_normalize_schema_from_string(self, serializer):
        """Test normalize_schema from GraphQL SDL string."""
        schema = 'type User { name: String }'
        normalized = serializer.normalize_schema(schema)
        assert 'sdl_content' in normalized or 'type' in normalized


@pytest.mark.xwschema_unit
class TestSwaggerSchemaSerializer:
    """Test Swagger Schema serializer."""
    
    @pytest.fixture
    def serializer(self):
        """Create Swagger Schema serializer."""
        return SwaggerSchemaSerializer()
    
    def test_schema_format_name(self, serializer):
        """Test schema_format_name property."""
        assert serializer.schema_format_name == 'swagger'
    
    def test_reference_keywords(self, serializer):
        """Test reference_keywords property."""
        keywords = serializer.reference_keywords
        assert '$ref' in keywords
    
    def test_definitions_keywords(self, serializer):
        """Test definitions_keywords property."""
        keywords = serializer.definitions_keywords
        assert 'definitions' in keywords


@pytest.mark.xwschema_unit
class TestWsdlSchemaSerializer:
    """Test WSDL Schema serializer."""
    
    @pytest.fixture
    def serializer(self):
        """Create WSDL Schema serializer."""
        return WsdlSchemaSerializer()
    
    def test_schema_format_name(self, serializer):
        """Test schema_format_name property."""
        assert serializer.schema_format_name == 'wsdl'
    
    def test_reference_keywords(self, serializer):
        """Test reference_keywords property."""
        keywords = serializer.reference_keywords
        assert 'import' in keywords or 'include' in keywords
    
    def test_properties_keyword(self, serializer):
        """Test properties_keyword property."""
        assert serializer.properties_keyword == 'element'


@pytest.mark.xwschema_unit
class TestFormatCommonFeatures:
    """Test common features across all format serializers."""
    
    @pytest.fixture
    def serializers(self):
        """Create all serializers."""
        return {
            'json': JsonSchemaSerializer(),
            'avro': AvroSchemaSerializer(),
            'xsd': XsdSchemaSerializer(),
            'openapi': OpenApiSchemaSerializer(),
            'protobuf': ProtobufSchemaSerializer(),
            'graphql': GraphQLSchemaSerializer(),
            'swagger': SwaggerSchemaSerializer(),
            'wsdl': WsdlSchemaSerializer(),
        }
    
    def test_all_have_schema_format_name(self, serializers):
        """Test all serializers have schema_format_name."""
        for name, serializer in serializers.items():
            assert hasattr(serializer, 'schema_format_name')
            assert isinstance(serializer.schema_format_name, str)
    
    def test_all_have_reference_keywords(self, serializers):
        """Test all serializers have reference_keywords."""
        for name, serializer in serializers.items():
            assert hasattr(serializer, 'reference_keywords')
            assert isinstance(serializer.reference_keywords, list)
    
    def test_all_have_properties_keyword(self, serializers):
        """Test all serializers have properties_keyword."""
        for name, serializer in serializers.items():
            assert hasattr(serializer, 'properties_keyword')
            assert isinstance(serializer.properties_keyword, str)
    
    def test_all_have_normalize_denormalize(self, serializers):
        """Test all serializers have normalize/denormalize methods."""
        for name, serializer in serializers.items():
            assert hasattr(serializer, 'normalize_schema')
            assert hasattr(serializer, 'denormalize_schema')
    
    def test_all_support_type_mapping(self, serializers):
        """Test all serializers support type mapping."""
        for name, serializer in serializers.items():
            assert hasattr(serializer, 'map_type_to')
            assert hasattr(serializer, 'map_type_from')
    
    def test_all_support_property_mapping(self, serializers):
        """Test all serializers support property mapping."""
        for name, serializer in serializers.items():
            assert hasattr(serializer, 'map_property_to')
    
    def test_all_support_format_conversion(self, serializers):
        """Test all serializers support format conversion."""
        for name, serializer in serializers.items():
            assert hasattr(serializer, 'convert_to_format')
    
    def test_all_support_schema_generation(self, serializers):
        """Test all serializers support schema generation."""
        for name, serializer in serializers.items():
            assert hasattr(serializer, 'generate_from_data')
    
    def test_all_support_reference_detection(self, serializers):
        """Test all serializers support reference detection."""
        for name, serializer in serializers.items():
            assert hasattr(serializer, 'detect_references')
    
    def test_all_support_schema_merging(self, serializers):
        """Test all serializers support schema merging."""
        for name, serializer in serializers.items():
            assert hasattr(serializer, 'merge_schemas')

