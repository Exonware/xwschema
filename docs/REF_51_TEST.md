# xwschema — Test Status and Coverage

**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 8–9, [REF_22_PROJECT.md](REF_22_PROJECT.md)

Test status and coverage (output of GUIDE_51_TEST). Evidence: repo `tests/`, docs/logs/.

---

## Definition of done (REF_01_REQ sec. 9)

First milestone (v1): existing features working; 100% tests passing; no regressions; docs/REF_* up to date. Test expectation: 4-layer suite (0.core–3.advance) in place and passing.

**v1 DoD (current):** All layers 0.core–3.advance passing; no regressions; runner options documented below. Confirm with `python tests/runner.py` (all) or per-layer flags.

---

## Test layers

| Layer | Path | Purpose |
|-------|------|---------|
| 0.core | tests/0.core/ | Facade, builder, engine, validator, generator, schema roundtrip, utilities |
| 1.unit | tests/1.unit/ | Config, formats, format conversion, base formats |
| 2.integration | tests/2.integration/ | End-to-end |
| 3.advance | tests/3.advance/ | Handler caching, performance |

---

## Running tests

```bash
python tests/runner.py
python tests/runner.py --core
python tests/runner.py --unit
python tests/runner.py --integration
python tests/runner.py --advance
python tests/runner.py --security    # security-focused tests
python tests/runner.py --performance # performance-focused tests
```

---

## Traceability

- **Requirements:** REF_01_REQ sec. 8 (maintainability, 4-layer tests); REF_22.
- **Evidence:** [logs/reviews/](logs/reviews/), [logs/tests/](logs/tests/) (TEST_* run summaries).

**Test output and cache:** The main runner writes to `docs/logs/tests/TEST_<timestamp>_SUMMARY.md`. Pytest cache (`.pytest_cache`) must not live under docs; ensure it is in `.gitignore` and not committed.

---

*Per GUIDE_00_MASTER and GUIDE_51_TEST.*
