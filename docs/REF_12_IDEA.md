# Idea Reference — xwschema (REF_12_IDEA)

**Library:** exonware-xwschema  
**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) (GUIDE_01_REQ)  
**Producing guide:** [GUIDE_12_IDEA.md](../../docs/guides/GUIDE_12_IDEA.md)

---

## Purpose

Idea context and evaluation for xwschema, filled from REF_01_REQ. Used for traceability from idea → requirements → project.

---

## Core Idea (from REF_01_REQ sec. 1–2)

| Field | Content |
|-------|---------|
| **Problem statement** | We don't want to create a new schema checker or new schema for every new data type; we can reuse XW schema for that—it's extremely flexible and powerful. |
| **Solution direction** | XW schema is a format-agnostic schema format and checker (like xw data is format-agnostic), using xw as the engine for everything. |
| **One-sentence purpose** | XW schema is a format-agnostic schema format and checker (like xw data is format-agnostic), using xw as the engine for everything. |
| **Primary beneficiaries** | XMD data (avoid circular referencing); developers using XWData, XW action, XW entity; developers using almost any of the advanced libraries. |
| **Top goals (ordered)** | (1) Support xwdata schema check. (2) Support parameters check in XW actions. (3) Support xwEntity schema features we want. (4) Pass all the tests. |
| **Out of scope** | XW data structure or XW actions (not xwschema's job). Reference and lazy assumed in xw data. No new features that reinvent xw data. Do not reimplement or bypass xwdata. |

---

## Evaluation

| Criterion | Assessment |
|-----------|------------|
| **Status** | Approved (implemented; REF_01_REQ clarity 14/14). |
| **Five Priorities** | Addressed in REF_01_REQ sec. 8 (security, usability, maintainability, performance, extensibility). |
| **Traceability** | REF_01_REQ → REF_22_PROJECT, REF_13_ARCH, REF_14_DX, REF_15_API, REF_21_PLAN. |

---

## Ideas (future)

| Idea | Description | Status |
|------|-------------|--------|
| **xwsyntax integration** | Optional dependency: use xwsyntax grammars for schema file parsing (Protobuf, Avro, GraphQL); format conversion via AST; unified syntax + semantic validation; IDE integration (LSP, Monaco). xwsyntax = syntax, xwschema = semantics. | Planning; see REF_22 roadmap. |

---

*See REF_01_REQ.md for full requirements. See REF_22_PROJECT.md for project status. **Consumers:** xwdata, xwaction, xwentity, xwstorage, xwquery — see [REF_22_PROJECT](REF_22_PROJECT.md) traceability.*
