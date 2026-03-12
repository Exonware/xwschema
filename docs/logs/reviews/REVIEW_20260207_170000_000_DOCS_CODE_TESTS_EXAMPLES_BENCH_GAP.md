# Review: xwschema — Documentation vs Code vs Tests vs Examples vs Benchmarks (Gap Analysis)

**Date:** 07-Feb-2026 17:00:00.000  
**Project:** xwschema (exonware-xwschema)  
**Artifact type:** Documentation (cross-check with Code, Testing, Examples, Benchmark)  
**Scope:** xwschema repo only — gap between docs (REF_*, INDEX, GUIDE_01_USAGE, README), codebase (src/exonware/xwschema), tests (tests/), examples (examples/), and benchmarks.  
**Producing guide:** [GUIDE_35_REVIEW.md](../../../../docs/guides/GUIDE_35_REVIEW.md)

---

## Summary

**Pass with comments.** Documentation is well aligned with code and tests. Main gaps: (1) examples path is not linked from REF_14_DX or GUIDE_01_USAGE (README does link `examples/`); (2) no REF_54_BENCH — the only benchmark is inside examples (`xwschema_parts_benchmark.py`), and there is no formal benchmark REF or logs; (3) REF_51_TEST “Running tests” section omits `--advance` (runner.py supports it). No critical issues; improvements and traceability actions below.

---

## 1. Documentation ↔ Codebase

