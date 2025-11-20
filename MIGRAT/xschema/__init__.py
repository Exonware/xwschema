"""
xSchema Library
==============

A comprehensive schema management library for xData ecosystem.
Provides schema validation, generation, and management capabilities.

Versions:
- legacy: Original xSchema implementation
- new: First major refactor
- new_2: Second major refactor  
- new_3: Latest version (current)
"""

import logging
from typing import Dict, Any, Union, Optional

logger = logging.getLogger(__name__)

# Import the current version (new_3)
try:
    from .new_3 import *
    from .new_3.facade import xSchema
    __version__ = "3.0.0"
    logger.info("🚀 xSchema v3.0.0 loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ xSchema v3.0.0 not available: {e}")
    try:
        from .new_2 import *
        from .new_2.facade import xSchema
        __version__ = "2.0.0"
        logger.info("🚀 xSchema v2.0.0 loaded successfully")
    except ImportError as e:
        logger.warning(f"⚠️ xSchema v2.0.0 not available: {e}")
        try:
            from .new import *
            from .new.facade import xSchema
            __version__ = "1.0.0"
            logger.info("🚀 xSchema v1.0.0 loaded successfully")
        except ImportError as e:
            logger.warning(f"⚠️ xSchema v1.0.0 not available: {e}")
            try:
                from .legacy import *
                from .legacy.facade import xSchema
                __version__ = "0.1.0"
                logger.info("🚀 xSchema v0.1.0 (legacy) loaded successfully")
            except ImportError as e:
                logger.error(f"❌ No xSchema version available: {e}")
                raise ImportError("No xSchema version could be loaded") from e

__all__ = [
    'xSchema',
    '__version__',
]
