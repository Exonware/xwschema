# XWSyntax Integration Guide

**Company:** eXonware.com  
**Author:** Eng. Muhammad AlShehri  
**Email:** connect@exonware.com  
**Version:** 0.0.1.1  
**Date:** December 2025

---

## Overview

This document describes the relationship between **xwsyntax** (Universal Grammar Engine) and **xwschema** (Schema Validation Library), and outlines collaboration opportunities for enhanced functionality and code reuse.

---

## Relationship Between XWSyntax and XWSchema

### XWSyntax: Universal Grammar Engine

**xwsyntax** is a comprehensive grammar engine that provides:
- **31+ grammar formats** (queries, data, programming languages, specialized)
- **Bidirectional parsing** (text → AST → text)
- **Automatic optimization** (xwnode-powered)
- **Binary format support** (BSON, MessagePack, CBOR, etc.)
- **IDE integration** (LSP, Monaco, tree-sitter)
- **High performance** (<1ms for common cases)

**Key Capabilities:**
- Parse and generate code/text for multiple formats
- Convert between formats via AST (Abstract Syntax Tree)
- Validate syntax correctness
- Provide grammar-aware editing features

### XWSchema: Schema Validation Library

**xwschema** is a schema validation and data structure definition library that provides:
- **Multi-format schema support** (JSON Schema, Avro, Protobuf, OpenAPI, GraphQL, XSD/WSDL)
- **Data validation** against schema definitions
- **Schema generation** from data
- **Schema format conversion** (roundtrip compatibility)
- **Structured error reporting** (node_path, issue_type, message)

**Key Capabilities:**
- Validate data structures against schema definitions
- Generate schemas from sample data
- Convert between different schema formats
- Provide detailed validation error reporting

---

## Why They Are Related

### 1. **Overlapping Format Support**

Both libraries deal with schema-related formats:

**xwsyntax supports:**
- Protobuf (`.proto`)
- Avro (`.avsc`, `.avro`)
- Thrift (`.thrift`)
- Parquet (`.parquet`)
- ORC (`.orc`)
- JSON, YAML, XML (data formats)
- GraphQL (query language)

**xwschema needs:**
- JSON Schema, Avro, Protobuf, OpenAPI, GraphQL, XSD/WSDL

**Overlap:** Avro, Protobuf, GraphQL, JSON, YAML, XML

### 2. **Complementary Responsibilities**

- **xwsyntax**: Handles **syntax** (parsing, generating, syntax validation)
- **xwschema**: Handles **semantics** (validation, constraints, type checking)

Together, they provide complete validation: **syntax + semantics**.

### 3. **Shared Architecture Foundation**

Both libraries:
- Use **xwnode** for optimized data structures
- Use **xwsystem** for serialization and utilities
- Follow similar architectural patterns
- Support multiple formats with unified APIs

---

## Collaboration Opportunities

### 1. **Schema File Parsing**

**Current State:**
- xwschema uses `AutoSerializer` for basic JSON/YAML I/O
- Schema format serializers need custom parsing logic
- Some formats (Protobuf, GraphQL) require IDL/SDL parsers

**Opportunity:**
- Use xwsyntax grammars to parse schema definition files
- Leverage existing grammar implementations
- Reduce code duplication

**Example:**
```python
# Instead of custom Protobuf parser in xwschema:
# Use xwsyntax's Protobuf grammar

from exonware.xwsyntax import BidirectionalGrammar
from exonware.xwschema import XWSchema

# Parse Protobuf schema using xwsyntax
proto_grammar = BidirectionalGrammar.load('protobuf')
proto_ast = proto_grammar.parse(proto_schema_text)

# Convert AST to xwschema format
schema_dict = convert_proto_ast_to_schema_dict(proto_ast)

# Use with xwschema
schema = XWSchema(schema_dict)
is_valid, errors = await schema.validate(data)
```

