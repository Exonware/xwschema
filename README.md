# xwschema

**Schema validation and data structure definition.** Define, validate, and evolve schemas with constraints, dynamic composition, and performance-optimized validation. Integrates with xwaction and the eXonware stack. Per project docs.

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com  
**Version:** See [version.py](src/exonware/xwschema/version.py) or PyPI. · **Updated:** See [version.py](src/exonware/xwschema/version.py) (`__date__`)

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org)
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

# Define and validate schemas; use with xwaction for workflow validation
# See docs/ and REF_* for full API and examples
```

See [docs/](docs/) for usage, REF_*, and GUIDE_01_USAGE when present.

---

## What you get

| Area | What's in it |
|------|----------------|
| **Validation** | Constraint-based validation, rich error reporting. |
| **Schema** | Dynamic composition, evolution, versioning. |
| **Schema Catalog** | DDL-like API (create_schema, alter_schema, drop_schema) and **apply_migration** for schema evolution; JSON-backed catalog for schema-on-write with xwstorage/XWDB. See [docs/REF_15_API.md](docs/REF_15_API.md). |
| **Integration** | xwaction workflow validation; eXonware ecosystem. |

Current phase and status: see [docs/REF_22_PROJECT.md](docs/REF_22_PROJECT.md) or [docs/](docs/) when present.

---

## Docs and tests

- **Start:** [docs/INDEX.md](docs/INDEX.md) or [docs/](docs/).
- **Tests:** Run from project root per project layout.

---

## License and links

MIT — see [LICENSE](LICENSE). **Homepage:** https://exonware.com · **Repository:** https://github.com/exonware/xwschema  

Contributing → CONTRIBUTING.md · Security → SECURITY.md (when present).

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
