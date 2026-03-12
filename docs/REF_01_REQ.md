# Requirements Reference (REF_01_REQ)

**Project:** xwschema  
**Sponsor:** ExonWare (same as other projects; final say on scope and priorities)  
**Version:** 0.0.1  
**Last Updated:** 07-Feb-2026 (Batch 3: reverse-engineered from codebase)  
**Produced by:** [GUIDE_01_REQ.md](../../docs/guides/GUIDE_01_REQ.md)

---

## Purpose of This Document

This document is the **single source of raw and refined requirements** collected from the project sponsor and stakeholders. It is updated on every requirements-gathering run. When the **Clarity Checklist** (section 12) reaches the agreed threshold, use this content to fill REF_11_COMP, REF_12_IDEA, REF_22_PROJECT, REF_13_ARCH, REF_14_DX, REF_15_API, and REF_21_PLAN (planning artifacts). Template structure: [GUIDE_01_REQ.md](../../docs/guides/GUIDE_01_REQ.md).

---

## 1. Vision and Goals

| Field | Content |
|-------|---------|
| One-sentence purpose | XW schema is a format-agnostic schema format and checker (like xw data is format-agnostic), using xw as the engine for everything. |
| Primary users/beneficiaries | XMD data (avoid circular referencing); developers using XWData, XW action, XW entity; developers using almost any of the advanced libraries will use XW schema. |
| Success (6 mo / 1 yr) | XW schema works with all the formats we have; supports xw data in all the things it wants; supports xw action in all the things it wants; supports xw entity in all the things it wants. |
| Top 3–5 goals (ordered) | (1) Support xwdata schema check. (2) Support parameters check in XW actions. (3) Support xwEntity schema features we want. (4) Pass all the tests. |
| Problem statement | We don't want to create a new schema checker or new schema for every new data type; we can reuse XW schema for that—it's extremely flexible and powerful. |

## 2. Scope and Boundaries

| In scope | Out of scope | Dependencies | Anti-goals |
|----------|--------------|--------------|------------|
| v1 = whatever we have achieved so far. Ensure it's working; testing 100% complete. | XW data structure or XW actions (not xwschema's job). Reference and lazy assumed implemented in xw data. No new "fascinating" features in xwschema—must reuse xw data features, not reinvent the wheel. | XWData, XWSystem, and all things that XW data extends. | Do not reimplement or bypass xwdata; xwdata is the base of the engine—use it. |

## 3. Stakeholders and Sponsor

| Sponsor (name, role, final say) | Main stakeholders | External customers/partners | Doc consumers |
|----------------------------------|-------------------|-----------------------------|---------------|
| ExonWare (same as other projects) | Developers; product uses of the advanced libraries | For now no external users; maybe in the future support a Python sponsorship and showcase this library. | Mostly developers and other users. |

## 4. Compliance and Standards

| Regulatory/standards | Security & privacy | Certifications/evidence |
|----------------------|--------------------|--------------------------|
| For now no standard in mind; this version stays like that. Developed with highest standards in mind; will review once we reach a version that requires the MARS standard. | Same as above—no specific requirements for this version; will review when MARS standard is required. | Same—none for this version; will review when MARS standard is required. |

## 5. Product and User Experience

| Main user journeys/use cases | Developer persona & 1–3 line tasks | Usability/accessibility | UX/DX benchmarks |
|-----------------------------|------------------------------------|--------------------------|------------------|
| (Reverse-engineered from codebase.) (1) Load schema from dict/path/XWData and validate data. (2) Generate schema from data (from_data). (3) Convert between schema formats (JSON Schema, OpenAPI, Avro, Protobuf, GraphQL, WSDL, XSD, Swagger). (4) Validate with strict/lax/fast/detailed modes; get issues list. (5) Extract/load properties from classes (xwentity-style); extract/load parameters from callables (xwaction param check). (6) Use builder for fluent schema construction. (7) Use engine/facade for async load, save, validate, convert. | Developer: exonware library authors and app developers. Tasks: (1) Create schema from dict or file, validate payload in 1–3 lines. (2) Convert schema format (e.g. OpenAPI → JSON Schema) via engine. (3) Use XWSchema.extract_properties / extract_parameters for entity/action integration. | Clear errors (ValidationIssue, XWSchema*Error hierarchy); config for validation/generation/performance; docs (README, REF_*, GUIDE_01_USAGE). | Like xwdata: format-agnostic, facade + engine; reuse xwsystem/xwdata; no manual I/O in xwschema. |

