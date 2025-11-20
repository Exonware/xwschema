"""
xSchema new_3 Performance Package

Performance optimization utilities for xSchema new_3.
"""

from .hashing import structural_hash, fast_equality_check

__all__ = [
    'structural_hash',
    'fast_equality_check'
]
