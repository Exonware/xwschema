#!/usr/bin/env python3
"""
XWSchema Usage Examples

Demonstrates how to use XWSchema with:
- Native Python data structures (dict, list)
- XWData instances
- Schema generation from data
- Schema validation
- Schema builder pattern
- Structured error reporting with node_path and issue_type
"""

import asyncio
from pathlib import Path

# Import XWSchema and related components
from exonware.xwschema import (
    XWSchema, XWSchemaBuilder, SchemaFormat, SchemaGenerationMode, ValidationIssue
)
from exonware.xwschema.config import XWSchemaConfig

# Import XWData (if available)
try:
    from exonware.xwdata import XWData
    XWDATA_AVAILABLE = True
except ImportError:
    XWDATA_AVAILABLE = False
    print("XWData not available, skipping XWData examples")


# ==============================================================================
# EXAMPLE 1: Using XWSchema with Native Python Data
# ==============================================================================

async def example_native_validation():
    """Example: Validate native Python dict/list against schema."""
    print("\n=== Example 1: Native Python Data Validation ===\n")
    
    # Create schema from native dict
    schema_dict = {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'minLength': 2,
                'maxLength': 50
            },
            'age': {
                'type': 'integer',
                'minimum': 0,
                'maximum': 150
            },
            'email': {
                'type': 'string',
                'format': 'email'
            }
        },
        'required': ['name', 'age']
    }
    
    schema = XWSchema(schema_dict)
    
    # Validate valid data
    valid_data = {
        'name': 'Alice',
        'age': 30,
        'email': 'alice@example.com'
    }
    is_valid, errors = await schema.validate(valid_data)
    print(f"Valid data result: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    
    # Validate invalid data
    invalid_data = {
        'name': 'A',  # Too short
        'age': 200,   # Too large
        # Missing required 'email' field
    }
    is_valid, errors = await schema.validate(invalid_data)
    print(f"\nInvalid data result: {is_valid}")
    if errors:
        print(f"Errors: {errors}")


# ==============================================================================
# EXAMPLE 2: Using XWSchema with XWData
# ==============================================================================

async def example_xwdata_validation():
    """Example: Validate XWData instance against schema."""
    if not XWDATA_AVAILABLE:
        print("\n=== Example 2: XWData Validation (Skipped - XWData not available) ===\n")
        return
    
    print("\n=== Example 2: XWData Validation ===\n")
    
    # Create schema
    schema = XWSchema({
        'type': 'object',
        'properties': {
            'users': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'active': {'type': 'boolean'}
                    },
                    'required': ['id', 'name']
                },
                'minItems': 1
            }
        }
    })
    
    # Create XWData instance
    data = XWData.from_native({
        'users': [
            {'id': 1, 'name': 'Alice', 'active': True},
            {'id': 2, 'name': 'Bob', 'active': False}
        ]
    })
    
    # Validate XWData instance
    is_valid, errors = await schema.validate(data)
    print(f"XWData validation result: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    
    # XWSchema automatically uses XWData's efficient path navigation
    # for validation, making it faster for large nested structures


# ==============================================================================
# EXAMPLE 3: Generate Schema from Data
# ==============================================================================

async def example_schema_generation():
    """Example: Generate schema from existing data."""
    print("\n=== Example 3: Schema Generation from Data ===\n")
    
    # Generate schema from native Python data
    sample_data = {
        'product_id': 12345,
        'name': 'Widget',
        'price': 29.99,
        'in_stock': True,
        'tags': ['electronics', 'gadgets'],
        'metadata': {
            'created_at': '2025-01-01',
            'updated_at': '2025-01-02'
        }
    }
    
    # Generate schema in INFER mode (basic type inference)
    schema = await XWSchema.from_data(sample_data, mode=SchemaGenerationMode.INFER)
    print("Generated schema (INFER mode):")
    print(schema.to_native())
    
    # Generate schema in COMPREHENSIVE mode (includes examples, descriptions, etc.)
    comprehensive_schema = await XWSchema.from_data(
        sample_data,
        mode=SchemaGenerationMode.COMPREHENSIVE
    )
    print("\nGenerated schema (COMPREHENSIVE mode):")
    print(comprehensive_schema.to_native())
    
    # Generate schema from XWData (if available)
    if XWDATA_AVAILABLE:
        xwdata = XWData.from_native(sample_data)
        schema_from_xwdata = await XWSchema.from_data(xwdata)
        print("\nGenerated schema from XWData:")
        print(schema_from_xwdata.to_native())


# ==============================================================================
# EXAMPLE 4: Schema Builder Pattern
# ==============================================================================

async def example_schema_builder():
    """Example: Build schema using XWSchemaBuilder."""
    print("\n=== Example 4: Schema Builder Pattern ===\n")
    
    # Build schema using builder pattern
    schema_dict = XWSchemaBuilder.build_schema_dict(
        type='object',
        title='User Profile',
        description='User profile information',
        properties={
            'username': XWSchemaBuilder.build_schema_dict(
                type='string',
                length_min=3,
                length_max=20,
                pattern='^[a-zA-Z0-9_]+$'
            ),
            'email': XWSchemaBuilder.build_schema_dict(
                type='string',
                format='email'
            ),
            'age': XWSchemaBuilder.build_schema_dict(
                type='integer',
                value_min=18,
                value_max=120
            ),
            'preferences': XWSchemaBuilder.build_schema_dict(
                type='object',
                properties={
                    'theme': XWSchemaBuilder.build_schema_dict(
                        type='string',
                        enum=['light', 'dark', 'auto']
                    ),
                    'notifications': XWSchemaBuilder.build_schema_dict(
                        type='boolean',
                        default=True
                    )
                }
            )
        },
        required=['username', 'email']
    )
    
    schema = XWSchema(schema_dict)
    
    # Validate data
    user_data = {
        'username': 'alice123',
        'email': 'alice@example.com',
        'age': 25,
        'preferences': {
            'theme': 'dark',
            'notifications': True
        }
    }
    
    is_valid, errors = await schema.validate(user_data)
    print(f"Validation result: {is_valid}")
    if errors:
        print(f"Errors: {errors}")


# ==============================================================================
# EXAMPLE 5: Schema with Nullable and Complex Types
# ==============================================================================

async def example_complex_schema():
    """Example: Complex schema with nullable, arrays, and nested objects."""
    print("\n=== Example 5: Complex Schema with Nullable ===\n")
    
    schema = XWSchema({
        'type': 'object',
        'properties': {
            'id': {'type': 'integer'},
            'name': {'type': 'string'},
            'middle_name': {
                'type': 'string',
                'nullable': True  # Can be null
            },
            'scores': {
                'type': 'array',
                'items': {
                    'type': 'number',
                    'minimum': 0,
                    'maximum': 100
                },
                'minItems': 1,
                'uniqueItems': True
            },
            'address': {
                'type': 'object',
                'properties': {
                    'street': {'type': 'string'},
                    'city': {'type': 'string'},
                    'zip_code': {'type': 'string', 'pattern': '^\\d{5}$'}
                },
                'required': ['street', 'city'],
                'additionalProperties': False  # No extra fields allowed
            }
        },
        'required': ['id', 'name']
    })
    
    # Valid data with null value
    valid_data = {
        'id': 1,
        'name': 'Bob',
        'middle_name': None,  # Nullable field
        'scores': [85, 90, 88],
        'address': {
            'street': '123 Main St',
            'city': 'Springfield',
            'zip_code': '12345'
        }
    }
    
    is_valid, errors = await schema.validate(valid_data)
    print(f"Valid complex data: {is_valid}")
    
    # Invalid data
    invalid_data = {
        'id': 1,
        'name': 'Bob',
        'scores': [85, 85, 90],  # Duplicate values (uniqueItems violation)
        'address': {
            'street': '123 Main St',
            'city': 'Springfield',
            'zip_code': '12345',
            'extra_field': 'not allowed'  # additionalProperties: false violation
        }
    }
    
    is_valid, errors = await schema.validate(invalid_data)
    print(f"\nInvalid complex data: {is_valid}")
    if errors:
        print(f"Errors: {errors}")


# ==============================================================================
# EXAMPLE 6: Structured Error Reporting with node_path and issue_type
# ==============================================================================

async def example_structured_errors():
    """Example: Get structured validation issues with node_path and issue_type."""
    print("\n=== Example 6: Structured Error Reporting ===\n")
    
    schema = XWSchema({
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'minLength': 3,
                'maxLength': 50
            },
            'age': {
                'type': 'integer',
                'minimum': 18,
                'maximum': 120
            },
            'email': {
                'type': 'string',
                'pattern': '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
            },
            'scores': {
                'type': 'array',
                'items': {
                    'type': 'number',
                    'minimum': 0,
                    'maximum': 100
                },
                'minItems': 1,
                'uniqueItems': True
            }
        },
        'required': ['name', 'age', 'email']
    })
    
    # Invalid data with multiple issues
    invalid_data = {
        'name': 'AB',  # Too short (minLength violation)
        'age': 15,     # Too young (minimum violation)
        'email': 'invalid-email',  # Pattern violation
        'scores': [85, 85, 105]  # Duplicate and out of range
    }
    
    # Get structured issues
    issues = await schema.validate_issues(invalid_data)
    
    print(f"Found {len(issues)} validation issues:\n")
    for issue in issues:
        print(f"  Path: {issue['node_path']}")
        print(f"  Type: {issue['issue_type']}")
        print(f"  Message: {issue['message']}")
        print()
    
    # Group issues by type
    issues_by_type = {}
    for issue in issues:
        issue_type = issue['issue_type']
        if issue_type not in issues_by_type:
            issues_by_type[issue_type] = []
        issues_by_type[issue_type].append(issue)
    
    print("\nIssues grouped by type:")
    for issue_type, type_issues in issues_by_type.items():
        print(f"  {issue_type}: {len(type_issues)} issue(s)")
        for issue in type_issues:
            print(f"    - {issue['node_path']}: {issue['message']}")