## 6. API and Surface Area

| Main entry points / "key code" | Easy (1–3 lines) vs advanced | Integration/existing APIs | Not in public API |
|--------------------------------|------------------------------|---------------------------|-------------------|
| (From codebase.) XWSchema (facade), XWSchemaBuilder, XWSchemaConfig + ValidationConfig/GenerationConfig/PerformanceConfig; SchemaFormat, ValidationMode, SchemaGenerationMode, ConstraintType; ValidationIssue; class_to_string, string_to_class, normalize_type, normalize_schema_dict; XWSchemaError family. Engine used internally; format handlers and operations are internal. | Easy: XWSchema(dict), await schema.validate(data); await XWSchema.load(path); await XWSchema.from_data(data). Advanced: builder chaining, validate_issues, convert between formats, extract_properties/load_properties, extract_parameters/load_parameters, custom config. | xwsystem (logging, I/O, XWObject); xwdata (load/save, path-based schema—base of the engine); xwquery for schema query; entry-point "xwsystem.schema_validators" for xwsystem consumers. | Internal: engine, format handler implementations, registry internals, pipeline implementations. Only facade/builder/config/defs/errors/type_utils in __all__. |

## 7. Architecture and Technology

| Required/forbidden tech | Preferred patterns | Scale & performance | Multi-language/platform |
|-------------------------|--------------------|----------------------|-------------------------|
| Python ≥3.12. Required: exonware-xwsystem, exonware-xwdata, exonware-xwquery. xwdata is the base of the engine—use it; do not reimplement or bypass. Optional: boto3, requests; dev/lazy/full extras. | Facade (XWSchema) + engine (XWSchemaEngine); format handlers (JSON Schema, OpenAPI, Avro, Protobuf, GraphQL, WSDL, XSD, Swagger); validation pipeline and conversion pipeline; strategy for validation/generation; reuse xwdata for load/save and $ref resolution. | Config: max schema size (e.g. 10 MB), max nesting depth (e.g. 50), timeout; validation/generation performance; 4-layer tests including advance/performance. | Python only for v1. README roadmap: Rust core later (v3); MARS standard in later versions. |

## 8. Non-Functional Requirements (Five Priorities)

| Security | Usability | Maintainability | Performance | Extensibility |
|----------|-----------|-----------------|-------------|---------------|
| Input validation; no code execution from schema data (per REF_22). Same as ecosystem; MARS review when required. | Clear API (facade, builder); REF_*, docs, examples; PROJECT_PHASES, usage guide. | 4-layer tests (0.core–3.advance); REF_*, logs under docs/; structure: facade, engine, formats, operations, registry. | Validation and conversion performance; configurable timeouts and limits; advance/performance tests. | Pluggable format handlers; SchemaFormat enum and engine extension; versioning/compatibility when needed. |

## 9. Milestones and Timeline

| Major milestones | Definition of done (first) | Fixed vs flexible |
|------------------|----------------------------|-------------------|
| (From codebase/REF_22.) M1 — Core registry and formats (done). M2 — Validation and conversion (done). M3 — REF_* compliance (done). v1 — Current state: all working, testing 100% complete (per sponsor). Roadmap: v1 production ready (Q1 2026), v2 MARS draft (Q2), v3 Rust core (Q3), v4 MARS implementation (Q4). | First milestone (v1): existing features working; 100% tests passing; no regressions; docs/REF_* and checklist up to date. | Scope-driven for v1 (what we have); dates flexible per roadmap; MARS and Rust are future phases. |

## 10. Risks and Assumptions