**Benefits:**
- ✅ No duplicate parsing logic
- ✅ Consistent parsing across formats
- ✅ Automatic grammar updates benefit both libraries
- ✅ Better error messages from grammar-aware parsing

---

### 2. **Schema Format Conversion**

**Current State:**
- xwschema has format conversion capabilities
- Conversion is done at the schema dictionary level
- Some conversions may lose information

**Opportunity:**
- Use xwsyntax's bidirectional capabilities for format conversion
- Parse schema A → AST → Generate schema B
- Preserve more information through AST representation

**Example:**
```python
# Convert JSON Schema to Protobuf using AST

from exonware.xwsyntax import BidirectionalGrammar

# Parse JSON Schema
json_schema_grammar = BidirectionalGrammar.load('json')
json_ast = json_schema_grammar.parse(json_schema_text)

# Transform AST (add Protobuf-specific annotations)
proto_ast = transform_ast_for_protobuf(json_ast)

# Generate Protobuf schema
proto_grammar = BidirectionalGrammar.load('protobuf')
proto_schema_text = proto_grammar.generate(proto_ast)
```

**Benefits:**
- ✅ More accurate format conversion
- ✅ Preserves metadata through AST
- ✅ Leverages xwsyntax's proven conversion logic
- ✅ Supports complex transformations

---

### 3. **Unified Validation (Syntax + Semantics)**

**Current State:**
- xwsyntax validates syntax correctness
- xwschema validates semantic correctness
- They operate independently

**Opportunity:**
- Combine syntax and semantic validation
- Provide unified error reporting
- Validate schema files before semantic validation

**Example:**
```python
from exonware.xwsyntax import XWSyntax
from exonware.xwschema import XWSchema

# Step 1: Syntax validation (xwsyntax)
syntax = XWSyntax()
try:
    ast = syntax.parse(schema_text, 'protobuf')
except SyntaxError as e:
    print(f"Syntax error: {e}")
    return

# Step 2: Semantic validation (xwschema)
schema = XWSchema.from_protobuf_ast(ast)
is_valid, errors = await schema.validate(data)

# Combined error reporting
if not is_valid:
    for error in errors:
        print(f"Semantic error at {error['node_path']}: {error['message']}")
```

**Benefits:**
- ✅ Catch syntax errors before semantic validation
- ✅ More comprehensive error reporting
- ✅ Better user experience
- ✅ Clearer error messages

---

### 4. **Schema Generation with Formatting**

**Current State:**
- xwschema generates schema dictionaries
- Formatting/serialization is handled separately
- May not preserve original formatting

**Opportunity:**
- Use xwsyntax to generate formatted schema files
- Preserve formatting preferences
- Support code generation with style options

**Example:**
```python
# Generate schema from data, then format using xwsyntax

from exonware.xwschema import XWSchema
from exonware.xwsyntax import BidirectionalGrammar

# Generate schema from data
schema = await XWSchema.from_data(sample_data)

# Convert to AST
schema_ast = schema.to_ast()

# Generate formatted Protobuf schema
proto_grammar = BidirectionalGrammar.load('protobuf')
proto_schema = proto_grammar.generate(
    schema_ast,
    options={'indent': 2, 'preserve_comments': True}
)
```

**Benefits:**
- ✅ Consistent formatting
- ✅ Preserve comments and metadata
- ✅ Support multiple output styles
- ✅ Better code generation

---

### 5. **IDE Integration**

**Current State:**
- xwsyntax provides LSP, Monaco, tree-sitter support
- xwschema has validation capabilities
- No integrated IDE experience for schema editing

**Opportunity:**
- Combine xwsyntax's IDE features with xwschema's validation
- Real-time syntax highlighting + semantic validation
- Autocomplete based on schema definitions
- Inline error reporting

