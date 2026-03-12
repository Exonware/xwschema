# Change: MIGRAT feature verification (historical)

**Date:** 2025-01-XX  
**Status:** All MIGRAT features verified in main library  
**Source:** _archive/MIGRAT_FEATURE_VERIFICATION.md (value moved 07-Feb-2026)

---

## Summary

All features from the MIGRAT version (`xwschema/MIGRAT/xwschema/`) were migrated to the main library (`xwschema/src/exonware/xwschema/`). Main library uses XW naming (e.g. `XWSchema`, `XWSchemaEngine`, `XWSchemaBuilder`) and includes: facade, engine, builder, format handlers (JSON Schema, YAML, XSD, TOML, NumPy via registry), config (XWSchemaConfig, ValidationConfig, GenerationConfig, PerformanceConfig), validator (XWSchemaValidator, ValidationIssue), generator (XWSchemaGenerator, from_data), and error classes. Migration complete; no ongoing action.

---

*Per GUIDE_41_DOCS.*
