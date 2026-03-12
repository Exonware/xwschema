# Change: Archive migration — value to REFs and logs, redundant files removed

**Date:** 08-Feb-2026  
**Type:** Documentation  
**Scope:** xwschema docs/_archive, docs/changes, docs/logs

---

## Summary

All archived and non-standard docs were reviewed; value was merged into REF_* or captured in logs (REVIEW_*, BENCH_*, TEST_*). Redundant files were then removed so that only standard docs (REF_*, INDEX, GUIDE_*, CHANGE_*, logs subdirs) remain per GUIDE_41_DOCS.

---

## Value extraction (where content went)

| Source (deleted or from _archive) | Value moved to |
|-----------------------------------|----------------|
| INSTALL_DEPENDENCIES.md | GUIDE_01_USAGE.md sec.  Install + Verification (full verification commands). |
| MIGRAT_FEATURE_VERIFICATION.md | logs/reviews/REVIEW_20250100_000000_000_MIGRAT_MIGRATION_VERIFICATION.md (verification summary). |
| PROJECT_PHASES.md | REF_22_PROJECT.md sec.  Historical phases (already present; confirmed). |
| README_PYTEST_CACHE_MISPLACED.md | REF_51_TEST.md (test output path + pytest cache must not be in docs). |
| changes/SCHEMA_FORMATS_NEEDED.md | REF_13_ARCH.md sec.  Format serializers (priority, xwdata path). |
| changes/VALIDATION_VERIFICATION.md | REF_15_API.md sec.  Validation: dual support; REF_14_DX.md (validate XWData/native row). |
| changes/XWSYNTAX_INTEGRATION.md | REF_12_IDEA.md sec.  Ideas (future) — xwsyntax integration. |
| logs/performance_summary.md | logs/benchmarks/BENCH_20251217_000000_000_LEGACY_FORMATS_SUMMARY.md + REF_54_BENCH. |
| logs/version_comparison_summary.md | Same BENCH_* (consolidated). |
| logs/runner_out.md | logs/tests/TEST_20251217_194056_000_CORE_LAYER_RUN.md (historical run). |
| docs/tests/TEST_20260208_*.md | Moved to docs/logs/tests/ (canonical location); runner updated to write to docs/logs/tests/. |

---

## New or updated artifacts

- **logs/reviews/:** REVIEW_20250100_000000_000_MIGRAT_MIGRATION_VERIFICATION.md (new).
- **logs/benchmarks/:** BENCH_20251217_000000_000_LEGACY_FORMATS_SUMMARY.md, INDEX.md (new).
- **logs/tests/:** TEST_20251217_194056_000_CORE_LAYER_RUN.md, INDEX.md (new).
- **REF_12_IDEA:** Ideas (future) — xwsyntax integration.
- **REF_13_ARCH:** Format serializers (xwsystem).
- **REF_14_DX:** Validate XWData or native row.
- **REF_15_API:** Validation: dual support.
- **REF_51_TEST:** Evidence logs/tests; test output path; pytest cache note.
- **REF_54_BENCH:** Run evidence logs/benchmarks.
- **GUIDE_01_USAGE:** Verification commands (no _archive link).
- **INDEX.md:** Evidence table includes logs/reviews, logs/tests, logs/benchmarks; _archive removed from Other.

---

## Files removed

- docs/_archive/INSTALL_DEPENDENCIES.md
- docs/_archive/MIGRAT_FEATURE_VERIFICATION.md
- docs/_archive/PROJECT_PHASES.md
- docs/_archive/README_PYTEST_CACHE_MISPLACED.md
- docs/changes/SCHEMA_FORMATS_NEEDED.md
- docs/changes/VALIDATION_VERIFICATION.md
- docs/changes/XWSYNTAX_INTEGRATION.md
- docs/logs/performance_summary.md
- docs/logs/runner_out.md
- docs/logs/version_comparison_summary.md
- docs/logs/ARCHIVE_VALUE_CAPTURE_XWSCHEMA.md (redundant with this change)

**Runner:** tests/runner.py now writes to docs/logs/tests/ (was docs/tests/).

---

*Per GUIDE_41_DOCS; single source of truth in REF_* and logs.*
