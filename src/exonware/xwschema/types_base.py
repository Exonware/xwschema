#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/types_base.py

Built-in **logical kinds** (mostly ``type: string`` with portable ``pattern``, plus a small set of
``integer`` / ``number`` / ``boolean`` fragments with ``minimum`` / ``maximum`` / ``multipleOf`` where that matches
JSON Schema / OpenAPI better than forcing strings). Values can still be transported as strings in forms/CSV and
validated after coercion when you control parsing.

This module replaces the former ``builtin_semantic_strings`` module (single source of truth).

Use :data:`schemas` / :func:`schema_for` for ready-made :class:`~exonware.xwschema.facade.XWSchema` instances,
:func:`string_type` (and lowercase markers like :data:`rfc3339`, :data:`slug`, …) for ``ActionParameter.param_type`` markers that also expose
``__kind_schema__``, or JSON Schema ``format`` / :data:`param_name_to_kind`.

For a short import path, use the same module under the alias name: ``from exonware.xwschema import types_basic as param`` (see package ``__init__``) or ``import exonware.xwschema.types_base as param``.

Each catalog entry is built as ``XWSchema({...})``: a normal JSON Schema fragment dict plus optional extension keys
``x-exonware-builtin-id`` and ``x-exonware-kind-aliases`` (see :mod:`exonware.xwschema.defs`). Those keys are removed
from the stored schema and copied into :attr:`~exonware.xwschema.base.ASchema._metadata` on the instance.

Non-type helpers (lookup, fragments, help text, validation) live in the same module for implementation convenience but
are **not** part of :data:`__all__` — import them explicitly or from :mod:`exonware.xwschema`.

**Intentionally not added as single “logical kinds” here**

Things that are really composite JSON (object / array / ``json`` / ``jsonb`` / full GeoJSON / WKT geometries), opaque blob
streams, arbitrary HTML/XML, ``$ref`` graph shapes, and similar shapes **do not** belong as one flat catalog fragment in
this registry without a larger schema object model. Modeling them as a fake one-line ``string`` regex would be
misleading, so they were skipped.

If you want a **second layer** (for example ``builtin_object_kinds`` with ``geojson_point`` as
``{"type": "object", ...}`` templates), that can be a follow-up module that sits beside this one instead of overloading
the scalar catalog.

**Intentionally not added as a fake “single string type”**

* **Nullable / optional as a wrapper** — needs an inner schema; express with ``oneOf`` / ``anyOf`` in real JSON Schema,
  not a lone catalog entry pretending to be a scalar.
* **Full “regex type”** (a regex that validates regexes) — not reliable across runtimes and validators.
* **Full GeoJSON / arbitrary binary** — belongs in real object schemas or ``contentEncoding`` / media-type aware layers,
  not a one-line pattern in this list.

