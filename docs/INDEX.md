# Documentation index — xwschema

**Last Updated:** 07-Feb-2026

Navigation hub for xwschema docs. Per GUIDE_41_DOCS and GUIDE_00_MASTER.

## Requirements (source of truth)

| Document | Purpose | Producing guide |
|----------|---------|------------------|
| [REF_01_REQ.md](REF_01_REQ.md) | **Requirements source** (vision, scope, NFRs, API); feeds REF_11, REF_12, REF_13, REF_14, REF_15, REF_21, REF_22 | GUIDE_01_REQ |

## References (REF_*)

| Document | Purpose | Producing guide |
|----------|---------|------------------|
| [REF_11_COMP.md](REF_11_COMP.md) | Compliance stance and standards (from REF_01_REQ sec. 4) | GUIDE_11_COMP |
| [REF_12_IDEA.md](REF_12_IDEA.md) | Idea context and evaluation (from REF_01_REQ sec. 1–2) | GUIDE_12_IDEA |
| [REF_13_ARCH.md](REF_13_ARCH.md) | Architecture (from REF_01_REQ sec. 7) | GUIDE_13_ARCH |
| [REF_14_DX.md](REF_14_DX.md) | Developer experience, happy paths (from REF_01_REQ sec. 5–6) | GUIDE_14_DX |
| [REF_15_API.md](REF_15_API.md) | API reference (from REF_01_REQ sec. 6) | GUIDE_15_API |
| [REF_21_PLAN.md](REF_21_PLAN.md) | Milestones and roadmap (from REF_01_REQ sec. 9) | GUIDE_21_PLAN |
| [REF_22_PROJECT.md](REF_22_PROJECT.md) | Vision, requirements, milestones (from REF_01_REQ) | GUIDE_22_PROJECT |
| [REF_35_REVIEW.md](REF_35_REVIEW.md) | Review summary and status | GUIDE_35_REVIEW |
| [REF_51_TEST.md](REF_51_TEST.md) | Test status and coverage (from REF_01_REQ sec. 8) | GUIDE_51_TEST |
| [REF_54_BENCH.md](REF_54_BENCH.md) | Benchmarks and performance (from REF_01_REQ sec. 8; example + 3.advance) | GUIDE_54_BENCH |

## Usage

| Document | Purpose |
|----------|---------|
| [GUIDE_01_USAGE.md](GUIDE_01_USAGE.md) | How to use xwschema (GUIDE_41_DOCS) |

## Evidence (logs)

| Location | Content |
|----------|---------|
| [logs/reviews/](logs/reviews/) | REVIEW_* (GUIDE_35_REVIEW); REF_01 alignment, MIGRAT verification, etc. |
| [logs/tests/](logs/tests/) | TEST_* (test run summaries); runner writes here. See [REF_51_TEST.md](REF_51_TEST.md). |
| [logs/benchmarks/](logs/benchmarks/) | BENCH_* (benchmark run evidence). See [REF_54_BENCH.md](REF_54_BENCH.md). |

## Other

| Path | Purpose |
|------|---------|
| [_archive/](_archive/) | Empty; value moved to REFs and logs (see [changes/CHANGE_20260208_ARCHIVE_MIGRATION_TO_REFS_AND_LOGS.md](changes/CHANGE_20260208_ARCHIVE_MIGRATION_TO_REFS_AND_LOGS.md)). |
| [changes/](changes/) | CHANGE_* (implementation change notes) |
| [Examples](../examples/simple_examples/) | Runnable examples (e.g. xwschema_dx.py, xwschema_parts_benchmark.py) — see REF_14_DX, REF_54_BENCH |
| Benchmarks | [logs/benchmarks/](logs/benchmarks/); example script: [examples/simple_examples/xwschema_parts_benchmark.py](../examples/simple_examples/xwschema_parts_benchmark.py); tests: [tests/3.advance/](../tests/3.advance/). See [REF_54_BENCH.md](REF_54_BENCH.md). |

---

*Per GUIDE_00_MASTER and GUIDE_41_DOCS.*