**Example:**
```python
# IDE integration combining both libraries

from exonware.xwsyntax import MonacoExporter
from exonware.xwschema import XWSchema

# Generate Monaco language definition from schema
schema = XWSchema.load('schema.json')
monaco_lang = MonacoExporter.from_schema(schema)

# Provides:
# - Syntax highlighting for schema format
# - Autocomplete for schema properties
# - Real-time validation feedback
# - Error markers in editor
```

**Benefits:**
- ✅ Rich IDE experience for schema editing
- ✅ Real-time validation feedback
- ✅ Better developer productivity
- ✅ Reduced errors through autocomplete

---

## Implementation Roadmap

### Phase 1: Schema File Parsing (High Priority)

**Goal:** Use xwsyntax grammars to parse schema definition files

**Tasks:**
1. Add xwsyntax as optional dependency to xwschema
2. Create AST-to-schema-dict converters for each format:
   - Protobuf AST → Schema Dict
   - Avro AST → Schema Dict
   - GraphQL AST → Schema Dict
3. Update `XWSchemaEngine.load_schema()` to use xwsyntax when available
4. Add fallback to current parsing methods

**Benefits:**
- Immediate code reuse
- Better parsing accuracy
- Consistent error handling

---

### Phase 2: Schema Format Conversion via AST (Medium Priority)

**Goal:** Use AST for more accurate format conversion

**Tasks:**
1. Implement AST transformation utilities
2. Add format conversion methods that use AST
3. Preserve metadata through AST representation
4. Test roundtrip conversions

**Benefits:**
- More accurate conversions
- Better metadata preservation
- Support for complex transformations

---

### Phase 3: Unified Validation (Medium Priority)

**Goal:** Combine syntax and semantic validation

**Tasks:**
1. Add syntax validation step before semantic validation
2. Combine error reporting from both libraries
3. Create unified error format
4. Update validation API to include syntax errors

**Benefits:**
- Comprehensive validation
- Better error messages
- Improved user experience

---

### Phase 4: IDE Integration (Lower Priority)

**Goal:** Provide rich IDE experience for schema editing

**Tasks:**
1. Create Monaco language definitions from schemas
2. Integrate with LSP server
3. Add autocomplete based on schema definitions
4. Real-time validation in editor

**Benefits:**
- Enhanced developer experience
- Reduced errors
- Better productivity

---

## Integration Pattern

### Recommended Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Application                      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      XWSchema API                        │
│  (Schema validation, generation, conversion)              │
└─────────────────────────────────────────────────────────┘
         │                              │
         │                              │
         ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│  XWSyntax        │          │  XWSchema        │
│  (Parsing)       │          │  (Validation)     │
│                  │          │                  │
│  - Parse schema  │◄────────►│  - Validate data │
│    files         │          │  - Generate      │
│  - Generate AST  │          │    schemas       │
│  - Format        │          │  - Convert        │
│    conversion    │          │    formats       │
└──────────────────┘          └──────────────────┘
         │                              │
         │                              │
         └──────────────┬───────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │     XWNode        │
              │  (Data Structures)│
              └──────────────────┘
```

### Code Example: Integrated Usage

```python
"""
Example: Using xwsyntax and xwschema together
"""

from exonware.xwsyntax import BidirectionalGrammar
from exonware.xwschema import XWSchema

async def parse_and_validate_protobuf_schema():
    """Parse Protobuf schema using xwsyntax, validate data using xwschema."""
    
    # Step 1: Parse Protobuf schema file using xwsyntax
    proto_grammar = BidirectionalGrammar.load('protobuf')
    with open('user.proto', 'r') as f:
        proto_text = f.read()
    
    try:
        proto_ast = proto_grammar.parse(proto_text)
    except SyntaxError as e:
        print(f"Syntax error in Protobuf schema: {e}")
        return
    
    # Step 2: Convert AST to xwschema format
    schema_dict = convert_proto_ast_to_schema_dict(proto_ast)
    
    # Step 3: Create xwschema instance
    schema = XWSchema(schema_dict)
    
    # Step 4: Validate data
    data = {
        'id': 1,
        'name': 'Alice',
        'email': 'alice@example.com'
    }
    
    is_valid, errors = await schema.validate(data)
    if not is_valid:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    
    # Step 5: Get structured issues
    issues = await schema.validate_issues(data)
    for issue in issues:
        print(f"Path: {issue['node_path']}")
        print(f"Type: {issue['issue_type']}")
        print(f"Message: {issue['message']}")


