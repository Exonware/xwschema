# xwschema — Usage Guide

**Last Updated:** 07-Feb-2026

How to use xwschema (output of GUIDE_41_DOCS). See [REF_01_REQ.md](REF_01_REQ.md), [REF_22_PROJECT.md](REF_22_PROJECT.md), [REF_14_DX.md](REF_14_DX.md) (key code), [REF_15_API.md](REF_15_API.md), [REF_13_ARCH.md](REF_13_ARCH.md), [REF_21_PLAN.md](REF_21_PLAN.md) (milestones). Full set: [INDEX.md](INDEX.md).

**Runnable examples:** [examples/simple_examples/](../examples/simple_examples/).

---

## Install

**Dependencies:** exonware-xwsystem, exonware-xwdata (and exonware-xwquery per pyproject.toml).

```bash
pip install -r requirements.txt
# or development:
pip install -e .
```

**Verification:** Run from xwschema directory: `python -c "from exonware.xwschema import XWSchema; print('OK')"` and `python -c "from exonware.xwschema.operations.format_conversion import SchemaFormatConverter; print('OK')"`.

---

## Quick start (REF_01_REQ sec. 5–6)

Format-agnostic schema: create from dict or load, validate data, optionally generate schema from data or convert between formats.

```python
from exonware.xwschema import XWSchema

# From dict
schema = XWSchema({"type": "object", "properties": {"name": {"type": "string"}}})

# Validate (async)
import asyncio
result = asyncio.run(schema.validate({"name": "Alice"}))

# Load from path, validate
# data = await XWSchema.load("schema.json")
# await schema.from_data(data)  # generate schema from data
```

---

## Easy vs advanced (REF_15_API)

- **Easy:** `XWSchema(dict)`, `await schema.validate(data)`, `await XWSchema.load(path)`, `await XWSchema.from_data(data)`.
- **Advanced:** Builder, `validate_issues`, format conversion (JSON Schema, OpenAPI, Avro, etc.), `extract_properties`/`extract_parameters` for entity/action integration, custom config. See [REF_15_API.md](REF_15_API.md) and [REF_01_REQ.md](REF_01_REQ.md) sec. 6.

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [REF_01_REQ.md](REF_01_REQ.md) | Requirements (vision, scope, API expectations) |
| [REF_12_IDEA.md](REF_12_IDEA.md) | Idea context and evaluation |
| [REF_22_PROJECT.md](REF_22_PROJECT.md) | Project vision, goals, FR/NFR, milestones |
| [REF_13_ARCH.md](REF_13_ARCH.md) | Architecture and boundaries (xwdata as engine base) |
| [REF_14_DX.md](REF_14_DX.md) | Developer experience and key code |
| [REF_15_API.md](REF_15_API.md) | Public API reference |
| [REF_21_PLAN.md](REF_21_PLAN.md) | Milestones and roadmap |
| [INDEX.md](INDEX.md) | Docs index |

---

*Per GUIDE_00_MASTER and GUIDE_41_DOCS.*
