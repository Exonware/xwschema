"""FastAPI route exposing :data:`xwschema.BASE_TYPES`.

Mounts ``GET /types`` returning the canonical base-type catalogue plus
any caller-supplied product-specific extensions (e.g. hive-db's
encrypted variants). Keeps UIs driven off the real type registry so
new canonical types propagate automatically.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Iterable

from fastapi import APIRouter, Depends

from ..base_types import BASE_TYPES, BaseType, by_category as _by_category


# An "extras" entry uses the same shape as the response rows so callers
# can describe product-specific storage types (origin = their product).
TypeEntry = dict[str, Any]
ExtrasProvider = Callable[[], Iterable[TypeEntry] | Awaitable[Iterable[TypeEntry]]]


def _entry(bt: BaseType, *, origin: str = "xwschema", hive_compatible: bool | None = None) -> TypeEntry:
    row: TypeEntry = {
        "id": bt.id,
        "label": bt.label,
        "category": bt.category,
        "description": bt.description,
        "origin": origin,
    }
    if hive_compatible is not None:
        row["hive_compatible"] = hive_compatible
    return row


def mount_types_routes(
    router: APIRouter,
    *,
    user_dep: Callable[..., Any],
    extras: ExtrasProvider | None = None,
    canonical_flag: str | None = None,
    canonical_flag_ids: Iterable[str] | None = None,
) -> None:
    """Attach ``GET /types`` to ``router``.

    - ``user_dep``: auth dependency (returns current user).
    - ``extras``: optional sync/async callable returning additional
      type rows (dicts). Entries whose ``id`` equals an ``xwschema``
      base-type id are folded into the base row instead of duplicating.
    - ``canonical_flag`` + ``canonical_flag_ids``: optional label + id
      set — when provided, every canonical row gets ``{flag: id in ids}``
      so UIs can mark which canonical types are supported by the host
      product (e.g. ``hive_compatible=True``).
    """
    flag_ids: set[str] = set(canonical_flag_ids or ())

    @router.get("/types")
    async def types(_: Any = Depends(user_dep)) -> dict[str, Any]:
        xwschema_ids = {bt.id for bt in BASE_TYPES}

        canonical_rows: list[TypeEntry] = []
        for bt in BASE_TYPES:
            row = _entry(bt, origin="xwschema")
            if canonical_flag:
                row[canonical_flag] = bt.id in flag_ids
            canonical_rows.append(row)

        extra_rows: list[TypeEntry] = []
        if extras is not None:
            raw = extras()
            if hasattr(raw, "__await__"):
                raw = await raw  # type: ignore[assignment]
            for row in raw:  # type: ignore[assignment]
                if row.get("id") in xwschema_ids:
                    # Fold into the canonical row if the caller wanted to
                    # attach storage-specific metadata on top of the base.
                    for canonical in canonical_rows:
                        if canonical["id"] == row["id"]:
                            canonical.update({k: v for k, v in row.items() if k not in ("id", "label", "category", "description")})
                            break
                else:
                    extra_rows.append(row)

        return {
            "types": canonical_rows + extra_rows,
            "by_category": {k: [bt.id for bt in v] for k, v in _by_category().items()},
        }