def convert_proto_ast_to_schema_dict(ast):
    """Convert Protobuf AST to xwschema format."""
    # Implementation would traverse AST and build schema dictionary
    # This is a placeholder - actual implementation would be more complex
    schema_dict = {
        'type': 'object',
        'properties': {}
    }
    # ... AST traversal logic ...
    return schema_dict
```

---

## Benefits Summary

### Code Reuse
- ✅ No duplicate parsing logic
- ✅ Consistent parsing across formats
- ✅ Shared grammar maintenance

### Performance
- ✅ Leverage xwsyntax's optimized AST operations
- ✅ Benefit from xwnode's performance optimizations
- ✅ Efficient format conversions

### Maintainability
- ✅ Single source of truth for grammar definitions
- ✅ Grammar updates automatically benefit both libraries
- ✅ Reduced maintenance burden

### Extensibility
- ✅ New schema formats in xwsyntax automatically available
- ✅ Easy to add new format conversions
- ✅ Unified extension points

### User Experience
- ✅ Comprehensive validation (syntax + semantics)
- ✅ Better error messages
- ✅ Rich IDE integration
- ✅ Consistent API patterns

---

## Dependencies

### Optional Dependency

xwsyntax should be an **optional dependency** for xwschema:

```python
# xwschema/src/exonware/xwschema/engine.py

try:
    from exonware.xwsyntax import BidirectionalGrammar
    XWSYNTAX_AVAILABLE = True
except ImportError:
    XWSYNTAX_AVAILABLE = False
    BidirectionalGrammar = None

class XWSchemaEngine:
    def load_schema(self, path: Path, format: SchemaFormat):
        if XWSYNTAX_AVAILABLE and format in SUPPORTED_XWSYNTAX_FORMATS:
            # Use xwsyntax for parsing
            return self._load_via_xwsyntax(path, format)
        else:
            # Fallback to current method
            return self._load_via_serializer(path, format)
```

This ensures:
- xwschema works without xwsyntax (backward compatible)
- Enhanced features when xwsyntax is available
- No breaking changes

---

## Future Enhancements

### 1. **Schema Language Server**
Combine xwsyntax's LSP capabilities with xwschema's validation for a complete schema editing experience.

### 2. **Schema Diff/Merge**
Use AST comparison for intelligent schema versioning and merging.

### 3. **Schema Documentation Generation**
Generate documentation from schemas using xwsyntax's formatting capabilities.

### 4. **Schema Testing Framework**
Combine syntax and semantic validation for comprehensive schema testing.

---

## Conclusion

The relationship between xwsyntax and xwschema is natural and complementary:

- **xwsyntax** handles **syntax** (parsing, generating, formatting)
- **xwschema** handles **semantics** (validation, constraints, type checking)

Together, they provide a complete solution for schema management:
- Parse schema files (xwsyntax)
- Validate data against schemas (xwschema)
- Convert between formats (both)
- Provide IDE integration (xwsyntax + xwschema)

The collaboration opportunities are significant and will result in:
- Better code reuse
- Improved performance
- Enhanced user experience
- Reduced maintenance burden

---

## References

- [xwsyntax README](../../xwsyntax/README.md)
- [xwsyntax Architecture](../../xwsyntax/docs/ARCHITECTURE.md)
- [xwschema README](../README.md)
- [Schema Formats Needed](../SCHEMA_FORMATS_NEEDED.md)

---

**Last Updated:** December 2025  
**Status:** Planning Phase - To be implemented in future releases

