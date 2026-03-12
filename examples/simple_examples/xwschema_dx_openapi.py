#!/usr/bin/env python3
"""
XWSchema DX OpenAPI — Validate OpenAPI 3.1 spec against official meta-schema.
- Schema: Official OAI 3.1 meta-schema (URL); one line: XWSchema.load(SCHEMA_URL, format="json").
- data: Known-good OpenAPI 3.1 sample from the internet (readmeio/oas-examples Petstore).
- data2: Local file (mail_server_openapi.json), not valid against the meta-schema.
- File reads use UTF-8 by default (read_source_text).
Requires: pip install -e xwschema (from repo root).
"""

import asyncio
import sys
from pathlib import Path
DIR = Path(__file__).resolve().parent


def _bootstrap():
    _d = DIR.parents[2]  # repo root
    # Include xwnode so local edits (e.g. cow/base _reconstruct_native) are used; xwdata imports xwnode
    for n in ("xwschema", "xwdata", "xwsystem", "xwnode"):
        s = _d / n / "src"
        if s.exists() and str(s) not in sys.path:
            sys.path.insert(0, str(s))
_bootstrap()
from exonware.xwdata import XWData
from exonware.xwschema import XWSchema
from exonware.xwsystem.io import read_source_text
from exonware.xwsystem.io.serialization import JsonSerializer
# Official OpenAPI 3.1 meta-schema and samples
SCHEMA_URL = "https://spec.openapis.org/oas/3.1/schema/2022-10-07"
DATA_URL = "https://raw.githubusercontent.com/readmeio/oas-examples/main/3.1/json/petstore.json"
DATA2_FILE = DIR / "mail_server_openapi.json"  # local; not valid against meta-schema
async def main():
    schema_openapi = await XWSchema.load(SCHEMA_URL, format="json")
    data_1 = await XWData(DATA_URL, format="json")
    data_2 = await XWData(DATA2_FILE, format="json") #Do not change it, make it work, change XWData
    # Valid data (from internet)
    valid, errors = await schema_openapi.validate(data_1)
    print(f"data (Petstore): Valid: {valid}" if valid else f"data (Petstore): Valid: {valid} ({len(errors)} errors)")
    # Invalid data (local mail_server_openapi.json; read_source_text uses utf-8 by default)
    valid2, errors2 = await schema_openapi.validate(data_2)
    print(f"data2 (local):   Valid: {valid2}" if valid2 else f"data2 (local):   Valid: {valid2} ({len(errors2)} errors)")
if __name__ == "__main__":
    asyncio.run(main())
