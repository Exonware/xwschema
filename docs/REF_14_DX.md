# Developer Experience Reference — xwschema (REF_14_DX)

**Library:** exonware-xwschema  
**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 5–6  
**Producing guide:** [GUIDE_14_DX.md](../../docs/guides/GUIDE_14_DX.md)

---

## Purpose

DX contract for xwschema: happy paths, "key code," and ergonomics. Filled from REF_01_REQ.

---

## Key code (1–3 lines)

| Task | Code |
|------|------|
| Create schema and validate | `schema = XWSchema(dict)` then `await schema.validate(data)` |
| Load and validate | `schema = await XWSchema.load(path)` then `await schema.validate(payload)` |
| Generate from data | `schema = await XWSchema.from_data(data)` |
| Convert format | Use engine to convert (e.g. OpenAPI → JSON Schema). |
| Validate XWData or native | `await schema.validate(xwdata_instance)` or `await schema.validate({"key": "value"})` — validator uses XWData path navigation when available, else native validation. |

---

## Developer persona (from REF_01_REQ sec. 5)

Exonware library authors and app developers. Tasks: (1) Create schema from dict or file, validate payload in 1–3 lines. (2) Convert schema format via engine. (3) Use XWSchema.extract_properties / extract_parameters for entity/action integration.

---

## Easy vs advanced

| Easy (1–3 lines) | Advanced |
|------------------|----------|
| XWSchema(dict), await schema.validate(data); await XWSchema.load(path); await XWSchema.from_data(data). | Builder chaining, validate_issues, convert between formats, extract_properties/load_properties, extract_parameters/load_parameters, custom config. |

---

## Main entry points (from REF_01_REQ sec. 6)

- **Facade:** XWSchema
- **Builder:** XWSchemaBuilder
- **Config:** XWSchemaConfig, ValidationConfig, GenerationConfig, PerformanceConfig
- **Types:** SchemaFormat, ValidationMode, SchemaGenerationMode, ConstraintType; ValidationIssue
- **Utilities:** class_to_string, string_to_class, normalize_type, normalize_schema_dict
- **Errors:** XWSchemaError family

---

## Usability expectations (from REF_01_REQ sec. 8)

Clear API (facade, builder); REF_*, docs, examples; PROJECT_PHASES, usage guide. Like xwdata: format-agnostic, facade + engine; reuse xwsystem/xwdata.

**Runnable examples:** [examples/simple_examples/](../examples/simple_examples/) (e.g. `xwschema_dx.py`, `xwschema_examples.py`, `xwschema_parts_benchmark.py`).

---

*See [REF_01_REQ.md](REF_01_REQ.md), [REF_15_API.md](REF_15_API.md), and [REF_21_PLAN.md](REF_21_PLAN.md) for milestones. Per GUIDE_14_DX.*
