"""
xwschema: Schema validation and data structure definition library
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.4.0.16
Generation Date: 09-Nov-2025
"""
# xwlazy (lazy install hook), xwsystem, xwdata are required; no fallbacks
# Public API

# GUIDE_00_MASTER: lazy install registration (before other package imports)
try:
    from exonware.xwlazy import config_package_lazy_install_enabled

    config_package_lazy_install_enabled(
        __package__ or "exonware.xwschema",
        enabled=True,
        mode="smart",
    )
except ImportError:
    pass

from .facade import XWSchema
from .defs import (
    SchemaFormat,
    ValidationMode,
    SchemaGenerationMode,
    ConstraintType,
    XW_EXONWARE_BUILTIN_ID_KEY,
    XW_EXONWARE_KIND_ALIASES_KEY,
)
from .config import XWSchemaConfig, ValidationConfig, GenerationConfig, PerformanceConfig
from .builder import XWSchemaBuilder
from .validator import ValidationIssue
from .type_utils import class_to_string, string_to_class, normalize_type, normalize_schema_dict
from .types_base import (
    BuiltinKind,
    string_kind,
    param_marker,
    kinds,
    schemas,
    string_type,
    clock_time,
    date_time,
    email,
    entity_id,
    hostname,
    integer,
    integer_string,
    iso_date,
    json_array,
    json_object,
    markdown,
    md,
    number,
    otp,
    password,
    rel_path,
    rfc3339,
    slug,
    telegram_username,
    text,
    text_long,
    text_short,
    uri,
    uuid,
    year_month,
    kind_for,
    schema_for,
    schema_fragment,
    aliases,
    param_name_to_kind,
    json_schema_format_to_kind,
    kind_id_for_json_schema_format,
    kind_for_param_name,
    one_of_kinds,
    help_example_for_param,
    help_pattern_for_param,
    validate_builtin_patterns,
)
# ``types_basic`` merged into ``types_base``: same module, second import path + package attribute.
import sys as _sys

_pkg = __package__ or "exonware.xwschema"
_types_base_mod = _sys.modules[_pkg + ".types_base"]
_sys.modules.setdefault(_pkg + ".types_basic", _types_base_mod)
types_basic = _types_base_mod
# Backward-compatible names (older imports). Prefer ``kind_for``, ``schema_for``, ``kinds``, ``string_type``, …
XWSchemaLogicalType = BuiltinKind
XWSchemaStringType = string_kind
XWSchemaParamType = param_marker
XW_SCHEMA_STRING_TYPES = kinds
XW_SCHEMA_LOGICAL_TYPES = kinds
XW_SCHEMA_STRING_SCHEMAS = schemas
xw_string_type = string_type
get_string_type = kind_for
get_string_schema = schema_for
get_kind = kind_for
SemanticStringKind = BuiltinKind
SEMANTIC_STRING_KINDS = kinds
ALIASES = aliases
PARAM_NAME_TO_KIND = param_name_to_kind
JSON_SCHEMA_FORMAT_TO_KIND = json_schema_format_to_kind
json_schema_string_fragment = schema_fragment
one_of_string_kinds = one_of_kinds
from .errors import (
    XWSchemaError,
    XWSchemaValidationError,
    XWSchemaTypeError,
    XWSchemaConstraintError,
    XWSchemaParseError,
    XWSchemaFormatError,
    XWSchemaReferenceError,
    XWSchemaGenerationError
)
from .version import __version__
__author__ = "eXonware Backend Team"
__email__ = "connect@exonware.com"
__company__ = "eXonware.com"
# Note: extract_properties, load_properties, extract_parameters, load_parameters
# are static methods on XWSchema class, accessible as XWSchema.extract_properties() etc.
# They are not exported here as separate functions to avoid confusion.
__all__ = [
    # Main API
    'XWSchema',
    'XWSchemaBuilder',
    'ValidationIssue',
    # Built-in logical kinds (``types_base``): canonical names
    'BuiltinKind',
    'string_kind',
    'param_marker',
    'kinds',
    'schemas',
    'string_type',
    'types_basic',
    'iso_date',
    'clock_time',
    'rfc3339',
    'date_time',
    'email',
    'uri',
    'uuid',
    'telegram_username',
    'slug',
    'rel_path',
    'entity_id',
    'text_short',
    'text',
    'text_long',
    'markdown',
    'md',
    'password',
    'otp',
    'json_object',
    'json_array',
    'hostname',
    'integer',
    'number',
    'year_month',
    'integer_string',
    'kind_for',
    'schema_for',
    'schema_fragment',
    'aliases',
    'param_name_to_kind',
    'json_schema_format_to_kind',
    'kind_id_for_json_schema_format',
    'kind_for_param_name',
    'one_of_kinds',
    'help_example_for_param',
    'help_pattern_for_param',
    'validate_builtin_patterns',
    # Backward-compatible names (older imports)
    'XWSchemaStringType',
    'XWSchemaLogicalType',
    'XW_SCHEMA_STRING_TYPES',
    'XW_SCHEMA_LOGICAL_TYPES',
    'XW_SCHEMA_STRING_SCHEMAS',
    'XWSchemaParamType',
    'xw_string_type',
    'get_string_type',
    'get_string_schema',
    'ALIASES',
    'PARAM_NAME_TO_KIND',
    'JSON_SCHEMA_FORMAT_TO_KIND',
    'get_kind',
    'SemanticStringKind',
    'SEMANTIC_STRING_KINDS',
    'json_schema_string_fragment',
    'one_of_string_kinds',
    # Type Utilities
    'class_to_string',
    'string_to_class',
    'normalize_type',
    'normalize_schema_dict',
    # Enums
    'SchemaFormat',
    'ValidationMode',
    'SchemaGenerationMode',
    'ConstraintType',
    'XW_EXONWARE_BUILTIN_ID_KEY',
    'XW_EXONWARE_KIND_ALIASES_KEY',
    # Configuration
    'XWSchemaConfig',
    'ValidationConfig',
    'GenerationConfig',
    'PerformanceConfig',
    # Errors
    'XWSchemaError',
    'XWSchemaValidationError',
    'XWSchemaTypeError',
    'XWSchemaConstraintError',
    'XWSchemaParseError',
    'XWSchemaFormatError',
    'XWSchemaReferenceError',
    'XWSchemaGenerationError',
]
