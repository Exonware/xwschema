"""
Benchmark for xwschema_parts.py: XWSchema(schema) + to_dict().
Measures import time, construction time, and to_dict() time.
WHY IMPORT TAKES ~1–1.5 s
-------------------------
  from exonware.xwschema import XWSchema  triggers this chain:
  1. exonware.xwschema.__init__
     -> exonware.xwlazy.auto_enable_lazy  (whole xwlazy package)
     -> .facade -> XWSchema
  2. .facade imports:
     -> exonware.xwsystem (get_logger, XWObject)
     -> exonware.xwdata (XWData)
     -> .base, .config, .engine, .builder, .type_utils, .errors
  3. .base imports:
     -> exonware.xwsystem.shared (AObject)
     -> exonware.xwdata (XWData again)
     -> .contracts, .config, .defs
  4. .engine imports:
     -> exonware.xwsystem.io.serialization.auto_serializer (AutoSerializer)
     -> exonware.xwdata (XWData again)
     -> .validator, .generator
  So one "import XWSchema" loads: xwlazy, xwsystem (logging, shared, io.serialization,
  security, caching, monitoring, ...), xwdata (facade, base, data engine, operations,
  format strategies, ...), and all of xwschema. No lazy loading: every dependency
  is resolved at import time. Hence ~1–1.5 s.
Run import-time breakdown:
  python -X importtime -c "from exonware.xwschema import XWSchema" 2>&1 | Select-String exonware
"""

import time
# -----------------------------------------------------------------------------
# 1. Import time
# -----------------------------------------------------------------------------
t0 = time.perf_counter()
from exonware.xwschema import XWSchema
t1 = time.perf_counter()
import_ms = (t1 - t0) * 1000
print(f"Import 'exonware.xwschema.XWSchema': {import_ms:.2f} ms")
# Same schema as xwschema_parts.py
SCHEMA = {
    "id": "xwschema.examples.person",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
    },
    "required": ["name", "age"],
}
# -----------------------------------------------------------------------------
# 2. Construction time (XWSchema(schema))
# -----------------------------------------------------------------------------
N = 500
warmup = 50
for _ in range(warmup):
    XWSchema(schema=SCHEMA)
t0 = time.perf_counter()
for _ in range(N):
    schema_person = XWSchema(schema=SCHEMA)
t1 = time.perf_counter()
construct_ms_total = (t1 - t0) * 1000
construct_ms_per_call = construct_ms_total / N
print(f"XWSchema(schema) x{N}: total {construct_ms_total:.2f} ms, per call {construct_ms_per_call:.3f} ms")
# -----------------------------------------------------------------------------
# 3. to_dict() time (single instance, many calls)
# -----------------------------------------------------------------------------
schema_person = XWSchema(schema=SCHEMA)
for _ in range(warmup):
    schema_person.to_dict()
t0 = time.perf_counter()
for _ in range(N):
    schema_person.to_dict()
t1 = time.perf_counter()
to_dict_ms_total = (t1 - t0) * 1000
to_dict_ms_per_call = to_dict_ms_total / N
print(f"to_dict() x{N}: total {to_dict_ms_total:.2f} ms, per call {to_dict_ms_per_call:.3f} ms")
# -----------------------------------------------------------------------------
# 4. One full run (construct + to_dict) like xwschema_parts.main()
# -----------------------------------------------------------------------------
t0 = time.perf_counter()
schema_person = XWSchema(schema=SCHEMA)
_ = schema_person.to_dict()
t1 = time.perf_counter()
full_run_ms = (t1 - t0) * 1000
print(f"One full run (construct + to_dict): {full_run_ms:.3f} ms")
# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
print()
print("Summary:")
print(f"  Import:        {import_ms:.2f} ms  (one-time)")
print(f"  Construct:     {construct_ms_per_call:.3f} ms per XWSchema(schema)")
print(f"  to_dict():     {to_dict_ms_per_call:.3f} ms per call")
print(f"  Full run:      {full_run_ms:.3f} ms (construct + to_dict)")
# -----------------------------------------------------------------------------
# Why it feels slow
# -----------------------------------------------------------------------------
if import_ms > 200:
    print()
    print("Why the script feels slow:")
    print("  - First-time import of 'exonware.xwschema' is ~{:.0f} ms (one-time cost).".format(import_ms))
    print("  - That pull brings in: xwdata (~350 ms), xwsystem (logging, I/O, security, caching),")
    print("    xwlazy, and the full xwschema stack (base, engine, facade).")
    print("  - After import, XWSchema(schema) and to_dict() are fast (<0.2 ms per run).")
    print("  - Import breakdown: python -X importtime -c \"from exonware.xwschema import XWSchema\" 2>&1")
