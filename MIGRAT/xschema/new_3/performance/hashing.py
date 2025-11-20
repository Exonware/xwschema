"""
xSchema new_3 Performance Hashing

Performance optimization utilities for xSchema new_3.
"""

import hashlib
import json
from typing import Any, Dict, Union


def structural_hash(data: Any) -> int:
    """
    Generate a structural hash for data.
    
    This is a simplified implementation that provides
    a hash based on the structure and content of the data.
    """
    if data is None:
        return hash(None)
    
    # Convert to JSON string for consistent hashing
    try:
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hash(json_str)
    except (TypeError, ValueError):
        # Fallback to object hash
        return hash(str(data))


def fast_equality_check(data1: Any, data2: Any) -> bool:
    """
    Fast equality check for data structures.
    
    This is a simplified implementation that provides
    quick equality checking for data structures.
    """
    if data1 is data2:
        return True
    
    if type(data1) != type(data2):
        return False
    
    if isinstance(data1, dict):
        if len(data1) != len(data2):
            return False
        for key in data1:
            if key not in data2:
                return False
            if not fast_equality_check(data1[key], data2[key]):
                return False
        return True
    
    elif isinstance(data1, list):
        if len(data1) != len(data2):
            return False
        for i, item in enumerate(data1):
            if not fast_equality_check(item, data2[i]):
                return False
        return True
    
    else:
        return data1 == data2