| Aspect | Documentation | Codebase | Gap? |
|--------|----------------|----------|------|
| **Public API** | REF_15_API: XWSchema, XWSchemaBuilder, config, enums, ValidationIssue, type_utils, XWSchemaError family | `__all__` in `src/exonware/xwschema/__init__.py` matches (facade, builder, config, defs, errors, type_utils) | **None** — REF_15_API and __all__ aligned. |
| **Internal / not public** | REF_15_API, REF_13_ARCH: engine, format handlers, registry internals, pipeline implementations not in public API | Engine, formats/, registry/, operations/ not in __all__ | **None** — boundaries respected. |
| **Architecture** | REF_13_ARCH: facade + engine; format handlers (JSON Schema, OpenAPI, Avro, Protobuf, GraphQL, WSDL, XSD, Swagger); xwdata as engine base | facade.py, engine.py, formats/schema/*.py, registry/, operations/ | **None** — structure matches. |
| **Key code (DX)** | REF_14_DX: XWSchema(dict), load(path), validate(data), from_data(data) | Facade provides these; async load/save/validate/from_data on XWSchema | **None** — snippets match API. |

**Critical issues:** None.  
**Improvements:** None required for doc ↔ code alignment.

---

## 2. Documentation ↔ Tests

| Aspect | Documentation | Tests | Gap? |
|--------|----------------|-------|------|
| **Layers** | REF_51_TEST: 0.core, 1.unit, 2.integration, 3.advance | tests/0.core/, 1.unit/, 2.integration/, 3.advance/ present | **None** — layout matches. |
| **Layer purpose** | 0.core: facade, builder, engine, validator, generator, roundtrip, utilities; 1.unit: config, formats, conversion; 2: end-to-end; 3: handler caching, performance | 0.core: test_facade, test_builder, test_engine, test_validator, test_generator, test_schema_roundtrip, test_schema_utilities, test_core; 1.unit: test_config, test_formats, engine_tests, formats_tests; 2: test_end_to_end; 3: test_handler_caching, test_performance | **None** — coverage matches. |
| **Runner** | REF_51_TEST: `python tests/runner.py`, `--core`, `--unit`, `--integration` | runner.py supports also `--advance`, `--security`, `--performance` | **Yes** — REF_51_TEST does not list `--advance` (and optional `--security`, `--performance`). |
| **Evidence** | REF_51_TEST: Evidence repo `tests/`, docs/logs/ | docs/logs/reviews/, docs/logs/runner_out.md, performance_summary.md | **None** — logs exist. |

**Critical issues:** None.  
**Improvements:** Add to REF_51_TEST “Running tests”: `python tests/runner.py --advance` (and optionally `--security`, `--performance` if you want them documented).

---

## 3. Documentation ↔ Examples

| Aspect | Documentation | Examples | Gap? |
|--------|----------------|----------|------|
| **REF_14_DX** | “Key code” and “Easy vs advanced”; mentions “docs, examples” in usability | examples/simple_examples/: xwschema_dx.py, xwschema_dx_openapi.py, xwschema_examples.py, xwschema_parts.py, xwschema_parts_benchmark.py + 2 JSON | **Yes** — REF_14_DX does not link to `examples/simple_examples/`. |
| **GUIDE_01_USAGE** | Quick start snippet; “Documentation” table (REF_*, INDEX) | Same examples implement quick start (XWSchema(dict), validate) | **Yes** — GUIDE_01_USAGE does not link to runnable examples path. |
| **README** | “Examples (examples/)” linked | examples/simple_examples/ present | **None** — README links examples. |
| **REF_22 / REF_01_REQ** | “docs, examples” in usability / NFR | examples exist | **None** — no path required in REF_22; adding path in REF_14_DX would complete traceability. |

**Critical issues:** None.  
**Improvements:** In REF_14_DX and GUIDE_01_USAGE add one line: “Runnable examples: [examples/simple_examples/](../../examples/simple_examples/).” (or equivalent relative path from docs/).

---

## 4. Documentation ↔ Benchmarks

| Aspect | Documentation | Benchmarks | Gap? |
|--------|----------------|------------|------|
| **REF_54_BENCH** | Not present | No dedicated benchmarks/ folder; one script: examples/simple_examples/xwschema_parts_benchmark.py | **Yes** — no REF_54_BENCH; benchmark exists only inside examples. |
| **REF_01_REQ sec. 8** | “Validation and conversion performance; configurable timeouts and limits; advance/performance tests.” | 3.advance/test_performance.py; xwschema_parts_benchmark.py in examples | **Partial** — performance is covered by tests and one example benchmark; no formal benchmark REF or docs/logs/benchmarks/. |
| **REF_51_TEST** | 3.advance: “Handler caching, performance” | test_handler_caching.py, test_performance.py | **None** — test layer matches. |

**Critical issues:** None.  
**Improvements:** Either (a) add REF_54_BENCH stating “No formal SLAs yet; see examples/simple_examples/xwschema_parts_benchmark.py and tests/3.advance/test_performance.py for performance checks,” or (b) add a short “Benchmarks” subsection in REF_51_TEST or REF_22 pointing to that example benchmark and 3.advance performance tests. Option (a) improves traceability with GUIDE_54_BENCH.

---

## 5. Per–GUIDE_35_REVIEW categories (Documentation artifact)

| Category | Finding |
|----------|---------|
| **Critical issues** | None. No wrong placement (all Markdown under docs/ except README); no broken internal REF links found. |
| **Improvements** | (1) REF_51_TEST: document `--advance` (and optionally `--security`, `--performance`). (2) REF_14_DX and GUIDE_01_USAGE: link to `examples/simple_examples/`. (3) Add REF_54_BENCH or a “Benchmarks” note in REF_51/REF_22. |
| **Optimizations** | REF_14_DX, REF_22, REF_01_REQ all mention “examples” in one line; point them to the same path (examples/simple_examples/) to avoid ambiguity. |
| **Missing features / alignment** | Examples path missing from REF_14_DX and GUIDE_01_USAGE; REF_54_BENCH missing; REF_51 “Running tests” missing --advance. |
| **Compliance & standards** | GUIDE_41_DOCS: docs under docs/ ✓. GUIDE_51_TEST: 4-layer layout and REF_51_TEST table ✓. GUIDE_15_API: REF_15_API present and matches __all__ ✓. |
| **Traceability** | REF_01_REQ → REF_22, REF_13, REF_14, REF_15, REF_21, REF_51 ✓. Doc → code ✓. Doc → tests ✓. Doc → examples: add explicit link. Doc → benchmarks: add REF_54_BENCH or equivalent note. |

---

## 6. Recommended next steps (priority order)

1. ~~**REF_14_DX and GUIDE_01_USAGE:** Add “Runnable examples: `examples/simple_examples/`” (with link from docs/).~~ **Done** (07-Feb-2026).
2. ~~**REF_51_TEST:** Add to “Running tests”: `python tests/runner.py --advance` (and optionally `--security`, `--performance`).~~ **Done** (07-Feb-2026).
3. ~~**REF_54_BENCH or benchmarks note:** Add either REF_54_BENCH (short: no SLAs yet; link example benchmark and 3.advance performance tests) or a “Benchmarks” subsection in REF_51_TEST / REF_22.~~ **Done** — REF_54_BENCH.md created and linked in INDEX (07-Feb-2026).

---

## 7. Traceability summary

| From | To | Status |
|------|-----|--------|
| REF_01_REQ | REF_22, REF_13, REF_14, REF_15, REF_21, REF_51 | OK |
| REF_15_API | Code __all__ | OK |
| REF_13_ARCH | Code layout (facade, engine, formats, registry, operations) | OK |
| REF_51_TEST | tests/0.core–3.advance, runner.py | OK (add --advance in doc) |
| REF_14_DX / GUIDE_01_USAGE | examples/simple_examples/ | **Add link** |
| REF_54 or REF_51/REF_22 | Benchmark (example script + 3.advance performance) | **Add REF_54 or note** |

---

*Per GUIDE_35_REVIEW. Evidence: xwschema docs/, src/exonware/xwschema/, tests/, examples/. Related: [REVIEW_20260207_120000_000_REQUIREMENTS.md](REVIEW_20260207_120000_000_REQUIREMENTS.md), [REVIEW_20260207_PROJECT_STATUS.md](REVIEW_20260207_PROJECT_STATUS.md).*
