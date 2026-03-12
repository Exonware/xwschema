#!/usr/bin/env python3
"""
XWSchema DX — Simple schema + data example.
- One simple schema, one simple data; validate and show result.
- Dict is handled automatically at construction (XWSchema/XWData accept dict).
- XWSchema reuses XWObject for __str__ (JSON-like) and from_string.
- XWData prints JSON-like via __str__; from_string for round-trip.
"""
# When run from repo, add local package src dirs so exonware.xwschema/xwdata/xwsystem are found
# (avoids ModuleNotFoundError if venv doesn't have editable install or a different venv is used)

import sys
from pathlib import Path

def _add_repo_src_to_path():
    _file = Path(__file__).resolve()
    # .../xwschema/examples/simple_examples/xwschema_dx.py -> repo root = parents[3]
    _repo = _file.parents[3]
    for _name in ("xwschema", "xwdata", "xwsystem"):
        _src = _repo / _name / "src"
        if _src.exists() and str(_src) not in sys.path:
            sys.path.insert(0, str(_src))
_add_repo_src_to_path()
import asyncio
from exonware.xwschema import XWSchema
from exonware.xwdata import XWData
# 1. Simple schema (dict handled at start)
schema = XWSchema({
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "count": {"type": "integer", "minimum": 0},
    },
    "required": ["name"],
})
# 2. Simple data (dict handled at start)
data = XWData({
    "name": "example",
    "count": -42,
})
async def main():
    is_valid, errors = await schema.validate(data)
    print("Schema (JSON-like, XWSchema reuses XWObject __str__):")
    print(schema)
    print("\nData (JSON-like):")
    print(data)
    print("\nValid:", is_valid)
    if errors:
        print("Errors:", errors)
    # Round-trip: to string and from string
    schema_str = str(schema)
    schema2 = XWSchema.from_string(schema_str)
    data_str = str(data)
    data2 = XWData.from_string(data_str)
    print("\nRound-trip (from_string) OK:", schema2.to_native() == schema.to_native(), data2.to_native() == data.to_native())
if __name__ == "__main__":
    asyncio.run(main())
