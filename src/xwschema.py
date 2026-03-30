"""
Convenience module for importing {xwschema}.
This allows users to import the library in two ways:
1. import exonware.{xwschema}
2. import {xwschema}  # This convenience import
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.7
Generation Date: February 2, 2025
"""
# Import everything from the main package

from exonware.xwschema import *  # noqa: F401, F403
# Re-export version from source of truth (version.py via exonware.xwschema)
__version__ = __version__  # noqa: F405
