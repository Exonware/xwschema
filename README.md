# xwschema

**Define once, validate everywhere.**  
`xwschema` lets you describe schema rules and validate data across different input formats and structures with one consistent validation layer.

You can take schema definitions from common formats (for example JSON-style or XML-style representations), then validate heterogeneous payloads and models without rewriting validation logic per format.

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com  

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

---

## 📦 Install

```bash
pip install exonware-xwschema
pip install exonware-xwschema[lazy]
pip install exonware-xwschema[full]
```

---

## 🚀 Quick start

```python
from exonware.xwschema import *

# Define and validate schemas; pair with xwaction for workflow validation
# See docs/ and REF_* for API and examples
```

See [docs/](docs/) for usage, REF_*, and GUIDE_01_USAGE when present.

---

## 🎯 Why developers use xwschema

- **Schema portability** - keep business validation rules stable while data formats vary.
- **Cross-format validation** - validate different payload styles through one schema engine.
- **Extensible model surface** - grow new format adapters and schema types without redesigning core validation.
- **Works with your stack** - use standalone or pair with xwaction/xwdata workflows.

---

## ✨ What you get

| Area | Contents |
|------|----------|
| **Validation** | Constraint checks and structured errors. |
| **Schema** | Dynamic composition, evolution, versioning. |
| **Schema catalog** | DDL-style helpers (`create_schema`, `alter_schema`, `drop_schema`) and **apply_migration** for evolution; JSON-backed catalog for schema-on-write with xwstorage/XWDB. See [docs/REF_15_API.md](docs/REF_15_API.md). |
| **Integration** | xwaction workflows and other eXonware packages. |

Current phase: [docs/REF_22_PROJECT.md](docs/REF_22_PROJECT.md) or [docs/](docs/).

---

## 🌐 Ecosystem functional contributions

`xwschema` provides validation contracts; sibling libs define where those contracts are applied in real systems.
You can use `xwschema` standalone for schema definition and validation in any Python project.
Integrating with the wider XW platform is optional and most useful for enterprise and mission-critical environments where validation must stay consistent across self-managed services.

| Supporting XW lib | What it provides to xwschema usage | Functional requirement it satisfies |
|------|----------------|----------------|
| **XWAction** | Action input/output validation hooks tied to schema definitions. | Contract-safe automation and endpoint execution. |
| **XWEntity** | Entity model contracts bound to schema rules. | Domain model correctness and controlled schema evolution. |
| **XWData** | Format-agnostic data ingestion where schemas validate transformed payloads. | Cross-format validation without rewriting rule logic per format. |
| **XWStorage** | Schema catalog/migration integration for persisted data systems. | Schema-on-write and migration governance for storage-backed workloads. |
| **XWSystem** | Core runtime/error utility layer for validators and schema tooling. | Consistent validation behavior and diagnostics across stack packages. |
| **XWAPI / XWAuth** | Request, response, and policy-rule validation at API/auth boundaries. | Safer public interfaces and security policy correctness. |

Competitive edge: schema rules become a reusable platform contract across APIs, storage, entities, and workflows instead of living as isolated validators in each service.

---

## 📖 Docs and tests

- **Start:** [docs/INDEX.md](docs/INDEX.md) or [docs/](docs/).
- **Tests:** From repo root per project layout.

---

## 📜 License and links

Apache-2.0 - see [LICENSE](LICENSE). **Homepage:** https://exonware.com · **Repository:** https://github.com/exonware/xwschema  

## ⏱️ Async Support

<!-- async-support:start -->
- xwschema includes asynchronous execution paths in production code.
- Source validation: 79 async def definitions and 64 await usages under src/.
- Use async APIs for I/O-heavy or concurrent workloads to improve throughput and responsiveness.
<!-- async-support:end -->
Version: 0.4.0.11 | Updated: 11-Apr-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
