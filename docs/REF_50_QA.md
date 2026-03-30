# QA Reference — xwschema

**Library:** exonware-xwschema  
**Version:** See [`src/exonware/xwschema/version.py`](../src/exonware/xwschema/version.py) (`__version__`; single source of truth).  
**Last Updated:** Synchronized with `version.get_date()` from that module at doc review time.  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 8 (Five Priorities)

---

## Purpose

Single source of truth for **xwschema** quality gates and release readiness (GUIDE_50_QA / GUIDE_00_MASTER).

---

## Readiness state (Go / No-Go)

| Gate | Requirement | Status | Evidence |
|------|-------------|--------|----------|
| Tests | All layers pass (0.core, 1.unit, 2.integration, 3.advance) | ⏳ | `docs/logs/tests/INDEX.md` |
| Coverage | Overall ≥ 90% and core critical paths 100% | ⏳ | `REF_51_TEST.md` |
| Lint/Types | Formatting + type checks pass | ⏳ | CI / local `black`, `isort`, `mypy` |
| Security | Security suites pass; no known critical vulnerabilities | ⏳ | `docs/logs/tests/INDEX.md` + compliance evidence |
| Performance | Benchmarks meet SLA; no regressions (>5% investigate; >10% block) | ⏳ | `benchmarks/` (project root per GUIDE_54_BENCH) + `REF_54_BENCH.md`; legacy: `docs/logs/benchmarks/` |
| Docs | Required REFs exist and are current (REF_*, logs indices, usage) | ⏳ | `docs/INDEX.md` |

**Decision:** ⏳ Pending (blocked until gates are green)

---

## Quality gates (canonical)

### Gate 1 — Test execution
- No skipped/rigged tests
- Evidence under `docs/logs/tests/` when using the hierarchical runner

### Gate 2 — Coverage
- Target: ≥ 90% overall (per GUIDE_50_QA / project policy)

### Gate 3 — Code quality
- Lint and type-check clean per `pyproject.toml` tool config

### Gate 4 — Performance
- Benchmarks run per `REF_54_BENCH.md` when performance changes

### Gate 5 — Security
- Input validation and dependency posture per REF_11_COMP / REF_01_REQ

### Gate 6 — Optional `[full]` extra
- `[full]` pulls many optional third-party packages; treat as **opt-in** and audit for supply-chain and platform compatibility before production use.

---

## Required evidence locations

- Tests: `docs/logs/tests/TEST_*.md` + `docs/logs/tests/INDEX.md`
- Benchmarks: `benchmarks/` at project root (canonical) + `REF_54_BENCH.md`; legacy index may exist under `docs/logs/benchmarks/`
- Releases: `docs/logs/releases/` + index (when used)

**Release checklist:** Gates above define go/no-go. Update this table when evidence moves from ⏳ to ✅.