| Top risks | Assumptions | Kill/pivot criteria |
|-----------|-------------|----------------------|
| (Reverse-engineered.) (1) Circular dependency with xwdata/xwentity/xwaction—mitigation: use xwdata as engine base, do not reimplement or bypass. (2) Format handler coverage vs ecosystem needs—mitigation: pluggable handlers; align with xwformats where relevant. (3) Performance on large schemas—mitigation: config limits, performance tests. (4) Drift from xwdata contract—mitigation: reuse xwdata, no reimplement. | XWData, XWSystem, XWQuery available and stable; reference/lazy in xwdata; developers use facade/builder and not internals; v1 = current achieved scope; tests define expected behavior. | If we reimplement or bypass xwdata (anti-goal); if v1 cannot be stabilized with 100% tests; if MARS or external sponsorship forces incompatible direction (then revisit scope). |

## 11. Workshop / Session Log (Optional)

| Date | Type | Participants | Outcomes |
|------|------|---------------|----------|
| 07-Feb-2026 | Batch 1 — Vision and scope | Sponsor | Sections 1–2 filled; clarity 1–5 confirmed. |
| 07-Feb-2026 | Batch 2 — Stakeholders and compliance | Sponsor | Sections 3–4 filled; clarity 6–7 confirmed. |
| 07-Feb-2026 | Batch 3 — Product, API, arch, NFRs, milestones, risks | Sponsor | Sections 5–10 filled from reverse-engineered codebase; clarity 8–14 confirmed. |
| 07-Feb-2026 | Direction update (PROMPT_01_REQ_03_UPDATE) | — | Review and implementation plan produced. Informed by report: REVIEW_20260207_PROJECT_STATUS.md; REF_35_REVIEW.md. |
| 07-Feb-2026 | Sponsor clarification: xwdata | Sponsor | Anti-goal corrected: use xwdata—it is the base of the engine. Anti-goal = do not reimplement or bypass xwdata. |
| 07-Feb-2026 | Downstream docs refreshed | — | REF_22_PROJECT, REF_13_ARCH, REF_15_API, REF_35_REVIEW populated from REF_01_REQ; sec. 7/sec. 10 wording aligned with xwdata-as-engine. |
| 07-Feb-2026 | Cont downstream (GUIDE_01_USAGE, REF_51, README) | Agent | GUIDE_01_USAGE expanded (quick start, REF links); REF_51_TEST expanded (DoD, layers, Running tests); README docs section added Requirements & REFs block; PROJECT_PHASES link fixed. |

## 12. Clarity Checklist

| # | Criterion | ☐ |
|---|-----------|---|
| 1 | Vision and one-sentence purpose filled and confirmed | ☑ |
| 2 | Primary users and success criteria defined | ☑ |
| 3 | Top 3–5 goals listed and ordered | ☑ |
| 4 | In-scope and out-of-scope clear | ☑ |
| 5 | Dependencies and anti-goals documented | ☑ |
| 6 | Sponsor and main stakeholders identified | ☑ |
| 7 | Compliance/standards stated or deferred | ☑ |
| 8 | Main user journeys / use cases listed | ☑ |
| 9 | API / "key code" expectations captured | ☑ |
| 10 | Architecture/technology constraints captured | ☑ |
| 11 | NFRs (Five Priorities) addressed | ☑ |
| 12 | Milestones and DoD for first milestone set | ☑ |
| 13 | Top risks and assumptions documented | ☑ |
| 14 | Sponsor confirmed vision, scope, priorities | ☑ |

**Clarity score:** 14 / 14. **Ready to fill downstream docs?** ☑ Yes

---

## Traceability (downstream REFs)

- **REF_11_COMP:** [REF_11_COMP.md](REF_11_COMP.md) — Compliance stance (sec. 4)
- **REF_12_IDEA:** [REF_12_IDEA.md](REF_12_IDEA.md) — Idea context (sec. 1–2)
- **REF_22_PROJECT:** [REF_22_PROJECT.md](REF_22_PROJECT.md) — Vision, FR/NFR, milestones
- **REF_13_ARCH:** [REF_13_ARCH.md](REF_13_ARCH.md) — Architecture (sec. 7)
- **REF_14_DX:** [REF_14_DX.md](REF_14_DX.md) — Developer experience (sec. 5–6)
- **REF_15_API:** [REF_15_API.md](REF_15_API.md) — API reference (sec. 6)
- **REF_21_PLAN:** [REF_21_PLAN.md](REF_21_PLAN.md) — Milestones and roadmap (sec. 9)

---

*Per GUIDE_01_REQ. Collect thoroughly, then feed downstream REFs.*
