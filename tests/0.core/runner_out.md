# Test Runner Output

**Library:** xwschema  
**Layer:** 0.core  
**Generated:** 17-Dec-2025 19:40:56  
**Description:** Core Tests - Fast, High-Value Checks (20% tests for 80% value)

---

---
# xwschema - Core Tests - Fast, High-Value Checks (20% tests for 80% value)
---
**Test Directory:** `D:\OneDrive\DEV\exonware\xwschema\tests\0.core`
**Output File:** `D:\OneDrive\DEV\exonware\xwschema\tests\0.core\runner_out.md`
**Added to path:** `D:\OneDrive\DEV\exonware\xwschema\src`

**Discovered:** 7 test file(s)

## Running Tests
```bash
C:\Program Files\Python312\python.exe -m pytest -v --tb=short D:\OneDrive\DEV\exonware\xwschema\tests\0.core -m xwschema_core
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
collecting ... collected 164 items

0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_type_only <- tests\core\test_builder.py PASSED [  0%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_title <- tests\core\test_builder.py PASSED [  1%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_description <- tests\core\test_builder.py PASSED [  1%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_format <- tests\core\test_builder.py PASSED [  2%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_enum <- tests\core\test_builder.py PASSED [  3%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_default <- tests\core\test_builder.py PASSED [  3%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_nullable <- tests\core\test_builder.py PASSED [  4%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_deprecated <- tests\core\test_builder.py PASSED [  4%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_confidential <- tests\core\test_builder.py PASSED [  5%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_pattern <- tests\core\test_builder.py PASSED [  6%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_length_min <- tests\core\test_builder.py PASSED [  6%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_length_max <- tests\core\test_builder.py PASSED [  7%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_strip_whitespace <- tests\core\test_builder.py PASSED [  7%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_to_upper <- tests\core\test_builder.py PASSED [  8%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_to_lower <- tests\core\test_builder.py PASSED [  9%]
0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_value_min <- tests\core\test_builder.py FAILED [  9%]

================================== FAILURES ===================================
________________ TestXWSchemaBuilder.test_build_with_value_min ________________
D:\OneDrive\DEV\exonware\xwschema\tests\core\test_builder.py:117: in test_build_with_value_min
    ???
..\src\exonware\xwschema\builder.py:167: in build_schema_dict
    type(None): 'null'
    ^^^^^^^^^^
E   TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'
=========================== short test summary info ===========================
FAILED 0.core\test_builder.py::TestXWSchemaBuilder::test_build_with_value_min - TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
======================== 1 failed, 15 passed in 0.53s =========================

```

### Summary

```
======================== 1 failed, 15 passed in 0.53s =========================
```

**Status:** ❌ FAILED

