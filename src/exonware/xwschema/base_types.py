#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/base_types.py

Canonical base-type catalogue for schema-driven products.

Individual formats (JSON Schema, Avro, OpenAPI, XSD) each use their own
type vocabulary — :class:`SchemaTypeMapper` already covers bidirectional
mapping between them. This module exposes the *canonical* set that
downstream products (hive-db, xwstorage-db, xwquery) register storage
implementations against, plus human-facing metadata so UIs can render a
dropdown out of the box without re-describing every type.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class BaseType:
    id: str              # canonical name, also the key in SchemaTypeMapper
    label: str           # short human label
    category: str        # 'text' | 'number' | 'logic' | 'temporal' | 'binary' | 'identity' | 'complex'
    description: str = ""
    nullable: bool = True


# The canonical set shared by every xw* product. Kept minimal so each
# product extends it when it has storage-specific flavours (HIVE-encrypted
# integer vs plain integer live at the hive-db layer).
BASE_TYPES: tuple[BaseType, ...] = (
    BaseType("string",    "Text",          "text",     "UTF-8 string, any length."),
    BaseType("bytes",     "Binary",        "binary",   "Raw bytes / BLOB."),
    BaseType("bool",      "Boolean",       "logic",    "True / False."),
    BaseType("int16",     "Integer (16)",  "number",   "Signed 16-bit integer."),
    BaseType("int32",     "Integer (32)",  "number",   "Signed 32-bit integer."),
    BaseType("int64",     "Integer (64)",  "number",   "Signed 64-bit integer."),
    BaseType("uint16",    "Unsigned (16)", "number",   "Unsigned 16-bit integer."),
    BaseType("uint32",    "Unsigned (32)", "number",   "Unsigned 32-bit integer."),
    BaseType("uint64",    "Unsigned (64)", "number",   "Unsigned 64-bit integer."),
    BaseType("float32",   "Float (32)",    "number",   "IEEE-754 single-precision float."),
    BaseType("float64",   "Double",        "number",   "IEEE-754 double-precision float."),
    BaseType("decimal",   "Decimal",       "number",   "Arbitrary-precision decimal."),
    BaseType("datetime",  "DateTime",      "temporal", "Date + time (UTC)."),
    BaseType("datetime_offset", "DateTime+Zone", "temporal", "Date + time with timezone offset."),
    BaseType("timespan",  "Duration",      "temporal", "Elapsed duration (ticks)."),
    BaseType("guid",      "GUID",          "identity", "Universally-unique identifier."),
    BaseType("uri",       "URI",           "text",     "Unified resource identifier."),
    BaseType("email",     "Email",         "text",     "RFC 5322 email address."),
    BaseType("json",      "JSON",          "complex",  "Embedded JSON blob."),
    BaseType("array",     "Array",         "complex",  "Ordered collection of values."),
    BaseType("object",    "Object",        "complex",  "Nested structure."),
    BaseType("null",      "Null",          "logic",    "Null value."),
)


def list_base_types() -> list[BaseType]:
    """Return a fresh list copy (for callers that mutate)."""
    return list(BASE_TYPES)


def base_type_ids() -> list[str]:
    return [t.id for t in BASE_TYPES]


def by_category() -> dict[str, list[BaseType]]:
    """Group base types by semantic category — handy for form UIs."""
    out: dict[str, list[BaseType]] = {}
    for bt in BASE_TYPES:
        out.setdefault(bt.category, []).append(bt)
    return out


def find(type_id: str) -> BaseType | None:
    for bt in BASE_TYPES:
        if bt.id == type_id:
            return bt
    return None


def extend_with(extra: Iterable[BaseType]) -> tuple[BaseType, ...]:
    """Return a tuple merging ``BASE_TYPES`` with additional product-specific
    types (e.g. hive-db's encrypted variants). Dedup by ``id`` — the
    supplied entries win."""
    seen = {bt.id: bt for bt in BASE_TYPES}
    for bt in extra:
        seen[bt.id] = bt
    return tuple(seen.values())


__all__ = [
    "BaseType",
    "BASE_TYPES",
    "list_base_types",
    "base_type_ids",
    "by_category",
    "find",
    "extend_with",
]
