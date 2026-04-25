# xwschema — API Reference

**Last Updated:** 20-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 6

API reference for xwschema (output of GUIDE_15_API). See [REF_22_PROJECT.md](REF_22_PROJECT.md) and [REF_13_ARCH.md](REF_13_ARCH.md).

---

## Main entry points / "key code" (REF_01_REQ sec. 6)

| Symbol | Role |
|--------|------|
| **XWSchema** | Facade: multi-type constructor (dict/path/XWData/XWSchema), async load/save/validate/from_data, validate_issues, extract_properties/load_properties, extract_parameters/load_parameters. |
| **XWSchemaBuilder** | Fluent schema construction. |
| **XWSchemaConfig**, ValidationConfig, GenerationConfig, PerformanceConfig | Configuration. |
| **SchemaFormat**, ValidationMode, SchemaGenerationMode, ConstraintType | Enums. |
| **ValidationIssue** | Validation result detail. |
| **class_to_string**, **string_to_class**, **normalize_type**, **normalize_schema_dict** | Type utilities. |
| **XWSchemaError** family | XWSchemaError, XWSchemaValidationError, XWSchemaTypeError, XWSchemaConstraintError, XWSchemaParseError, XWSchemaFormatError, XWSchemaReferenceError, XWSchemaGenerationError. |

Engine, format handler implementations, registry internals, and pipeline implementations are **internal**—not in public API (only facade/builder/config/defs/errors/type_utils in `__all__`).

**Validation: dual support.** The validator accepts **XWData** or **native** dict/list. For XWData it uses path navigation (`data[field]`) and `to_native()` for type checking; for native structures it uses standard dict/list validation. Required fields, properties, array items, types, constraints, enums, and patterns are validated in both paths. See REF_14_DX for key code.

---

## Easy (1–3 lines) vs advanced

**Easy:**

- `schema = XWSchema({'type': 'object', 'properties': {'name': {'type': 'string'}}})`
- `is_valid, errors = await schema.validate(data)` or `schema.validate_sync(data)`
- `schema = await XWSchema.load(path)` or `await XWSchema.load(path, format=SchemaFormat.JSON_SCHEMA)`
- `schema = await XWSchema.from_data(data)`

**Advanced:**

- Builder chaining; `validate_issues` / `validate_issues_sync` for full issue list.
- Convert between schema formats via engine (e.g. OpenAPI → JSON Schema).
- `XWSchema.extract_properties(obj)`, `load_properties(obj, list[XWSchema])`; `extract_parameters(func)`, `load_parameters(func, parameters)`.
- Custom XWSchemaConfig (validation/generation/performance).

---

## Schema Catalog (DDL-like API)

**SchemaCatalog** and **SchemaCatalogEntry** live in `xwschema.registry.catalog`. Use for local schema-on-write and DDL-style operations:

- **SchemaCatalog(catalog_path)** — local JSON-backed catalog; persistence uses xwsystem **JsonSerializer** (flyweight) for reusability and performance. **ConfluentSchemaRegistry** (and other registry implementations in `registry/schema_registry.py`) use the same **get_serializer(JsonSerializer)** for schema string normalization (no stdlib json). Optional **cache_size** on ConfluentSchemaRegistry uses xwsystem **create_cache** for get_schema/get_latest_schema (LRU, high performance). JSON and cache reuse are covered by `tests/1.unit/registry_tests/test_schema_registry.py`.
- **create_schema(name, definition, schema_type="JSON")** — CREATE equivalent; returns SchemaCatalogEntry.
- **alter_schema(name, changes)** — ALTER equivalent; merges `changes["definition"]` and bumps version.
- **drop_schema(name)** — DROP equivalent.
- **get_schema(name)**, **get_schema_version(name)** (returns version or None), **list_schemas()** — read API.

This provides **schema-on-write** when used with XWStorageDb or any validate-on-write flow: pass a SchemaCatalog instance as the `schema` option (e.g. XWStorageDb(schema=catalog)); writes are validated against the catalog before persistence. Integrate with xwstorage/xwquery by passing a SchemaCatalog instance as the `schema` option for validate-on-write. See tests in `tests/1.unit/registry_tests/test_catalog.py`.

**Schema migrations.** Use **apply_migration(catalog, name, definition_updates)** (from `xwschema.registry`) to evolve a schema in one step: it deep-merges `definition_updates` into the schema definition and bumps the version via `alter_schema`. Use for adding properties, changing `required`, or other definition changes. Raises if the schema does not exist. **diff_schema_definitions(old_def, new_def)** returns a list of `(path, change_type, old_val, new_val)` with change_type in `"added"`, `"removed"`, `"changed"` for migration audit and tooling. Tests: `tests/1.unit/registry_tests/test_catalog.py` (TestApplyMigration, TestDiffSchemaDefinitions).

**Format conversion (optional BaaS).** **SchemaFormatConverter** in `xwschema.operations.format_conversion` converts between schema formats (e.g. OpenAPI ↔ JSON Schema). When **cache_size** > 0 it uses xwsystem **create_cache** for conversion result cache (LRU); tests: `tests/1.unit/engine_tests/test_format_conversion.py` (TestSchemaFormatConverterCache).

---

## Integration / existing APIs (REF_01_REQ sec. 6)

- **xwsystem:** Logging, I/O, XWObject (facade extends it).
- **xwdata:** Load/save, path-based schema—base of the engine; used by facade and engine.
- **xwquery:** Schema query (e.g. XWData.query).
- **xwstorage/XWStorageDb:** Optional SchemaCatalog or XWSchema for schema-on-write.
- **Entry point:** `xwsystem.schema_validators` for xwsystem consumers (e.g. xwdata).

---

## Not in public API

- Engine (XWSchemaEngine), format handler classes, registry internals, validation/conversion pipeline implementations. Use facade and builder only for public use.

---

*Per GUIDE_00_MASTER and GUIDE_15_API.*
