# xwschema

Schema validation and structure definitions: constraints, composition, evolution, and fast paths where implemented. Works with xwaction and the wider eXonware stack. Full detail is in project REF docs.

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
Version: 0.4.0.4 | Updated: 30-Mar-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
