# Architecture Reference — xwschema

**Library:** exonware-xwschema  
**Last Updated:** 07-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md)

Per REF_01_REQ sec. 7, sec. 6, sec. 5. See REF_22_PROJECT.md for project status.

---

## Overview

xwschema provides schema registry, validation, and format conversion. **xwdata is the base of the engine—use it; do not reimplement or bypass.** Facade and builder expose the public API; engine orchestrates formats, registry, and operations.

---

## Required / forbidden tech (REF_01_REQ sec. 7)

- **Python ≥3.12.** Required: exonware-xwsystem, exonware-xwdata, exonware-xwquery. xwdata is the base of the engine—use it; do not reimplement or bypass. Optional: boto3, requests; dev/lazy/full extras.

---

## Preferred patterns (REF_01_REQ sec. 7)

- **Facade (XWSchema) + engine (XWSchemaEngine):** Single entry for users; engine does load/save via xwdata, validation and generation in-house.
- **Format handlers:** JSON Schema, OpenAPI, Avro, Protobuf, GraphQL, WSDL, XSD, Swagger; pluggable.
- **Validation and conversion pipelines:** Operations layer; strategy for validation/generation.
- **Reuse xwdata** for load/save and $ref resolution; reuse xwsystem for I/O and logging.

**Format serializers (xwsystem):** Schema I/O goes through xwdata. Schema-specific format serializers (e.g. in xwsystem) can extend support; priority order for implementation: JSON Schema (partially supported), Avro, OpenAPI, Protobuf, GraphQL, XSD/WSDL. Format handlers in xwschema are pluggable (SchemaFormat enum, engine registry).

---

## Boundaries

- **Public API:** Facade (XWSchema), builder, config, defs, errors, type_utils (REF_01_REQ sec. 6). Engine, format handler implementations, registry internals, and pipeline implementations are **not** in the public API.
- **Delegation:** xwentity/xwdata for entity-aware validation; xwformats for serialization alignment where relevant.

---

## Scale and performance (REF_01_REQ sec. 7)

- Config: max schema size (e.g. 10 MB), max nesting depth (e.g. 50), timeout. Validation and conversion performance; 4-layer tests including advance/performance.

---

## Multi-language / platform (REF_01_REQ sec. 7)

- Python only for v1. Roadmap: Rust core later (v3); MARS standard in later versions.

---

*See REF_01_REQ.md sec. 5–7. Review: REF_35_REVIEW.md.*
