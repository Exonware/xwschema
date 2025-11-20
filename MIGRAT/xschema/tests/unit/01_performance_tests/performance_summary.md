# xSchema Performance Test Results

## Overview
Performance tests were conducted on the xSchema library across four different formats: JSON, XML, TOML, and YAML. Currently, only the **legacy** version is available and functional.

## Test Environment
- **Available Versions**: legacy (v0.1.0)
- **Tested Formats**: JSON, XML, TOML, YAML
- **Operations Tested**: Schema Creation, Validation, Serialization, Property Access
- **Measurement**: Time (milliseconds) and Memory (KB)

---

## JSON Format Performance

| Operation | Version | Time (ms) | Memory (KB) | Status |
|-----------|---------|-----------|-------------|--------|
| Schema Creation | legacy | 0.053 | 4.0 | ✅ PASS |
| Validation | legacy | 0.029 | 0.0 | ✅ PASS |
| Serialization | legacy | 0.007 | 0.0 | ✅ PASS |
| Property Access | legacy | 0.078 | 56.0 | ✅ PASS |

**Summary**: JSON format shows excellent performance with very fast serialization (0.007ms) and reasonable validation times. Property access uses the most memory (56KB) but is still very fast.

---

## XML Format Performance

| Operation | Version | Time (ms) | Memory (KB) | Status |
|-----------|---------|-----------|-------------|--------|
| Schema Creation | legacy | 0.031 | 0.0 | ✅ PASS |
| Validation | legacy | 0.022 | 0.0 | ✅ PASS |
| Serialization | legacy | 0.008 | 0.0 | ✅ PASS |
| Property Access | legacy | 0.051 | 4.0 | ✅ PASS |

**Summary**: XML format demonstrates the fastest schema creation (0.031ms) and very efficient memory usage across all operations. Property access is also the fastest among all formats.

---

## TOML Format Performance

| Operation | Version | Time (ms) | Memory (KB) | Status |
|-----------|---------|-----------|-------------|--------|
| Schema Creation | legacy | 0.066 | 0.0 | ✅ PASS |
| Validation | legacy | 0.011 | 0.0 | ✅ PASS |
| Serialization | legacy | 0.010 | 0.0 | ✅ PASS |
| Property Access | legacy | 0.059 | 4.0 | ✅ PASS |

**Summary**: TOML format shows the fastest validation performance (0.011ms) and very consistent memory usage. All operations complete in under 0.07ms.

---

## YAML Format Performance

| Operation | Version | Time (ms) | Memory (KB) | Status |
|-----------|---------|-----------|-------------|--------|
| Schema Creation | legacy | 0.041 | 0.0 | ✅ PASS |
| Validation | legacy | 0.016 | 0.0 | ✅ PASS |
| Serialization | legacy | 0.010 | 0.0 | ✅ PASS |
| Property Access | legacy | 0.064 | 4.0 | ✅ PASS |

**Summary**: YAML format provides balanced performance across all operations with very low memory usage. Validation is particularly efficient at 0.016ms.

---

## Performance Rankings

### 🏆 Fastest Operations by Category

| Category | Winner | Format | Time (ms) |
|----------|--------|--------|-----------|
| Schema Creation | legacy | XML | 0.031 |
| Validation | legacy | TOML | 0.011 |
| Serialization | legacy | JSON | 0.007 |
| Property Access | legacy | XML | 0.051 |

### 📊 Overall Performance Summary

| Format | Avg Time (ms) | Avg Memory (KB) | Success Rate |
|--------|---------------|-----------------|--------------|
| XML | 0.028 | 1.0 | 100% |
| TOML | 0.037 | 1.0 | 100% |
| YAML | 0.033 | 1.0 | 100% |
| JSON | 0.042 | 15.0 | 100% |

---

## Key Findings

1. **XML is the fastest overall** with the lowest average time (0.028ms)
2. **JSON has the highest memory usage** due to property access (56KB)
3. **All formats show excellent performance** with sub-millisecond operation times
4. **TOML has the fastest validation** at 0.011ms
5. **JSON has the fastest serialization** at 0.007ms
6. **All operations completed successfully** with 100% success rate

## Recommendations

- **For speed-critical applications**: Use XML format
- **For memory-constrained environments**: Use TOML or YAML
- **For general use**: All formats perform excellently, choose based on your data structure needs
- **For validation-heavy workloads**: TOML provides the best validation performance

---

## Test Details

- **Total Tests Run**: 16
- **Successful Tests**: 16 (100%)
- **Failed Tests**: 0
- **Available xSchema Versions**: 1 (legacy)
- **Missing Versions**: new, new_2, new_3 (due to missing dependencies)

The legacy version of xSchema demonstrates excellent performance across all tested formats and operations, making it a reliable choice for schema validation and processing tasks.
