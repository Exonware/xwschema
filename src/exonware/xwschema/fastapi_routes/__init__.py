"""FastAPI router factories backed by xwschema primitives.

Exposes the canonical :data:`BASE_TYPES` catalogue over HTTP so UIs
(HIVE Studio's "create collection" form, …) can populate field-type
pickers without hard-coding the list. Products append their own
storage-specific types via the ``extras`` callback.
"""

from __future__ import annotations

from .types import mount_types_routes

__all__ = ["mount_types_routes"]
