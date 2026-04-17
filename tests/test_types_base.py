"""Full coverage for :mod:`exonware.xwschema.types_base` (catalog, helpers, validation)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import exonware.xwschema.types_base as tb
from exonware.xwschema.facade import XWSchema


def test_builtin_catalog_and_aliases() -> None:
    assert len(tb.kinds) > 0
    assert tb.schemas is tb.kinds
    for sch in tb._builtin_catalog:
        bid = sch._metadata.get("builtin_kind_id")
        if bid:
            assert tb.kinds[str(bid)] is sch
    assert tb.aliases.get("iso_date") == "date"
    assert tb.aliases.get("rfc3339") == "datetime"


def test_kind_for_direct_alias_and_unknown() -> None:
    d = tb.kind_for("date")
    assert d is tb.kinds["date"]
    assert tb.kind_for("DATE") is d
    assert tb.kind_for("iso_date") is d
    assert tb.kind_for("calendar_date") is d
    assert tb.kind_for("  no-such-kind-xyz  ") is None


def test_kind_id_for_json_schema_format() -> None:
    assert tb.kind_id_for_json_schema_format("email") == "email"
    # Spaces are normalized to ``-`` after ``_norm`` (hyphens in the input become ``_`` first).
    assert tb.kind_id_for_json_schema_format("  date time  ") == "datetime"
    assert tb.kind_id_for_json_schema_format("date-time") is None
    assert tb.kind_id_for_json_schema_format("unknown-format-xyz") is None


def test_kind_for_param_name() -> None:
    assert tb.kind_for_param_name("start_date") == "date"
    assert tb.kind_for_param_name("TCP_PORT") == "port"
    assert tb.kind_for_param_name("not_a_mapped_name_12345") is None


def test_schema_fragment_and_one_of() -> None:
    frag = tb.schema_fragment("slug")
    assert frag.get("type") == "string"
    assert "pattern" in frag
    with pytest.raises(KeyError, match="Unknown builtin kind"):
        tb.schema_fragment("not_a_real_kind")
    combo = tb.one_of_kinds("email", "uri")
    assert combo == {"oneOf": [tb.schema_fragment("email"), tb.schema_fragment("uri")]}
    assert tb.one_of_kinds() == {"oneOf": []}


def test_schema_for() -> None:
    assert tb.schema_for("uuid") is tb.kinds["uuid"]
    assert tb.schema_for("nope") is None


def test_resolve_kind_branches() -> None:
    email = tb.kind_for("email")
    assert tb._resolve_kind(param_name="anything", json_schema_format="email") is email
    assert tb._resolve_kind(param_name="start_date", json_schema_format=None) is tb.kind_for("date")
    assert tb._resolve_kind(param_name="unknown", json_schema_format="") is None
    assert tb._resolve_kind(param_name="unknown", json_schema_format=None) is None


def test_resolve_kind_format_mid_without_schema() -> None:
    """When ``format`` maps to an id that does not resolve, fall back to param-name hints."""
    with patch.dict(tb.json_schema_format_to_kind, {"__ghost_fmt__": "___missing_kind___"}, clear=False):
        assert tb.kind_id_for_json_schema_format("__ghost_fmt__") == "___missing_kind___"
        assert tb.kind_for("___missing_kind___") is None
        got = tb._resolve_kind(param_name="start_date", json_schema_format="__ghost_fmt__")
        assert got is tb.kind_for("date")


def test_help_example_and_pattern() -> None:
    assert tb.help_example_for_param(param_name="nope") is None
    ex = tb.help_example_for_param(param_name="start_date")
    assert ex and str(ex).strip() != ""
    assert tb.help_example_for_param(param_name="anything", json_schema_format="email") is not None
    assert tb.help_pattern_for_param(param_name="nope") is None
    pat = tb.help_pattern_for_param(param_name="short_id", json_schema_format=None)
    assert isinstance(pat, str) and len(pat) > 0
    assert tb.help_pattern_for_param(param_name="body") is None


def test_help_example_only_blank_examples_returns_first() -> None:
    mock_kind = MagicMock()
    mock_kind.to_native.return_value = {"examples": ["  ", "\t"]}

    def _fake_resolve(*, param_name: str, json_schema_format: str | None) -> MagicMock | None:
        return mock_kind

    with patch.object(tb, "_resolve_kind", side_effect=_fake_resolve):
        assert tb.help_example_for_param(param_name="x") == "  "


def test_help_example_no_examples() -> None:
    mock_kind = MagicMock()
    mock_kind.to_native.return_value = {"examples": []}

    with patch.object(tb, "_resolve_kind", return_value=mock_kind):
        assert tb.help_example_for_param(param_name="x") is None


def test_string_type_alias_cache_and_errors() -> None:
    cls = tb.string_type("iso_date")
    assert cls.__kind_id__ == "date"
    assert cls.__kind_schema__ is tb.kinds["date"]
    assert tb.string_type("date") is cls
    with pytest.raises(KeyError, match="Unknown builtin kind"):
        tb.string_type("___not_a_kind___")


def test_string_type_rebuild_doc_uses_canon_when_title_empty() -> None:
    cls_date = tb.string_type("date")
    tb._MARKERS.pop("date", None)
    sch = tb.kinds["date"]
    with patch.object(sch, "to_native", return_value={"title": "", "type": "string"}):
        cls2 = tb.string_type("date")
    assert cls2.__doc__ == "date"
    tb._MARKERS["date"] = cls_date


def test_param_marker_and_exports() -> None:
    assert issubclass(tb.slug, tb.param_marker)
    assert tb.BuiltinKind is XWSchema
    assert tb.string_kind is tb.string_type
    assert tb.text is tb.text_short
    assert tb.date_time is tb.rfc3339
    assert tb.md is tb.markdown


def test_rx() -> None:
    rx = tb._rx(r"^[a-z]+$")
    assert rx.fullmatch("abc")
    assert rx.fullmatch("ABC") is None


def test_example_numeric_value() -> None:
    assert tb._example_numeric_value(42, as_int=True) == 42
    assert tb._example_numeric_value(3.5, as_int=True) == 3
    assert tb._example_numeric_value(2.5, as_int=False) == 2.5
    assert tb._example_numeric_value("  -7 ", as_int=True) == -7
    assert tb._example_numeric_value("1.25", as_int=False) == 1.25
    with pytest.raises(TypeError, match="boolean is not a numeric example"):
        tb._example_numeric_value(True, as_int=True)


def test_builtin_dict_maps_optional_keys() -> None:
    d = tb._builtin_dict(
        "t_array",
        "Array T",
        "desc",
        json_type="array",
        items_schema=None,
        min_items=1,
        max_items=3,
        examples=([1],),
        kind_aliases=("a1",),
    )
    assert d["type"] == "array"
    assert d["items"] == {}
    assert d["minItems"] == 1
    assert d["maxItems"] == 3
    obj = tb._builtin_dict(
        "t_obj",
        "Obj T",
        "desc",
        json_type="object",
        additional_properties={"type": "string"},
        examples=({"k": "v"},),
        kind_aliases=(),
    )
    assert obj["additionalProperties"] == {"type": "string"}
    num = tb._builtin_dict(
        "t_num",
        "Num T",
        "desc",
        json_type="number",
        minimum=0.0,
        maximum=10.0,
        exclusive_minimum=1.0,
        exclusive_maximum=9.0,
        multiple_of=0.5,
        examples=(2.0,),
        format=None,
    )
    assert num["minimum"] == 0.0
    assert num["exclusiveMinimum"] == 1.0
    assert num["multipleOf"] == 0.5
    en = tb._builtin_dict(
        "t_enum",
        "E",
        "d",
        enum_choices=("a", "b"),
        examples=("a",),
        kind_aliases=("bee",),
    )
    assert en["enum"] == ["a", "b"]


def test_validate_builtin_patterns_happy_path() -> None:
    tb.validate_builtin_patterns()


@pytest.mark.parametrize(
    ("factory", "match"),
    [
        (
            lambda: XWSchema(
                tb._builtin_dict(
                    "badpat",
                    "t",
                    "d",
                    pattern=r"^[a-z]+$",
                    examples=("BAD",),
                    kind_aliases=(),
                )
            ),
            "does not match",
        ),
        (
            lambda: XWSchema(
                tb._builtin_dict(
                    "badint_min",
                    "t",
                    "d",
                    json_type="integer",
                    minimum=10,
                    examples=(1,),
                    kind_aliases=(),
                )
            ),
            "below minimum",
        ),
        (
            lambda: XWSchema(
                tb._builtin_dict(
                    "badint_max",
                    "t",
                    "d",
                    json_type="integer",
                    maximum=5,
                    examples=(9,),
                    kind_aliases=(),
                )
            ),
            "above maximum",
        ),
        (
            lambda: XWSchema(
                tb._builtin_dict(
                    "badint_mo",
                    "t",
                    "d",
                    json_type="integer",
                    multiple_of=3,
                    examples=(4,),
                    kind_aliases=(),
                )
            ),
            "multipleOf",
        ),
        (
            lambda: XWSchema(
                tb._builtin_dict(
                    "badnum_min",
                    "t",
                    "d",
                    json_type="number",
                    minimum=1.0,
                    examples=(0.5,),
                    kind_aliases=(),
                )
            ),
            "below minimum",
        ),
        (
            lambda: XWSchema(
                tb._builtin_dict(
                    "badnum_max",
                    "t",
                    "d",
                    json_type="number",
                    maximum=1.0,
                    examples=(2.0,),
                    kind_aliases=(),
                )
            ),
            "above maximum",
        ),
        (
            lambda: XWSchema(
                tb._builtin_dict(
                    "badnum_mo",
                    "t",
                    "d",
                    json_type="number",
                    multiple_of=0.3,
                    examples=(0.2,),
                    kind_aliases=(),
                )
            ),
            "multipleOf",
        ),
        (
            lambda: XWSchema(
                tb._builtin_dict(
                    "badbool",
                    "t",
                    "d",
                    json_type="boolean",
                    examples=("maybe",),
                    kind_aliases=(),
                )
            ),
            "not a boolean",
        ),
        (
            lambda: XWSchema(
                tb._builtin_dict(
                    "badarr",
                    "t",
                    "d",
                    json_type="array",
                    items_schema={},
                    examples=("not-list",),
                    kind_aliases=(),
                )
            ),
            "not a JSON array",
        ),
        (
            lambda: XWSchema(
                tb._builtin_dict(
                    "badarr_min",
                    "t",
                    "d",
                    json_type="array",
                    items_schema={},
                    min_items=2,
                    examples=([1],),
                    kind_aliases=(),
                )
            ),
            "shorter than minItems",
        ),
        (
            lambda: XWSchema(
                tb._builtin_dict(
                    "badarr_max",
                    "t",
                    "d",
                    json_type="array",
                    items_schema={},
                    max_items=1,
                    examples=([1, 2],),
                    kind_aliases=(),
                )
            ),
            "longer than maxItems",
        ),
        (
            lambda: XWSchema(
                tb._builtin_dict(
                    "badobj",
                    "t",
                    "d",
                    json_type="object",
                    additional_properties=True,
                    examples=([1, 2],),
                    kind_aliases=(),
                )
            ),
            "not a JSON object",
        ),
        (
            lambda: XWSchema(
                tb._builtin_dict(
                    "badenum",
                    "t",
                    "d",
                    enum_choices=("a", "b"),
                    examples=("c",),
                    kind_aliases=(),
                )
            ),
            "not in enum",
        ),
    ],
)
def test_validate_builtin_patterns_errors(factory: object, match: str) -> None:
    bad = factory()  # type: ignore[operator]
    with patch.object(tb, "kinds", {"__bad__": bad}):
        with pytest.raises(ValueError, match=match):
            tb.validate_builtin_patterns()


def test_validate_boolean_examples_as_native_python_bool() -> None:
    """When ``to_native()`` still has real ``bool`` examples, the fast-path ``continue`` runs."""
    sch = XWSchema(
        tb._builtin_dict(
            "boolnative",
            "t",
            "d",
            json_type="boolean",
            examples=(True, False),
            kind_aliases=(),
        )
    )
    with patch.object(
        sch,
        "to_native",
        return_value={"type": "boolean", "examples": [True, False], "enum": None},
    ):
        with patch.object(tb, "kinds", {"boolnative": sch}):
            tb.validate_builtin_patterns()


def test_validate_boolean_examples_as_true_false_strings() -> None:
    sch = XWSchema(
        tb._builtin_dict(
            "boolstr",
            "t",
            "d",
            json_type="boolean",
            examples=("true", "FALSE"),
            kind_aliases=(),
        )
    )
    with patch.object(tb, "kinds", {"boolstr": sch}):
        tb.validate_builtin_patterns()


def test_validate_unknown_json_type_skips_typed_branches() -> None:
    """``type`` values outside the handled set skip typed checks (no ``enum`` → no failure)."""
    sch = XWSchema({"type": "null", "title": "n", "description": "d", "examples": [None]})
    with patch.object(tb, "kinds", {"nullish": sch}):
        tb.validate_builtin_patterns()


def test_validate_string_without_pattern_still_runs_enum_block() -> None:
    """``type: string`` with no ``pattern`` skips regex checks; trailing ``enum`` block still applies."""
    ok = XWSchema(
        tb._builtin_dict(
            "str_no_pat",
            "t",
            "d",
            json_type="string",
            pattern=None,
            min_length=0,
            max_length=10,
            examples=("x",),
            enum_choices=("x", "y"),
            kind_aliases=(),
        )
    )
    with patch.object(tb, "kinds", {"str_no_pat": ok}):
        tb.validate_builtin_patterns()