# ==============================================================================
# EXAMPLE 7: Load and Save Schema
# ==============================================================================

async def example_schema_io():
    """Example: Load schema from file and save to file."""
    print("\n=== Example 7: Schema File I/O ===\n")
    
    # Create a schema
    schema = XWSchema({
        'type': 'object',
        'properties': {
            'title': {'type': 'string'},
            'content': {'type': 'string'}
        }
    })
    
    # Save schema to file
    schema_path = Path('example_schema.json')
    await schema.save(schema_path, format=SchemaFormat.JSON_SCHEMA)
    print(f"Schema saved to {schema_path}")
    
    # Load schema from file
    loaded_schema = await XWSchema.load(schema_path)
    print(f"Schema loaded from {schema_path}")
    print(f"Loaded schema: {loaded_schema.to_native()}")
    
    # Clean up
    if schema_path.exists():
        schema_path.unlink()
        print(f"Cleaned up {schema_path}")


# ==============================================================================
# EXAMPLE 8: Synchronous Validation (for non-async contexts)
# ==============================================================================

async def example_sync_validation():
    """Example: Synchronous validation wrapper (demonstrated in async context)."""
    print("\n=== Example 8: Synchronous Validation ===\n")
    
    schema = XWSchema({
        'type': 'string',
        'minLength': 5
    })
    
    # In async context, use await validate() directly
    is_valid, errors = await schema.validate('hello')
    print(f"Validation result: {is_valid}")
    
    is_valid, errors = await schema.validate('hi')  # Too short
    print(f"Validation result: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    
    # Use validate_issues() for structured errors
    issues = await schema.validate_issues('hi')
    print(f"\nStructured issues: {len(issues)}")
    for issue in issues:
        print(f"  {issue['node_path']}: {issue['issue_type']} - {issue['message']}")
    
    print("\nNote: validate_sync() and validate_issues_sync() are available")
    print("      for use in non-async contexts (e.g., scripts, CLI tools)")


# ==============================================================================
# MAIN: Run all examples
# ==============================================================================

async def main():
    """Run all examples."""
    print("=" * 70)
    print("XWSchema Usage Examples")
    print("=" * 70)
    
    await example_native_validation()
    await example_xwdata_validation()
    await example_schema_generation()
    await example_schema_builder()
    await example_complex_schema()
    await example_structured_errors()
    await example_schema_io()
    await example_sync_validation()
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == '__main__':
    asyncio.run(main())

