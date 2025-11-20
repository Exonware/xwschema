# xSchema Unit Tests

Comprehensive test suite for all 4 versions of xSchema library with performance benchmarking.

## 📁 Test Structure

```
src/xlib/xschema/tests/unit/
├── 00_core_tests/           # Core functionality tests
│   ├── __init__.py
│   ├── conftest.py          # Common fixtures
│   ├── runner.py            # Test runner
│   ├── test_xschema_core.py # Main core tests
│   └── data/                # Test data files
└── 01_performance_tests/    # Performance and benchmarking tests
    ├── __init__.py
    ├── conftest.py          # Performance fixtures
    ├── runner.py            # Performance test runner
    └── test_xschema_performance.py # Main performance tests
```

## 🧪 Test Coverage

### Core Tests (`00_core_tests/`)

Tests basic functionality across all 4 xSchema versions:
- **legacy** (v0.1.0)
- **new** (v1.0.0)
- **new_2** (v2.0.0)
- **new_3** (v3.0.0)

**Features tested:**
- ✅ Schema creation and initialization
- ✅ Data validation (valid and invalid data)
- ✅ Schema serialization (JSON, dict)
- ✅ Property access and method calls
- ✅ Complex schema handling with references
- ✅ Error handling and reporting
- ✅ Schema reference resolution

### Performance Tests (`01_performance_tests/`)

Comprehensive performance benchmarking with deep and shallow tests:

**Shallow Performance Tests:**
- ⏱️ Simple schema creation performance
- ⏱️ Basic validation performance
- ⏱️ Serialization performance
- ⏱️ Property access performance
- ⏱️ Method call performance

**Deep Performance Tests:**
- 🔍 Complex schema creation performance
- 🔍 Complex validation performance
- 🔍 Reference resolution performance
- 🔍 Error collection performance
- 🔍 Memory usage analysis

**Scalability Tests:**
- 📈 Schema size scalability (10, 50, 100, 200 properties)
- 📈 Data size scalability
- 📈 Memory leak detection
- 📈 Concurrent validation performance

## 🚀 Running Tests

### Core Tests
```bash
# From project root
cd src/xlib/xschema/tests/unit/00_core_tests
python runner.py

# Or using pytest directly
pytest test_xschema_core.py -v
```

### Performance Tests
```bash
# From project root
cd src/xlib/xschema/tests/unit/01_performance_tests
python runner.py

# Or using pytest directly
pytest test_xschema_performance.py -v --durations=10
```

### All Tests
```bash
# From project root
pytest src/xlib/xschema/tests/unit/ -v
```

## 📊 Performance Metrics

The performance tests measure and compare:

- **Time Performance:**
  - Schema creation time
  - Validation time
  - Serialization time
  - Method execution time

- **Memory Performance:**
  - Memory usage during operations
  - Memory leak detection
  - Memory efficiency comparison

- **Scalability:**
  - Performance with different schema sizes
  - Performance with different data sizes
  - Concurrent operation performance

## 🏆 Performance Rankings

Tests automatically generate performance rankings:
- 🥇 Fastest version for each operation
- 🥈 Second fastest
- 🥉 Third fastest
- 📊 Detailed performance comparison tables

## 🔧 Requirements

- Python 3.7+
- pytest
- psutil (for memory monitoring)
- All 4 xSchema versions available

## 📝 Test Output

### Core Tests Output
```
🧪 Running xSchema Core Tests
============================
📋 Available schema versions: ['legacy', 'new', 'new_2', 'new_3']
🎯 Current version: 3.0.0

✅ legacy: Schema created successfully
✅ new: Schema created successfully
✅ new_2: Schema created successfully
✅ new_3: Schema created successfully
```

### Performance Tests Output
```
🚀 Running xSchema Performance Tests
===================================

📊 PERFORMANCE TEST RESULTS
================================================================================

🔍 SIMPLE SCHEMA CREATION
------------------------------------------------------------
✅ legacy        | Time: 0.000123s | Memory:    45.67KB
✅ new           | Time: 0.000098s | Memory:    38.92KB
✅ new_2         | Time: 0.000087s | Memory:    35.14KB
✅ new_3         | Time: 0.000076s | Memory:    32.89KB

🏆 Fastest: new_3 (0.000076s)
```

## 🐛 Troubleshooting

### Import Errors
If you encounter import errors:
1. Ensure you're running from the project root
2. Check that all xSchema versions are available
3. Verify Python path includes `src/`

### Performance Test Failures
- Some versions might not support all features
- Tests are designed to handle missing functionality gracefully
- Check console output for detailed error messages

### Memory Issues
- Performance tests use significant memory
- Ensure sufficient RAM is available
- Tests include garbage collection to minimize memory impact

## 📈 Continuous Integration

These tests are designed to run in CI/CD pipelines:
- Automated performance regression detection
- Version compatibility verification
- Memory leak detection
- Scalability validation

## 🤝 Contributing

When adding new tests:
1. Follow the existing test structure
2. Include both shallow and deep tests
3. Add performance measurements
4. Update this README with new features
5. Ensure tests work across all versions
