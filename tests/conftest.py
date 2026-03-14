"""
Shared pytest fixtures for xwschema tests.
"""

from __future__ import annotations
import pytest


@pytest.fixture(autouse=True)
def _reset_xwschema_globals():
    """
    Ensure test isolation.
    xwschema uses module-level caches on XWSchema (extraction cache).
    We reset their in-memory state between tests.
    """
    from exonware.xwschema.facade import XWSchema
    XWSchema._clear_extraction_cache()
    yield