If you want a **second catalog** for **schema templates** (nullable wrappers, GeoJSON Point, multipart file metadata
objects, and so on), add something like ``types_templates.py`` next to this module rather than stretching
``types_base`` beyond scalar / small-fragment shapes.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
"""

from __future__ import annotations

import re
from typing import Any, ClassVar

from .defs import XW_EXONWARE_BUILTIN_ID_KEY, XW_EXONWARE_KIND_ALIASES_KEY
from .facade import XWSchema


def _builtin_dict(
    id: str,
    title: str,
    description: str,
    *,
    pattern: str | None = None,
    examples: tuple[Any, ...] = (),
    kind_aliases: tuple[str, ...] = (),
    json_type: str = "string",
    format: str | None = None,
    minimum: int | float | None = None,
    maximum: int | float | None = None,
    exclusive_minimum: int | float | None = None,
    exclusive_maximum: int | float | None = None,
    multiple_of: int | float | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    enum_choices: tuple[Any, ...] | None = None,
    items_schema: dict[str, Any] | None = None,
    additional_properties: bool | dict[str, Any] | None = None,
    min_items: int | None = None,
    max_items: int | None = None,
) -> dict[str, Any]:
    """Build one catalog schema dict (JSON Schema fragment + exonware extension keys)."""
    frag: dict[str, Any] = {
        "type": json_type,
        "title": title,
        "description": description,
    }
    for value, json_key in (
        (format, "format"),
        (pattern, "pattern"),
        (min_length, "minLength"),
        (max_length, "maxLength"),
        (minimum, "minimum"),
        (maximum, "maximum"),
        (exclusive_minimum, "exclusiveMinimum"),
        (exclusive_maximum, "exclusiveMaximum"),
        (multiple_of, "multipleOf"),
    ):
        if value is not None:
            frag[json_key] = value
    if enum_choices is not None:
        frag["enum"] = list(enum_choices)
    if json_type == "array":
        frag["items"] = dict(items_schema) if items_schema is not None else {}
        if min_items is not None:
            frag["minItems"] = min_items
        if max_items is not None:
            frag["maxItems"] = max_items
    if json_type == "object" and additional_properties is not None:
        frag["additionalProperties"] = additional_properties
    if examples:
        frag["examples"] = list(examples)
    frag[XW_EXONWARE_BUILTIN_ID_KEY] = id
    frag[XW_EXONWARE_KIND_ALIASES_KEY] = list(kind_aliases)
    return frag


class param_marker:
    """Marker base for :func:`string_type` classes used as ``ActionParameter.param_type``."""

    __slots__ = ()
    # Class-level on each concrete marker from :func:`string_type` (not instance fields).
    __kind_id__: ClassVar[str]
    __kind_schema__: ClassVar[XWSchema]


def _rx(pat: str) -> re.Pattern[str]:
    return re.compile(pat)


# NOTE: keep patterns ECMA-262 friendly — avoid ``\p{...}`` (not in Python ``re``).
_builtin_catalog: tuple[XWSchema, ...] = (
    XWSchema(_builtin_dict(
        id="date",
        title="ISO calendar date",
        description="YYYY-MM-DD (Gregorian).",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$",
        examples=("2026-04-12", "1999-01-01"),
        kind_aliases=("iso_date", "calendar_date"),
    )),
    XWSchema(_builtin_dict(
        id="time",
        title="Clock time",
        description="24h HH:MM or HH:MM:SS.",
        pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$",
        examples=("17:28", "09:05:00"),
        kind_aliases=("clock_time",),
    )),
    XWSchema(_builtin_dict(
        id="datetime",
        title="RFC 3339 timestamp (no fractional leap quirks)",
        description="ISO-like date + time with optional Z or numeric offset.",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])[T ](?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?(?:\.\d{1,9})?(?:Z|[+-](?:[01]\d|2[0-3]):?[0-5]\d)?$",
        examples=("2026-04-12T17:28:00Z", "2026-04-12T17:28:00+00:00"),
        kind_aliases=("date_time", "timestamp", "rfc3339"),
    )),
    XWSchema(_builtin_dict(
        id="year_month",
        title="Year-month",
        description="YYYY-MM (month always two digits).",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
        examples=("2026-04", "1999-12"),
        kind_aliases=("yearmonth", "month"),
    )),
    XWSchema(_builtin_dict(
        id="email",
        title="Email address",
        description="Pragmatic mailbox string (not full RFC 5322).",
        pattern=r"^[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,63}\.[A-Za-z]{2,24}$",
        examples=("team@exonware.com",),
        kind_aliases=("e_mail",),
    )),
    XWSchema(_builtin_dict(
        id="uri",
        title="HTTP(S) URL",
        description="Common web URL form; tighten per product if needed.",
        pattern=r"^https?://[\w.-]+(?::\d{1,5})?(?:/[\w._~/?#%+\-=&]*)?$",
        examples=("https://example.com/path?q=1", "http://localhost:8080/"),
        kind_aliases=("url", "http_url", "https_url"),
    )),
    XWSchema(_builtin_dict(
        id="uuid",
        title="UUID",
        description="Lowercase canonical UUID string.",
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        examples=("550e8400-e29b-41d4-a716-446655440000",),
        kind_aliases=("guid",),
    )),
    XWSchema(_builtin_dict(
        id="uuid_v7",
        title="UUID v7 (hex string, shape-only)",
        description="UUID with version nibble ``7`` (time-ordered IDs). Shape check only; use a UUID library to validate semantics.",
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        examples=("018e611b-8b2a-7f93-a3b1-111111111111",),
        kind_aliases=("uuid7", "time_ordered_uuid"),
    )),
    XWSchema(_builtin_dict(
        id="slug",
        title="Identifier / slug",
        description="Short ASCII id: letters, digits, ``_`` or ``-`` (good for keys, auth folders, command tokens).",
        pattern=r"(?i)^[a-z0-9][a-z0-9_-]{1,63}$",
        examples=("RU-xxxxxx", "kta", "rep_broad_day_u"),
        kind_aliases=("kebab", "kebab_case", "path_token", "short_id"),
    )),
    XWSchema(_builtin_dict(
        id="entity_id",
        title="Entity / record id (snake_case)",
        description="Lowercase stable key for entities and cross-references (JSON fields like ``id``, ``*_id``).",
        pattern=r"^(?=.{1,64}$)[a-z][a-z0-9_]*$",
        examples=("blue", "blue_father", "blues_myth_world", "fairy_guardian_shard"),
        kind_aliases=("record_id", "object_id", "world_entity_id"),
    )),
    XWSchema(_builtin_dict(
        id="namespaced_key",
        title="Namespaced logical type key",
        description="Dot-separated lowercase segments (e.g. ``bluesmyth.character`` for ``schema.name`` / ``type_id`` strings).",
        pattern=r"^(?=.{2,128}$)[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$",
        examples=("bluesmyth.character", "bluesmyth.story_arc", "bluesmyth.player_character"),
        kind_aliases=("logical_type", "type_key", "schema_name_key"),
    )),
    XWSchema(_builtin_dict(
        id="rel_path",
        title="Relative path fragment",
        description="Config or log path fragment (letters, digits, common punctuation; not a full OS path validator).",
        pattern=r"^[A-Za-z0-9_.:/\\-]{0,512}$",
        examples=("", ".data/xwauth", "logs/out.txt"),
        kind_aliases=("path", "posixish_path", "win_path_fragment"),
    )),
    XWSchema(_builtin_dict(
        id="telegram_username",
        title="Telegram username / handle",
        description="Optional @; Telegram allows a-z, 0-9, underscore; length bounds are practical (not official).",
        pattern=r"(?i)^@?[a-z0-9_]{4,32}$",
        examples=("@muhdashe", "karizma_dev_bot"),
        kind_aliases=("tg_username", "telegram_handle", "telegram_user"),
    )),
    XWSchema(_builtin_dict(
        id="color_hex",
        title="CSS hex color",
        description="#RGB, #RRGGBB, or #RRGGBBAA.",
        pattern=r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$",
        examples=("#0cf", "#00ccff", "#00ccff88"),
        kind_aliases=("hex_color", "colour_hex"),
    )),
    XWSchema(_builtin_dict(
        id="country_code_iso3166_alpha2",
        title="ISO 3166-1 alpha-2 country code",
        description="Two ASCII letters, uppercase.",
        pattern=r"^[A-Z]{2}$",
        examples=("US", "DE", "AE"),
        kind_aliases=("country_code", "iso_country", "country_iso2"),
    )),
    XWSchema(_builtin_dict(
        id="city_name",
        title="City or locality name",
        description="Human place name (Latin + common accents + digits/punctuation).",
        pattern=r"^[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9\s.,'()\-]{0,127}$",
        examples=("Dubai", "São Paulo", "St. John's"),
        kind_aliases=("city", "locality"),
    )),
    XWSchema(_builtin_dict(
        id="country_name",
        title="Country name (free text)",
        description="Country as written (not the ISO code).",
        pattern=r"^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s.'-]{1,63}$",
        examples=("United Arab Emirates", "Côte d'Ivoire"),
        kind_aliases=("country",),
    )),
    XWSchema(_builtin_dict(
        id="temperature",
        title="Temperature with optional unit",
        description="Number + optional C/F suffix (ASCII).",
        pattern=r"(?i)^-?\d+(?:\.\d+)?\s*(?:c|f|℃|°f|°c)?$",
        examples=("21", "70.5F", "-3C"),
        kind_aliases=("temp",),
    )),
    XWSchema(_builtin_dict(
        id="length_measure",
        title="Length / distance with unit",
        description="Positive number + common metric/imperial unit token.",
        pattern=r"(?i)^\d+(?:\.\d+)?\s*(?:mm|cm|m|km|in|ft|yd|mi)$",
        examples=("12cm", "1.5m", "6ft"),
        kind_aliases=("length", "distance"),
    )),
    XWSchema(_builtin_dict(
        id="weight_measure",
        title="Mass / weight with unit",
        description="Positive number + common mass unit token.",
        pattern=r"(?i)^\d+(?:\.\d+)?\s*(?:mg|g|kg|lb|oz|t)$",
        examples=("70kg", "12.5lb"),
        kind_aliases=("weight", "mass"),
    )),
    XWSchema(_builtin_dict(
        id="currency_code_iso4217",
        title="ISO 4217 currency code",
        description="Three uppercase letters.",
        pattern=r"^[A-Z]{3}$",
        examples=("USD", "EUR", "AED"),
        kind_aliases=("currency", "iso4217"),
    )),
    XWSchema(_builtin_dict(
        id="phone_e164ish",
        title="Phone number (simple international)",
        description="Optional +, leading country digit 1-9, 7-14 further digits.",
        pattern=r"^\+?[1-9]\d{6,14}$",
        examples=("+971501234567", "15551234567"),
        kind_aliases=("phone", "msisdn", "telephone"),
    )),
    XWSchema(_builtin_dict(
        id="ipv4",
        title="IPv4 address",
        description="Dotted decimal quad.",
        pattern=r"^(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)$",
        examples=("192.168.0.1", "10.0.0.1"),
        kind_aliases=("ip_v4",),
    )),
    XWSchema(_builtin_dict(
        id="hostname",
        title="DNS hostname",
        description="LDH labels with at least one dot (not single-label `.local` special cases).",
        pattern=r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$",
        examples=("api.example.com", "bot.telegram.org"),
        kind_aliases=("host", "domain_name"),
    )),
    XWSchema(_builtin_dict(
        id="integer_string",
        title="Integer as decimal string",
        description="Optional leading minus; no scientific notation.",
        pattern=r"^-?\d+$",
        examples=("-1", "0", "42"),
        kind_aliases=("int_string", "decimal_integer_string"),
    )),
    XWSchema(_builtin_dict(
        id="decimal_string",
        title="Decimal number as string",
        description="Optional leading minus; dot as radix separator.",
        pattern=r"^-?\d+(?:\.\d+)?$",
        examples=("3.14", "-0.5"),
        kind_aliases=("float_string", "number_string", "decimal", "decimal_string_api"),
    )),
    XWSchema(_builtin_dict(
        id="boolean_token",
        title="Boolean token",
        description="Common true/false spellings (ASCII, case-insensitive).",
        pattern=r"(?i)^(?:true|false|1|0|yes|no)$",
        examples=("true", "false", "YES"),
        kind_aliases=("bool_token",),
    )),
    XWSchema(_builtin_dict(
        id="locale_bcp47",
        title="BCP 47 language tag (simple)",
        description="``ll`` or ``ll-RR`` (language + optional region).",
        pattern=r"(?i)^[a-z]{2}(?:-[a-z]{2})?$",
        examples=("en", "en-US", "ar-AE"),
        kind_aliases=("language_tag", "lang", "locale"),
    )),
    # --- Numeric JSON types (OpenAPI / JSON Schema; prefer over string when the wire format is JSON) ---
    XWSchema(_builtin_dict(
        id="int32",
        title="32-bit signed integer",
        description="JSON ``integer`` in the signed 32-bit range (API / DB interop).",
        json_type="integer",
        minimum=-2147483648,
        maximum=2147483647,
        examples=(0, -1, 2147483647),
        kind_aliases=("integer32", "sql_int"),
    )),
    XWSchema(_builtin_dict(
        id="uint8",
        title="8-bit unsigned integer",
        description="JSON ``integer`` from 0 to 255 (byte / tinyint).",
        json_type="integer",
        minimum=0,
        maximum=255,
        examples=(0, 128, 255),
        kind_aliases=("byte", "tinyint_unsigned", "uint8_t"),
    )),
    XWSchema(_builtin_dict(
        id="port",
        title="TCP/UDP port",
        description="JSON ``integer`` in ``1..65535``.",
        json_type="integer",
        minimum=1,
        maximum=65535,
        examples=(1, 443, 65535),
        kind_aliases=("tcp_port", "udp_port"),
    )),
    XWSchema(_builtin_dict(
        id="unix_timestamp_seconds",
        title="Unix epoch seconds",
        description="JSON ``integer`` seconds since 1970-01-01T00:00:00Z (practical upper bound for APIs).",
        json_type="integer",
        minimum=0,
        maximum=4102444800,
        examples=(0, 1700000000),
        kind_aliases=("epoch_seconds", "unix_time", "timestamp", "unix_timestamp"),
    )),
    XWSchema(_builtin_dict(
        id="year_integer",
        title="Gregorian calendar year",
        description="JSON ``integer`` year (common DB / analytics use).",
        json_type="integer",
        minimum=1583,
        maximum=9999,
        examples=(1999, 2026),
        kind_aliases=("calendar_year",),
    )),
    XWSchema(_builtin_dict(
        id="latitude",
        title="Latitude (decimal degrees)",
        description="JSON ``number`` in ``[-90, 90]`` (WGS84-style decimal degrees).",
        json_type="number",
        minimum=-90.0,
        maximum=90.0,
        examples=(0.0, 25.2048, -33.8688),
        kind_aliases=("lat", "geo_lat"),
    )),
    XWSchema(_builtin_dict(
        id="longitude",
        title="Longitude (decimal degrees)",
        description="JSON ``number`` in ``[-180, 180]`` (WGS84-style decimal degrees).",
        json_type="number",
        minimum=-180.0,
        maximum=180.0,
        examples=(0.0, 55.2708, -151.2093),
        kind_aliases=("lng", "lon", "geo_lng"),
    )),
    XWSchema(_builtin_dict(
        id="percentage_0_100",
        title="Percentage (0–100)",
        description="JSON ``number`` from 0 to 100 inclusive (UI metrics, progress).",
        json_type="number",
        minimum=0.0,
        maximum=100.0,
        examples=(0.0, 50.5, 100.0),
        kind_aliases=("percent", "pct", "percentage", "ratio_percent"),
    )),
    XWSchema(_builtin_dict(
        id="probability",
        title="Probability (0–1)",
        description="JSON ``number`` from 0 to 1 inclusive.",
        json_type="number",
        minimum=0.0,
        maximum=1.0,
        examples=(0.0, 0.25, 1.0),
        kind_aliases=("prob", "p_value"),
    )),
    XWSchema(_builtin_dict(
        id="boolean_json",
        title="JsonBoolean",
        description="Native JSON ``true`` / ``false`` (not a string token).",
        json_type="boolean",
        examples=(True, False),
        kind_aliases=("bool", "json_boolean", "boolean", "flag"),
    )),
    # --- String encodings / identifiers (still JSON ``type: string``) ---
    XWSchema(_builtin_dict(
        id="ulid",
        title="ULID (Crockford base32)",
        description="26-character ULID string (case-insensitive).",
        pattern=r"(?i)^[0-9A-HJKMNP-TV-Z]{26}$",
        examples=("01ARZ3NDEKTSV4RRFFQ69G5FAV",),
        kind_aliases=("ulid_string",),
    )),
    XWSchema(_builtin_dict(
        id="base64_standard",
        title="Base64 (standard alphabet, padded)",
        description="Common Base64 text form (RFC 4648 base64 alphabet with padding).",
        pattern=r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$",
        examples=("Zg==", "SGVsbG8=", "U29sYXJ5"),
        kind_aliases=("base64", "b64"),
    )),
    XWSchema(_builtin_dict(
        id="mime_type",
        title="MIME type / media type",
        description="Pragmatic ``type/subtype`` token (not full IANA registry enforcement).",
        pattern=r"(?i)^[a-z0-9][a-z0-9._+-]*/[a-z0-9][a-z0-9._+-]+$",
        examples=("application/json", "image/png", "text/plain"),
        kind_aliases=("media_type", "content_type"),
    )),
    XWSchema(_builtin_dict(
        id="semver",
        title="Semantic version (loose)",
        description="``MAJOR.MINOR.PATCH`` plus optional prerelease/build (pragmatic; not full SemVer grammar).",
        pattern=r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$",
        # Avoid quoted "0.0.x" literals: CI version scan treats them as legacy package versions.
        examples=("1.0.0", "0.1.0", "2.0.0-rc.1"),
        kind_aliases=("semantic_version", "version_string"),
    )),
    XWSchema(_builtin_dict(
        id="duration_iso8601",
        title="ISO 8601 duration (subset)",
        description="Common ``PnDTnHnM`` / ``PTnHnM`` style durations (subset; not all ISO edge cases).",
        pattern=r"^P(?=\d|T\d)(?:\d+Y)?(?:\d+M)?(?:\d+W)?(?:\d+D)?(?:T(?:\d+H)?(?:\d+M)?(?:\d+(?:\.\d+)?S)?)?$",
        examples=("P1D", "PT1H30M", "P3DT12H"),
        kind_aliases=("iso_duration", "duration"),
    )),
    XWSchema(_builtin_dict(
        id="timezone_iana_loose",
        title="IANA-like timezone name (loose)",
        description="``Area/Location`` style string (not a full IANA validator; use zoneinfo in apps).",
        pattern=r"^(?:UTC|Etc/UTC|[A-Za-z_]{2,14}/[A-Za-z0-9_.+-]{1,64})$",
        examples=("America/New_York", "Asia/Dubai", "UTC"),
        kind_aliases=("tz", "iana_timezone"),
    )),
    XWSchema(_builtin_dict(
        id="cron_expression_basic",
        title="Cron-like schedule (basic)",
        description="Five or six whitespace-separated fields of digits, ``*``, ``/``, ``-``, ``,`` (not full cron semantics).",
        pattern=r"^[\d\*\/\-\,\s]{9,128}$",
        examples=("0 9 * * 1", "*/15 * * * *"),
        kind_aliases=("cron", "cron_string"),
    )),
    XWSchema(_builtin_dict(
        id="jwt_compact",
        title="JWT compact serialization (shape only)",
        description="Three Base64URL-ish segments separated by ``.`` (signature/header claims not validated here).",
        pattern=r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$",
        examples=("eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",),
        kind_aliases=("jwt", "bearer_token_shape"),
    )),
    XWSchema(_builtin_dict(
        id="md5_hex",
        title="MD5 digest (hex)",
        description="32 lowercase hex chars (string transport of a 128-bit digest).",
        pattern=r"^[0-9a-f]{32}$",
        examples=("d41d8cd98f00b204e9800998ecf8427e",),
        kind_aliases=("md5",),
    )),
    XWSchema(_builtin_dict(
        id="sha256_hex",
        title="SHA-256 digest (hex)",
        description="64 lowercase hex chars (string transport of a 256-bit digest).",
        pattern=r"^[0-9a-f]{64}$",
        examples=(
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        ),
        kind_aliases=("sha256", "sha2_256_hex"),
    )),
    XWSchema(_builtin_dict(
        id="ipv6",
        title="IPv6 address (strict subset)",
        description="Full 8-group form or ``::1`` loopback (use ``format: ipv6`` + a dedicated validator for full RFC 5952 coverage).",
        pattern=r"(?i)^(?:(?:[0-9a-f]{1,4}:){7}[0-9a-f]{1,4}|::1)$",
        examples=("::1", "2001:0db8:0000:0000:0000:0000:0000:0001"),
        kind_aliases=("ip_v6",),
        format="ipv6",
    )),
    XWSchema(_builtin_dict(
        id="mac_address_eui48",
        title="MAC address (EUI-48 colon hex)",
        description="Six octets as colon-separated hex pairs.",
        pattern=r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$",
        examples=("00:1B:44:11:3A:B7", "aa:bb:cc:dd:ee:ff"),
        kind_aliases=("mac", "mac_address"),
    )),
    XWSchema(_builtin_dict(
        id="cidr_ipv4",
        title="IPv4 CIDR block",
        description="IPv4 + ``/`` + prefix length 0–32.",
        pattern=r"^(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)/(?:[0-9]|[12][0-9]|3[0-2])$",
        examples=("10.0.0.0/24", "192.168.0.0/16", "0.0.0.0/0"),
        kind_aliases=("cidr", "subnet"),
    )),
    # --- OpenAPI / bot “Big Four” + common containers (JSON Schema fragments) ---
    XWSchema(_builtin_dict(
        id="text_short",
        title="Short UTF-8 text",
        description="Generic ``string`` for names, labels, titles (bounded).",
        json_type="string",
        min_length=1,
        max_length=4096,
        examples=("Blue", "Hello, world!"),
        kind_aliases=("short_text", "label", "title_text", "name_text"),
    )),
    XWSchema(_builtin_dict(
        id="text_long",
        title="Long UTF-8 text",
        description="Generic ``string`` for chat bodies, descriptions, logs (bounded).",
        json_type="string",
        min_length=0,
        max_length=262144,
        examples=("A longer message…",),
        kind_aliases=("long_text", "message_text", "clob_like"),
    )),
    XWSchema(_builtin_dict(
        id="markdown_message",
        title="Markdown text (transport)",
        description="Markdown as UTF-8 ``string`` (rendering/validation is app-side).",
        json_type="string",
        min_length=1,
        max_length=1048576,
        examples=("## Title\n- item\n",),
        kind_aliases=("markdown", "md", "bot_message_markdown"),
    )),
    XWSchema(_builtin_dict(
        id="password_secret",
        title="Password / secret (string transport)",
        description="Bounded secret string (write-only semantics belong in your API layer).",
        json_type="string",
        min_length=8,
        max_length=256,
        pattern=r"^[\s\S]{8,256}$",
        examples=("correct-horse-battery-staple", "P@ssw0rd!9"),
        kind_aliases=("password", "secret", "credential"),
    )),
    XWSchema(_builtin_dict(
        id="otp",
        title="One-time passcode (digits)",
        description="Numeric OTP / TOTP / SMS-style code as a digit string (length policy is app-side beyond this shape check).",
        json_type="string",
        pattern=r"^\d{4,12}$",
        examples=("123456", "483921", "00000000"),
        kind_aliases=("otp_code", "totp", "mfa_code", "sms_code"),
    )),
    XWSchema(_builtin_dict(
        id="api_key_token",
        title="API key / opaque token (shape)",
        description="High-entropy opaque token string (not a full JWT grammar check).",
        json_type="string",
        min_length=16,
        max_length=512,
        pattern=r"^[A-Za-z0-9_.+/=-]{16,512}$",
        examples=("sk_live_1234567890abcdefghij", "pk_test_abcdefghijklmnopqrstuvwxyz0123456789"),
        kind_aliases=("api_key", "token", "opaque_token", "refresh_token_shape"),
    )),
    XWSchema(_builtin_dict(
        id="image_url_http",
        title="Image URL (http(s), common extensions)",
        description="HTTP(S) URL ending with a common raster/vector image extension.",
        json_type="string",
        format="uri",
        pattern=r"(?i)^https?://[^\s]{3,2048}\.(?:png|jpe?g|gif|webp|svg)(?:\?[^\s#]*)?(?:#[^\s]*)?$",
        examples=("https://example.com/avatar.png", "http://localhost:8080/x.webp"),
        kind_aliases=("image", "image_url", "avatar_url"),
    )),
    XWSchema(_builtin_dict(
        id="file_url_http",
        title="File URL (http(s))",
        description="HTTP(S) URL for uploaded/remote files (MIME typing is separate).",
        json_type="string",
        format="uri",
        pattern=r"^https?://[^\s]{3,2048}$",
        examples=("https://cdn.example.com/files/report.pdf",),
        kind_aliases=("file", "file_url", "upload_url"),
    )),
    XWSchema(_builtin_dict(
        id="json_integer_open",
        title="JsonIntegerUnbounded",
        description="OpenAPI-style ``integer`` without min/max (validate ranges in your domain layer if needed).",
        json_type="integer",
        examples=(1, 42, -7),
        kind_aliases=("integer", "int", "bigint_json_shape"),
    )),
    XWSchema(_builtin_dict(
        id="json_number_open",
        title="JsonNumber",
        description="OpenAPI-style ``number`` (IEEE-754 JSON number).",
        json_type="number",
        examples=(1.25, -0.5, 3.0),
        kind_aliases=("number", "float", "double"),
    )),
    XWSchema(_builtin_dict(
        id="json_array",
        title="JsonArray",
        description="``array`` with permissive ``items: {}`` (lists/tags/attachments). Prefer tighter ``items`` in real schemas.",
        json_type="array",
        items_schema={},
        examples=([1, 2, 3], ["a", "b"], []),
        kind_aliases=("array", "list"),
    )),
    XWSchema(_builtin_dict(
        id="json_object",
        title="JsonObject",
        description="``object`` with ``additionalProperties: true`` (metadata/settings/webhook bodies). Prefer explicit ``properties`` in real schemas.",
        json_type="object",
        additional_properties=True,
        examples=({"kind": "ping"}, {"a": 1, "b": 2}),
        kind_aliases=("object", "map", "dictionary", "json", "jsonb_shape", "payload"),
    )),
    XWSchema(_builtin_dict(
        id="embedding_vector",
        title="Embedding vector (float array)",
        description="``array`` of JSON numbers (RAG / semantic search). Bounds are practical defaults, not model-specific.",
        json_type="array",
        items_schema={"type": "number"},
        min_items=1,
        max_items=16384,
        examples=([0.12, -0.98, 0.03], [0.0, 1.0]),
        kind_aliases=("vector", "embedding", "float_vector"),
    )),
    XWSchema(_builtin_dict(
        id="enum_priority_sample",
        title="Enum (sample: priority)",
        description="Template for bot/API enums: replace with your own ``enum`` list in schemas.",
        json_type="string",
        enum_choices=("low", "medium", "high"),
        examples=("medium",),
        kind_aliases=("enum", "enum_sample", "priority"),
    )),
    XWSchema(_builtin_dict(
        id="interval_date_range_string",
        title="Date range (ISO start/end, slash-separated)",
        description="Inclusive calendar date range ``YYYY-MM-DD/YYYY-MM-DD`` as a single string (Postgres daterange-ish interchange).",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])/\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$",
        examples=("2026-01-01/2026-12-31",),
        kind_aliases=("daterange", "date_range", "period"),
    )),
    XWSchema(_builtin_dict(
        id="money_decimal_string",
        title="Money amount (decimal string, 2 fractional digits)",
        description="Exact two fractional digits (pair with ``currency_code_iso4217`` in APIs). Prefer decimal strings over binary floats for money.",
        pattern=r"^-?\d+\.\d{2}$",
        examples=("0.00", "12.34", "-99.99"),
        kind_aliases=("money", "currency_amount", "decimal_money"),
    )),
)

aliases: dict[str, str] = {
    str(a).lower(): str(sch._metadata["builtin_kind_id"])
    for sch in _builtin_catalog
    if sch._metadata.get("builtin_kind_id")
    for a in (sch._metadata.get("kind_aliases") or ())
}

# JSON Schema ``format`` strings (draft) → canonical kind id (subset).
json_schema_format_to_kind: dict[str, str] = {
    "date": "date",
    "time": "time",
    "date-time": "datetime",
    "email": "email",
    "uri": "uri",
    "uri-reference": "uri",
    "url": "uri",
    "uuid": "uuid",
    "hostname": "hostname",
    "ipv4": "ipv4",
    "ipv6": "ipv6",
    "markdown": "markdown_message",
}

# Heuristic: normalized parameter name → canonical kind id (product-specific keys welcome).
param_name_to_kind: dict[str, str] = {
    "year_month": "year_month",
    "yearmonth": "year_month",
    "startdate": "date",
    "start_date": "date",
    "enddate": "date",
    "end_date": "date",
    "datefrom": "date",
    "date_from": "date",
    "dateto": "date",
    "date_to": "date",
    "shortid": "slug",
    "short_id": "slug",
    "bshortid": "slug",
    "telegramusername": "telegram_username",
    "telegram_username": "telegram_username",
    "b_telegram": "telegram_username",
    "btriallink": "uri",
    "b_triallink": "uri",
    "report_wait": "integer_string",
    "base_path": "rel_path",
    "basepath": "rel_path",
    "use_storage": "boolean_token",
    "usestorage": "boolean_token",
    # Cross-entity references (e.g. Blue's Myth / xwentity examples)
    "arc_id": "entity_id",
    "character_id": "entity_id",
    "city_id": "entity_id",
    "contract_id": "entity_id",
    "country_id": "entity_id",
    "dungeon_id": "entity_id",
    "era_id": "entity_id",
    "event_id": "entity_id",
    "giver_id": "entity_id",
    "guardian_id": "entity_id",
    "host_id": "entity_id",
    "location_id": "entity_id",
    "organization_id": "entity_id",
    "overlord_org_id": "entity_id",
    "owner_id": "entity_id",
    "parent_id": "entity_id",
    "planet_id": "entity_id",
    "region_id": "entity_id",
    "ruler_org_id": "entity_id",
    "scene_id": "entity_id",
    "story_id": "entity_id",
    "target_id": "entity_id",
    "tower_id": "entity_id",
    "tree_of_life_id": "entity_id",
    # Common API / analytics names
    "lat": "latitude",
    "latitude": "latitude",
    "lng": "longitude",
    "lon": "longitude",
    "longitude": "longitude",
    "port": "port",
    "tcp_port": "port",
    "udp_port": "port",
    "percent": "percentage_0_100",
    "percentage": "percentage_0_100",
    "probability": "probability",
    "prob": "probability",
    "epoch": "unix_timestamp_seconds",
    "epoch_seconds": "unix_timestamp_seconds",
    "unix_ts": "unix_timestamp_seconds",
    "year": "year_integer",
    "calendar_year": "year_integer",
    "semver": "semver",
    "version": "semver",
    "ulid": "ulid",
    "mime": "mime_type",
    "mime_type": "mime_type",
    "content_type": "mime_type",
    "media_type": "mime_type",
    "base64": "base64_standard",
    "jwt": "jwt_compact",
    "timezone": "timezone_iana_loose",
    "tz": "timezone_iana_loose",
    "iana_timezone": "timezone_iana_loose",
    "cron": "cron_expression_basic",
    "cron_expression": "cron_expression_basic",
    "duration": "duration_iso8601",
    "iso_duration": "duration_iso8601",
    "money": "money_decimal_string",
    "money_amount": "money_decimal_string",
    "price": "money_decimal_string",
    "amount": "money_decimal_string",
    "currency_code": "currency_code_iso4217",
    "md5": "md5_hex",
    "sha256": "sha256_hex",
    "cidr": "cidr_ipv4",
    "subnet": "cidr_ipv4",
    "mac": "mac_address_eui48",
    "mac_address": "mac_address_eui48",
    "byte": "uint8",
    "tinyint": "uint8",
    "int32": "int32",
    # Bot / API common names
    "body": "text_long",
    "message": "text_long",
    "caption": "text_long",
    "reply": "markdown_message",
    "webhook_payload": "json_object",
    "metadata": "json_object",
    "settings": "json_object",
    "tags": "json_array",
    "attachments": "json_array",
    "vector": "embedding_vector",
    "embedding": "embedding_vector",
    "currency": "currency_code_iso4217",
    "pricing_currency": "currency_code_iso4217",
    "phone_number": "phone_e164ish",
    "mobile": "phone_e164ish",
    "msisdn": "phone_e164ish",
    "count": "json_integer_open",
    "limit": "json_integer_open",
    "offset": "json_integer_open",
    "score": "json_number_open",
    "amount_float": "json_number_open",
}

kinds: dict[str, XWSchema] = {
    str(s._metadata["builtin_kind_id"]): s for s in _builtin_catalog if s._metadata.get("builtin_kind_id")
}
schemas = kinds


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace("-", "_")


def kind_for(kind_id: str) -> XWSchema | None:
    """Resolve ``kind_id`` or alias (case-insensitive) to the built-in :class:`~exonware.xwschema.facade.XWSchema`."""
    key = _norm(kind_id)
    if key in kinds:
        return kinds[key]
    canon = aliases.get(key)
    return kinds.get(canon or "", None)


def kind_id_for_json_schema_format(fmt: str) -> str | None:
    """Map JSON Schema ``format`` string to a canonical kind id, if known."""
    return json_schema_format_to_kind.get(_norm(fmt).replace(" ", "-"), None)


def kind_for_param_name(param_name: str) -> str | None:
    """Best-effort kind id from a parameter / field name."""
    return param_name_to_kind.get(_norm(param_name))


def schema_fragment(kind_id: str) -> dict[str, Any]:
    """
    JSON Schema fragment for a built-in logical kind (``string``, ``integer``, ``number``, or ``boolean``).

    Merge into your schema with care (``examples`` is draft 2019-09+; many validators accept it).
    """
    k = kind_for(kind_id)
    if k is None:
        raise KeyError(f"Unknown builtin kind: {kind_id!r}")
    return dict(k.to_native())


def one_of_kinds(*kind_ids: str) -> dict[str, Any]:
    """``{"oneOf": [ ... ]}`` accepting any of the listed built-in logical kinds."""
    parts: list[dict[str, Any]] = []
    for kid in kind_ids:
        parts.append(schema_fragment(kid))
    return {"oneOf": parts}


def _resolve_kind(
    *,
    param_name: str,
    json_schema_format: str | None,
) -> XWSchema | None:
    if json_schema_format:
        mid = kind_id_for_json_schema_format(json_schema_format)
        if mid:
            k2 = kind_for(mid)
            if k2 is not None:
                return k2
    hinted = kind_for_param_name(param_name)
    if hinted:
        return kind_for(hinted)
    return None


def help_example_for_param(
    *,
    param_name: str,
    json_schema_format: str | None = None,
) -> str | None:
    """
    Short **sample** (no backticks) for inline help, or ``None``.

    Priority: JSON Schema ``format``, then parameter-name heuristics.
    """
    k = _resolve_kind(param_name=param_name, json_schema_format=json_schema_format)
    if k is None:
        return None
    exs = k.to_native().get("examples") or []
    if not exs:
        return None
    for ex in exs:
        if str(ex).strip() != "":
            return str(ex)
    return str(exs[0])


def help_pattern_for_param(
    *,
    param_name: str,
    json_schema_format: str | None = None,
) -> str | None:
    """Regex string for inline help, or ``None`` when the kind is not string-regex based."""
    k = _resolve_kind(param_name=param_name, json_schema_format=json_schema_format)
    if k is None:
        return None
    pat = k.to_native().get("pattern")
    return str(pat) if pat else None


_MARKERS: dict[str, type[param_marker]] = {}


def string_type(kind_id: str) -> type[param_marker]:
    """
    Return a small marker class suitable for ``ActionParameter(param_type=...)``.

    The class sets ``__kind_id__`` so :class:`exonware.xwaction.defs.ActionParameter` can emit the right JSON Schema
    fragment (``dict(schema.to_native())``), and ``__kind_schema__`` to the matching catalog
    :class:`~exonware.xwschema.facade.XWSchema` in :data:`kinds`.
    """
    key = _norm(kind_id)
    spec = kinds.get(key)
    if spec is None:
        spec = kind_for(kind_id)
    if spec is None:
        raise KeyError(f"Unknown builtin kind: {kind_id!r}")
    canon = str(spec._metadata.get("builtin_kind_id") or key)
    cached = _MARKERS.get(canon)
    if cached is not None:
        return cached
    safe = canon.replace(".", "_").replace("-", "_")
    name = f"kind_{safe}"

    class _M(param_marker):
        __kind_id__ = canon
        __kind_schema__ = spec

    _M.__name__ = name
    _M.__qualname__ = name
    _M.__doc__ = str(spec.to_native().get("title") or canon)
    _MARKERS[canon] = _M
    return _M


def _example_numeric_value(ex: Any, *, as_int: bool) -> int | float:
    if isinstance(ex, bool):
        raise TypeError("boolean is not a numeric example")
    if isinstance(ex, (int, float)):
        return int(ex) if as_int else float(ex)
    s = str(ex).strip()
    if as_int:
        return int(s, 10)
    return float(s)


def validate_builtin_patterns() -> None:
    """
    Validate shipped examples against patterns / numeric bounds.

    **Not** run at import time (keeps library startup light). Call from tests / CI, e.g.
    ``pytest`` on this package.
    """
    for kid, sch in kinds.items():
        d = sch.to_native()
        jt = d.get("type")
        exs = d.get("examples") or []
        enum = d.get("enum")
        if jt == "string":
            pat = d.get("pattern")
            if pat is not None:
                _rx(str(pat))
                for ex in exs:
                    if str(ex).strip() == "":
                        continue
                    if not _rx(str(pat)).fullmatch(str(ex)):
                        raise ValueError(f"Example {ex!r} does not match kind {kid!r} pattern")
        elif jt == "integer":
            for ex in exs:
                v = _example_numeric_value(ex, as_int=True)
                mn = d.get("minimum")
                mx = d.get("maximum")
                mo = d.get("multipleOf")
                if mn is not None and v < int(mn):
                    raise ValueError(f"Example {ex!r} below minimum for kind {kid!r}")
                if mx is not None and v > int(mx):
                    raise ValueError(f"Example {ex!r} above maximum for kind {kid!r}")
                if mo is not None and v % int(mo) != 0:
                    raise ValueError(f"Example {ex!r} not a multipleOf {mo!r} for kind {kid!r}")
        elif jt == "number":
            for ex in exs:
                v = _example_numeric_value(ex, as_int=False)
                mn = d.get("minimum")
                mx = d.get("maximum")
                mo = d.get("multipleOf")
                if mn is not None and v < float(mn):
                    raise ValueError(f"Example {ex!r} below minimum for kind {kid!r}")
                if mx is not None and v > float(mx):
                    raise ValueError(f"Example {ex!r} above maximum for kind {kid!r}")
                if mo is not None:
                    m = float(mo)
                    if abs((v / m) - round(v / m)) > 1e-9:
                        raise ValueError(f"Example {ex!r} not a multipleOf {mo!r} for kind {kid!r}")
        elif jt == "boolean":
            for ex in exs:
                if isinstance(ex, bool):
                    continue
                # ``to_native()`` may surface JSON booleans as strings depending on XWData path.
                if isinstance(ex, str) and ex.lower() in ("true", "false"):
                    continue
                raise ValueError(f"Example {ex!r} is not a boolean for kind {kid!r}")
        elif jt == "array":
            for ex in exs:
                if not isinstance(ex, list):
                    raise ValueError(f"Example {ex!r} is not a JSON array for kind {kid!r}")
                mini = d.get("minItems")
                maxi = d.get("maxItems")
                if mini is not None and len(ex) < int(mini):
                    raise ValueError(f"Example {ex!r} shorter than minItems for kind {kid!r}")
                if maxi is not None and len(ex) > int(maxi):
                    raise ValueError(f"Example {ex!r} longer than maxItems for kind {kid!r}")
        elif jt == "object":
            for ex in exs:
                if not isinstance(ex, dict):
                    raise ValueError(f"Example {ex!r} is not a JSON object for kind {kid!r}")
        if enum is not None:
            allowed = set(enum)
            for ex in exs:
                if ex not in allowed:
                    raise ValueError(f"Example {ex!r} not in enum for kind {kid!r}")


for _cid in kinds:
    string_type(_cid)


def schema_for(kind_id: str) -> XWSchema | None:
    """Same as :func:`kind_for` (each built-in catalog entry is already an :class:`~exonware.xwschema.facade.XWSchema`)."""
    return kind_for(kind_id)


# Lowercase annotation markers (``string_type``; paired :class:`~exonware.xwschema.facade.XWSchema` in :data:`kinds`).
# Namespace import: ``from exonware.xwschema import types_basic as param`` or ``import exonware.xwschema.types_base as param``.
iso_date = string_type("date")
clock_time = string_type("time")
rfc3339 = string_type("datetime")
date_time = rfc3339  # backward-compatible alias (same kind as ``rfc3339``)
email = string_type("email")
uri = string_type("uri")
uuid = string_type("uuid")
telegram_username = string_type("telegram_username")
slug = string_type("slug")
rel_path = string_type("rel_path")
entity_id = string_type("entity_id")
text_short = string_type("text_short")
text = text_short  # shorthand for short UTF-8 fields (names, labels); use ``text_long`` for long bodies
text_long = string_type("text_long")
markdown = string_type("markdown_message")
md = markdown  # shorthand alias
password = string_type("password_secret")
otp = string_type("otp")
json_object = string_type("json_object")
json_array = string_type("json_array")
hostname = string_type("hostname")
integer = string_type("json_integer_open")
number = string_type("json_number_open")
year_month = string_type("year_month")
integer_string = string_type("integer_string")

# Backward-compatible names (older imports / ``exonware.xwschema`` package surface).
BuiltinKind = XWSchema
string_kind = string_type

__all__ = [
    "param_marker",
    "kinds",
    "schemas",
    "string_type",
    "iso_date",
    "clock_time",
    "rfc3339",
    "date_time",
    "email",
    "uri",
    "uuid",
    "telegram_username",
    "slug",
    "rel_path",
    "entity_id",
    "text_short",
    "text",
    "text_long",
    "markdown",
    "md",
    "password",
    "otp",
    "json_object",
    "json_array",
    "hostname",
    "integer",
    "number",
    "year_month",
    "integer_string",
    "BuiltinKind",
    "string_kind",
]
