#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/registry/defs.py

Schema Registry Definitions

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from enum import Enum


class CompatibilityLevel(Enum):
    """Schema compatibility levels."""
    NONE = "NONE"
    BACKWARD = "BACKWARD"
    FORWARD = "FORWARD"
    FULL = "FULL"
    BACKWARD_TRANSITIVE = "BACKWARD_TRANSITIVE"
    FORWARD_TRANSITIVE = "FORWARD_TRANSITIVE"
    FULL_TRANSITIVE = "FULL_TRANSITIVE"
