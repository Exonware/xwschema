# Test Runner Output

**Library:** xwschema  
**Layer:** 1.unit  
**Generated:** 17-Dec-2025 19:41:06  
**Description:** Unit Tests - Individual Component Tests

---

---
# xwschema - Unit Tests - Individual Component Tests
---
**Test Directory:** `D:\OneDrive\DEV\exonware\xwschema\tests\1.unit`
**Output File:** `D:\OneDrive\DEV\exonware\xwschema\tests\1.unit\runner_out.md`
**Added to path:** `D:\OneDrive\DEV\exonware\xwschema\src`

**Discovered:** 3 test file(s)

## Running Tests
```bash
C:\Program Files\Python312\python.exe -m pytest -v --tb=short D:\OneDrive\DEV\exonware\xwschema\tests\1.unit -m xwschema_unit
```
**Working directory:** `D:\OneDrive\DEV\exonware\xwschema\tests`

### Test Output
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.1, pluggy-1.6.0 -- C:\Program Files\Python312\python.exe
cachedir: .pytest_cache
rootdir: D:\OneDrive\DEV\exonware\xwschema
configfile: pyproject.toml
plugins: anyio-4.12.0, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 107 items

1.unit\test_base_formats.py::TestSchemaPrimitiveType::test_all_primitives <- tests\unit\test_base_formats.py PASSED [  0%]
1.unit\test_base_formats.py::TestSchemaPrimitiveType::test_primitive_constants <- tests\unit\test_base_formats.py PASSED [  1%]
1.unit\test_base_formats.py::TestSchemaComplexType::test_all_complex <- tests\unit\test_base_formats.py PASSED [  2%]
1.unit\test_base_formats.py::TestSchemaComplexType::test_complex_constants <- tests\unit\test_base_formats.py PASSED [  3%]
1.unit\test_base_formats.py::TestSchemaTypeMapper::test_map_type_json_to_avro <- tests\unit\test_base_formats.py PASSED [  4%]
1.unit\test_base_formats.py::TestSchemaTypeMapper::test_map_type_avro_to_json <- tests\unit\test_base_formats.py PASSED [  5%]
1.unit\test_base_formats.py::TestSchemaTypeMapper::test_map_type_unknown <- tests\unit\test_base_formats.py PASSED [  6%]
1.unit\test_base_formats.py::TestSchemaTypeMapper::test_reverse_map_type <- tests\unit\test_base_formats.py PASSED [  7%]
1.unit\test_base_formats.py::TestSchemaPropertyMapper::test_map_property_json_to_avro <- tests\unit\test_base_formats.py PASSED [  8%]
1.unit\test_base_formats.py::TestSchemaPropertyMapper::test_map_property_avro_to_json <- tests\unit\test_base_formats.py PASSED [  9%]
1.unit\test_base_formats.py::TestSchemaPropertyMapper::test_map_property_unknown <- tests\unit\test_base_formats.py PASSED [ 10%]
1.unit\test_base_formats.py::TestSchemaPropertyMapper::test_map_schema_json_to_avro <- tests\unit\test_base_formats.py PASSED [ 11%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_detect_references_json_schema <- tests\unit\test_base_formats.py PASSED [ 12%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_detect_references_no_refs <- tests\unit\test_base_formats.py PASSED [ 13%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_merge_schemas_allof <- tests\unit\test_base_formats.py PASSED [ 14%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_merge_schemas_deep <- tests\unit\test_base_formats.py PASSED [ 14%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_merge_schemas_shallow <- tests\unit\test_base_formats.py PASSED [ 15%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_flatten_schema_with_refs <- tests\unit\test_base_formats.py PASSED [ 16%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_flatten_schema_no_refs <- tests\unit\test_base_formats.py PASSED [ 17%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_generate_from_data_string <- tests\unit\test_base_formats.py PASSED [ 18%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_generate_from_data_object <- tests\unit\test_base_formats.py PASSED [ 19%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_generate_from_data_array <- tests\unit\test_base_formats.py PASSED [ 20%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_compare_schemas_identical <- tests\unit\test_base_formats.py PASSED [ 21%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_compare_schemas_different <- tests\unit\test_base_formats.py PASSED [ 22%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_compare_schemas_with_added_properties <- tests\unit\test_base_formats.py PASSED [ 23%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_is_compatible_same_type <- tests\unit\test_base_formats.py PASSED [ 24%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_is_compatible_different_type <- tests\unit\test_base_formats.py PASSED [ 25%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_extract_metadata <- tests\unit\test_base_formats.py PASSED [ 26%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_preserve_metadata <- tests\unit\test_base_formats.py PASSED [ 27%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_merge_metadata <- tests\unit\test_base_formats.py PASSED [ 28%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_map_type_to <- tests\unit\test_base_formats.py PASSED [ 28%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_map_type_from <- tests\unit\test_base_formats.py PASSED [ 29%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_is_primitive_type <- tests\unit\test_base_formats.py PASSED [ 30%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_is_complex_type <- tests\unit\test_base_formats.py PASSED [ 31%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_extract_definitions <- tests\unit\test_base_formats.py PASSED [ 32%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_extract_properties <- tests\unit\test_base_formats.py PASSED [ 33%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_extract_types <- tests\unit\test_base_formats.py PASSED [ 34%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_validate_schema_structure <- tests\unit\test_base_formats.py PASSED [ 35%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_validate_schema_structure_invalid <- tests\unit\test_base_formats.py PASSED [ 36%]
1.unit\test_base_formats.py::TestASchemaSerializationCommon::test_validate_schema <- tests\unit\test_base_formats.py PASSED [ 37%]
1.unit\test_config.py::TestXWSchemaConfig::test_config_init_default <- tests\unit\test_config.py PASSED [ 38%]
1.unit\test_config.py::TestXWSchemaConfig::test_config_init_with_validation <- tests\unit\test_config.py PASSED [ 39%]
1.unit\test_config.py::TestXWSchemaConfig::test_config_init_with_generation <- tests\unit\test_config.py PASSED [ 40%]
1.unit\test_config.py::TestXWSchemaConfig::test_config_init_with_performance <- tests\unit\test_config.py PASSED [ 41%]
1.unit\test_config.py::TestXWSchemaConfig::test_config_default_factory <- tests\unit\test_config.py PASSED [ 42%]
1.unit\test_config.py::TestXWSchemaConfig::test_config_copy <- tests\unit\test_config.py FAILED [ 42%]

================================== FAILURES ===================================
_____________________ TestXWSchemaConfig.test_config_copy _____________________
D:\OneDrive\DEV\exonware\xwschema\tests\unit\test_config.py:64: in test_config_copy
    ???
E   AttributeError: 'XWSchemaConfig' object has no attribute 'copy'
=========================== short test summary info ===========================
FAILED 1.unit\test_config.py::TestXWSchemaConfig::test_config_copy - AttributeError: 'XWSchemaConfig' object has no attribute 'copy'
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
======================== 1 failed, 45 passed in 0.65s =========================

```

### Summary

```
======================== 1 failed, 45 passed in 0.65s =========================
```

**Status:** ❌ FAILED

