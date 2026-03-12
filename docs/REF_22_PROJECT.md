# Project Reference — xwschema

**Library:** exonware-xwschema  
**Last Updated:** 20-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md)

Requirements and project status (output of GUIDE_22_PROJECT). Populated from REF_01_REQ.

---

## Vision

**One-sentence purpose (REF_01_REQ sec. 1):** XW schema is a format-agnostic schema format and checker (like xw data is format-agnostic), using xw as the engine for everything.

xwschema provides schema formats and validation for the eXonware ecosystem: JSON Schema, OpenAPI, GraphQL, Protobuf, Avro, WSDL, XSD, Swagger; registry, validation, and format conversion. It supports xwdata, xwaction, and xwentity. **xwdata is the base of the engine—use it; do not reimplement or bypass.** (xwdata docs: [REF_01_REQ](../../xwdata/docs/REF_01_REQ.md), [INDEX](../../xwdata/docs/INDEX.md).)

---

## Goals (REF_01_REQ sec. 1, ordered)

1. **Support xwdata schema check.**
2. **Support parameters check in XW actions.**
3. **Support xwEntity schema features we want.**
4. **Pass all the tests.**

Additional: Multi-format schemas; validation pipeline; format conversion; engine, facade, builder; integration with xwentity, xwdata, xwformats.

---

## Scope and boundaries (REF_01_REQ sec. 2)

| In scope | Out of scope | Dependencies | Anti-goals |
|----------|--------------|--------------|------------|
| v1 = current achieved state. Ensure working; testing 100% complete. | XW data structure or XW actions (not xwschema's job). Reference and lazy in xw data. No new features that reinvent xw data. | XWData, XWSystem, and all that XW data extends. | Do not reimplement or bypass xwdata; xwdata is the base of the engine—use it. |

---

## Success (REF_01_REQ sec. 1)

- **6 mo / 1 yr:** XW schema works with all formats we have; supports xw data, xw action, and xw entity in all the things they want.

---

## Functional Requirements (Summary)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-001 | Schema registry and format support | High | Done |
| FR-002 | Validation pipeline | High | Done |
| FR-003 | Format conversion (schema-to-schema) | Medium | Done |
| FR-004 | Engine, facade, builder API | High | Done |
| FR-005 | 4-layer tests | High | Done |

---

## Non-Functional Requirements (Five Priorities, REF_01_REQ sec. 8)

1. **Security:** Input validation; no code execution from schema data. MARS review when required.
2. **Usability:** Clear API (facade, builder); REF_*, docs, examples; usage guide.
3. **Maintainability:** 4-layer tests (0.core–3.advance); REF_*, logs under docs/; structure: facade, engine, formats, operations, registry.
4. **Performance:** Validation and conversion performance; configurable timeouts and limits; advance/performance tests.
5. **Extensibility:** Pluggable format handlers; SchemaFormat enum and engine extension; versioning/compatibility when needed.

---

## Project Status Overview

- **Current phase:** Alpha (Medium). Engine, formats, registry, operations; 0.core–3.advance.
- **Docs:** REF_01_REQ (source), REF_22_PROJECT (this file), REF_13_ARCH, REF_15_API, REF_35_REVIEW; logs/reviews/.

---

## Milestones (REF_01_REQ sec. 9)

| Milestone | Target | Status |
|-----------|--------|--------|
| M1 — Core registry and formats | v0.x | Done |
| M2 — Validation and conversion | v0.x | Done |
| M3 — REF_* compliance | v0.x | Done |
| v1 — Current state working, 100% tests | Scope-driven | In progress |

**Definition of done (v1):** Existing features working; 100% tests passing; no regressions; docs/REF_* and checklist up to date.

**Roadmap:** v1 production ready (Q1 2026), v2 MARS draft (Q2), v3 Rust core (Q3), v4 MARS implementation (Q4).

### Historical phases (xwschema roadmap)

*Consolidated from PROJECT_PHASES; phased roadmap retained in REF_22.*

- **Version 0 (experimental):** Core schema validation, constraint system, dynamic composition, rich errors, schema evolution, XWAction integration. Status: foundation complete.
- **Version 1 (production):** Production hardening, benchmarks, security audit, CI/CD. Target: Q1 2026.
- **Version 2–4:** MARS draft (Q2), Rust core (Q3), MARS implementation (Q4) — same as roadmap above.

---

## Risks and assumptions (REF_01_REQ sec. 10)

- **Risks:** Circular dependency (use xwdata as engine, don’t reimplement); format coverage (pluggable handlers); large-schema performance (config + tests); drift from xwdata (reuse only).
- **Assumptions:** XWData, XWSystem, XWQuery stable; reference/lazy in xwdata; v1 = current scope.
- **Kill/pivot:** Reimplement or bypass xwdata; v1 cannot be stabilized; MARS/sponsorship forces incompatible direction.

---

## Traceability

- **Requirements source:** [REF_01_REQ.md](REF_01_REQ.md).
- **Compliance:** [REF_11_COMP.md](REF_11_COMP.md) | **Ideas:** [REF_12_IDEA.md](REF_12_IDEA.md) | **DX:** [REF_14_DX.md](REF_14_DX.md) | **API:** [REF_15_API.md](REF_15_API.md) (Schema Catalog, apply_migration) | **Planning:** [REF_21_PLAN.md](REF_21_PLAN.md).
- **Review:** [REF_35_REVIEW.md](REF_35_REVIEW.md), [logs/reviews/](logs/reviews/).
- **Full stack vs PostgreSQL:** xwschema is part of the compared stack; capability comparison and gaps: [../../xwquery/docs/logs/reviews/REVIEW_20260220_165944_014_FULL_STACK_VS_POSTGRES.md](../../xwquery/docs/logs/reviews/REVIEW_20260220_165944_014_FULL_STACK_VS_POSTGRES.md).

---

*See GUIDE_22_PROJECT.md for requirements process.*
