# xwschema

**Define once, validate everywhere.**  
`xwschema` lets you describe schema rules and validate data across different input formats and structures with one consistent validation layer.

You can take schema definitions from common formats (for example JSON-style or XML-style representations), then validate heterogeneous payloads and models without rewriting validation logic per format.

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com  

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Install

```bash
pip install exonware-xwschema
```

---

## Quick start

```python
from exonware.xwschema import *

# Define and validate schemas; pair with xwaction for workflow validation
# See docs/ and REF_* for API and examples
```

See [docs/](docs/) for usage, REF_*, and GUIDE_01_USAGE when present.

---

## Why developers use xwschema

- **Schema portability** - keep business validation rules stable while data formats vary.
- **Cross-format validation** - validate different payload styles through one schema engine.
- **Extensible model surface** - grow new format adapters and schema types without redesigning core validation.
- **Works with your stack** - use standalone or pair with xwaction/xwdata workflows.

---

## What you get

| Area | Contents |
|------|----------|
| **Validation** | Constraint checks and structured errors. |
| **Schema** | Dynamic composition, evolution, versioning. |
| **Schema catalog** | DDL-style helpers (`create_schema`, `alter_schema`, `drop_schema`) and **apply_migration** for evolution; JSON-backed catalog for schema-on-write with xwstorage/XWDB. See [docs/REF_15_API.md](docs/REF_15_API.md). |
| **Integration** | xwaction workflows and other eXonware packages. |

Current phase: [docs/REF_22_PROJECT.md](docs/REF_22_PROJECT.md) or [docs/](docs/).

---

## Docs and tests

- **Start:** [docs/INDEX.md](docs/INDEX.md) or [docs/](docs/).
- **Tests:** From repo root per project layout.

---

## License and links

MIT - see [LICENSE](LICENSE). **Homepage:** https://exonware.com · **Repository:** https://github.com/exonware/xwschema  

## Async Support

<!-- async-support:start -->
- xwschema includes asynchronous execution paths in production code.
- Source validation: 79 async def definitions and 64 await usages under src/.
- Use async APIs for I/O-heavy or concurrent workloads to improve throughput and responsiveness.
<!-- async-support:end -->
Version: 0.4.0.6 | Updated: 31-Mar-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
