# XWSchema Validation Verification

## Purpose
XWSchema ensures that **XWData** or **native Python structures** follow the schema format.

## How It Works

### 1. **Dual Support: XWData and Native Structures**

XWSchema validates both:
- **XWData instances**: Uses efficient path navigation via `data[field]`
- **Native Python structures**: Standard dict/list validation

### 2. **Validation Flow**

```python
# In validator.py:validate_schema()
if XWData and isinstance(data, XWData):
    # Use XWData for efficient navigation
    return self._validate_with_xwdata(data, schema)
else:
    # Standard validation for native Python types
    return self._validate_native(data, schema)
```

### 3. **XWData Validation** (`_validate_with_xwdata`)

- Uses XWData's efficient path navigation: `data[field]`
- Leverages XWData's `to_native()` for type checking
- Supports nested structures via recursive validation
- Handles required fields, properties, and array items

### 4. **Native Structure Validation** (`_validate_native`)

- Validates standard Python dict/list structures
- Type checking, constraints, enums, patterns
- Nested object and array validation
- Required fields validation

## Examples

### Example 1: Native Dict Validation
```python
schema = XWSchema({
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'age': {'type': 'integer'}
    },
    'required': ['name']
})

# Validate native dict
is_valid, errors = await schema.validate({'name': 'Alice', 'age': 30})
assert is_valid  # True
```

### Example 2: XWData Validation
```python
from exonware.xwdata import XWData

# Create XWData instance
data = XWData.from_native({'name': 'Alice', 'age': 30})

# Validate XWData
is_valid, errors = await schema.validate(data)
assert is_valid  # True - uses efficient XWData path navigation
```

### Example 3: Invalid Data
```python
# Missing required field
is_valid, errors = await schema.validate({'age': 30})
assert not is_valid  # False
assert 'Required field' in errors[0]

# Wrong type
is_valid, errors = await schema.validate({'name': 123})  # Should be string
assert not is_valid  # False
```

## Key Features

✅ **Dual Support**: Works with both XWData and native structures
✅ **Efficient Navigation**: Uses XWData's path navigation when available
✅ **Type Validation**: Validates types, constraints, enums, patterns
✅ **Nested Structures**: Supports nested objects and arrays
✅ **Required Fields**: Validates required fields
✅ **Error Reporting**: Returns detailed error messages

## Implementation Details

- **Facade**: `XWSchema.validate()` accepts any data type
- **Engine**: `XWSchemaEngine.validate_data()` coordinates validation
- **Validator**: `XWSchemaValidator.validate_schema()` implements validation logic
- **XWData Integration**: Automatically detects XWData instances and uses optimized path navigation
