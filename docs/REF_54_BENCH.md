# Benchmark reference — xwschema (REF_54_BENCH)

**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 8 (performance)  
**Producing guide:** [GUIDE_54_BENCH.md](../../docs/guides/GUIDE_54_BENCH.md)

---

## Purpose

Benchmark and performance reference for xwschema. No formal SLAs yet; performance is covered by advance-layer tests and one example benchmark script.

---

## Current status

| Item | Location | Notes |
|------|----------|--------|
| **Example benchmark** | [examples/simple_examples/xwschema_parts_benchmark.py](../examples/simple_examples/xwschema_parts_benchmark.py) | Runnable script in examples; schema validation/parts performance. |
| **Performance tests** | [tests/3.advance/test_performance.py](../tests/3.advance/test_performance.py) | Part of 4-layer suite; run with `python tests/runner.py --advance` or `--performance`. |
| **REF_01_REQ sec. 8** | Validation and conversion performance; configurable timeouts and limits; advance/performance tests. | Addressed via config (PerformanceConfig, max schema size, nesting depth, timeout) and 3.advance tests. |
| **Run evidence** | [logs/benchmarks/](logs/benchmarks/) | INDEX + BENCH_* (e.g. legacy format summary). |

---

## Formal SLAs

- **None yet.** When SLAs are defined (e.g. validation latency, conversion throughput), they will be added here and evidence logged under `docs/logs/benchmarks/` per GUIDE_54_BENCH.

---

## Traceability

- **Requirements:** [REF_01_REQ.md](REF_01_REQ.md) sec. 8  
- **Tests:** [REF_51_TEST.md](REF_51_TEST.md) (3.advance, performance)  
- **Examples:** [examples/simple_examples/](../examples/simple_examples/) (includes xwschema_parts_benchmark.py)

---

*Per GUIDE_54_BENCH. For run evidence, use tests/runner.py --performance and examples/simple_examples/xwschema_parts_benchmark.py until docs/logs/benchmarks/ is used.*
