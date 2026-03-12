# Benchmark: Legacy format performance (JSON, XML, TOML, YAML)

**Date:** 17-Dec-2025 (historical run)  
**Scope:** xwschema legacy implementation; formats JSON, XML, TOML, YAML  
**Operations:** Schema creation, validation, serialization, property access  
**Measurement:** Time (ms), Memory (KB)

---

## Summary

Performance tests showed sub-millisecond operation times and 100% success rate across formats. Only legacy version was tested (new/new_2/new_3 not available in run environment).

---

## Results by format

| Format | Avg time (ms) | Avg memory (KB) | Notes |
|--------|----------------|-----------------|--------|
| XML | 0.028 | 1.0 | Fastest overall; fastest property access |
| TOML | 0.037 | 1.0 | Fastest validation (0.011 ms) |
| YAML | 0.033 | 1.0 | Fastest serialization (0.006 ms) |
| JSON | 0.042 | 15.0 | Fast serialization (0.007 ms); higher memory on property access |

---

## Fastest by category

- **Schema creation:** XML (0.031 ms)
- **Validation:** TOML (0.011 ms)
- **Serialization:** JSON (0.007 ms)
- **Property access:** XML (0.051 ms)

---

## Recommendations (from run)

- Speed-critical: XML format
- Memory-constrained: TOML or YAML
- Validation-heavy: TOML
- General use: all formats suitable; choose by data structure needs

---

*Value consolidated from logs/performance_summary.md and logs/version_comparison_summary.md during docs archive migration (08-Feb-2026). Current benchmarks: REF_54_BENCH, tests/3.advance/test_performance.py, examples/simple_examples/xwschema_parts_benchmark.py.*
