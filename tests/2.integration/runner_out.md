# Test Runner Output

**Library:** xwschema  
**Layer:** 2.integration  
**Generated:** 17-Dec-2025 19:41:06  
**Description:** Integration Tests - End-to-End Scenario Tests

---

---
# xwschema - Integration Tests - End-to-End Scenario Tests
---
**Test Directory:** `D:\OneDrive\DEV\exonware\xwschema\tests\2.integration`
**Output File:** `D:\OneDrive\DEV\exonware\xwschema\tests\2.integration\runner_out.md`
**Added to path:** `D:\OneDrive\DEV\exonware\xwschema\src`

**Discovered:** 1 test file(s)

## Running Tests
```bash
C:\Program Files\Python312\python.exe -m pytest -v --tb=short D:\OneDrive\DEV\exonware\xwschema\tests\2.integration -m xwschema_integration
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
collecting ... collected 15 items

2.integration\test_end_to_end.py::TestEndToEndWorkflows::test_load_validate_save_workflow <- tests\integration\test_end_to_end.py FAILED [  6%]

================================== FAILURES ===================================
___________ TestEndToEndWorkflows.test_load_validate_save_workflow ____________
D:\OneDrive\DEV\exonware\xwschema\tests\integration\test_end_to_end.py:56: in test_load_validate_save_workflow
    ???
E   TypeError: XWSchema.load() missing 1 required positional argument: 'path'
=========================== short test summary info ===========================
FAILED 2.integration\test_end_to_end.py::TestEndToEndWorkflows::test_load_validate_save_workflow - TypeError: XWSchema.load() missing 1 required positional argument: 'path'
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
============================== 1 failed in 0.60s ==============================

```

### Summary

```
============================== 1 failed in 0.60s ==============================
```

**Status:** ❌ FAILED

