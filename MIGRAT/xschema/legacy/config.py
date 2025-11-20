#!/usr/bin/env python3
"""
⚙️ xSchema Configuration Module
Configuration classes for secure, performant, and type-safe xSchema operations.
Adapted from xData configuration for schema-specific needs.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

from src.xlib.xdata.core.enums import RefLoad, RefResolve, RefCopy
from src.xlib.xsystem.monitoring.performance_monitor import logger, create_performance_monitor
from src.xlib.xsystem.security.path_validator import PathValidator
from src.xlib.xsystem.threading.locks import EnhancedRLock
from src.xlib.xsystem.structures.circular_detector import CircularReferenceDetector

# Constants for schema operations
DEFAULT_MAX_FILE_SIZE_MB = 100.0
DEFAULT_MAX_MEMORY_USAGE_MB = 500.0
DEFAULT_MAX_DICT_DEPTH = 100
DEFAULT_MAX_TO_DICT_SIZE_MB = 50.0
DEFAULT_LOCK_TIMEOUT = 30.0
DEFAULT_MAX_CIRCULAR_DEPTH = 50
DEFAULT_ENCODING = 'utf-8'
DEFAULT_PATH_DELIMITER = '.'

# Schema type mapping for validation
SCHEMA_TYPE_MAPPING = {
    'string': str,
    'integer': int,
    'number': float,
    'boolean': bool,
    'array': list,
    'object': dict,
    'null': type(None)
}

# Forward declarations for type hints
if False:  # TYPE_CHECKING
    from ...xsystem.monitoring.performance_monitor import PerformanceMonitor


@dataclass(frozen=True)
class xSchemaSecurityConfig:
    """🔒 Security configuration with immutable, type-safe settings."""
    enable_path_security: bool = False
    allow_absolute_paths: bool = True
    max_path_length: int = 4096
    max_path_depth: int = 100
    
    def create_path_validator(self, base_path: Optional[str] = None) -> Optional['PathValidator']:
        """Create PathValidator instance if security is enabled."""
        if not self.enable_path_security:
            return None
        return PathValidator(
            base_path=base_path,
            allow_absolute=self.allow_absolute_paths,
            max_path_length=self.max_path_length,
            check_existence=False
        )


@dataclass(frozen=True)
class xSchemaPerformanceConfig:
    """🚀 Performance configuration with standard defaults."""
    enable_monitoring: bool = False
    enable_memory_monitoring: bool = True
    max_file_size_mb: float = DEFAULT_MAX_FILE_SIZE_MB
    max_memory_usage_mb: float = DEFAULT_MAX_MEMORY_USAGE_MB
    max_dict_depth: int = DEFAULT_MAX_DICT_DEPTH
    max_to_dict_size_mb: float = DEFAULT_MAX_TO_DICT_SIZE_MB
    
    def create_monitor(self) -> Optional['PerformanceMonitor']:
        """Create PerformanceMonitor if monitoring is enabled."""
        if not self.enable_monitoring:
            return None
        return create_performance_monitor(
            enabled=True,
            enable_memory_monitoring=self.enable_memory_monitoring
        )


@dataclass(frozen=True)
class xSchemaThreadingConfig:
    """🔐 Threading configuration for concurrent access."""
    enable_thread_safety: bool = False
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT
    
    def create_lock(self, instance_id: int) -> Optional['EnhancedRLock']:
        """Create EnhancedRLock if threading is enabled."""
        if not self.enable_thread_safety:
            return None
        return EnhancedRLock(
            timeout=self.lock_timeout, 
            name=f"xSchema-{instance_id}"
        )


@dataclass(frozen=True)
class xSchemaValidationConfig:
    """📋 Validation configuration for schema operations."""
    enable_strict_validation: bool = True
    allow_unknown_properties: bool = False
    validate_required_fields: bool = True
    validate_type_constraints: bool = True
    validate_format_constraints: bool = True
    validate_enum_constraints: bool = True
    validate_numeric_constraints: bool = True
    validate_pattern_constraints: bool = True
    validate_array_constraints: bool = True
    validate_object_constraints: bool = True
    max_validation_errors: int = 100


@dataclass(frozen=True)
class xSchemaReferenceConfig:
    """🔗 Reference handling configuration for schemas."""
    handle_references: Optional[str] = None
    resolve_schema_references: Optional[str] = None  # Schema-specific reference resolution
    user_defined_links: Optional[Dict[str, str]] = None
    max_circular_depth: int = DEFAULT_MAX_CIRCULAR_DEPTH
    
    def create_circular_detector(self) -> 'CircularReferenceDetector':
        """Create CircularReferenceDetector instance."""
        return CircularReferenceDetector(max_depth=self.max_circular_depth)


@dataclass(frozen=True)
class xSchemaEncodingConfig:
    """📝 Encoding configuration for schema operations."""
    default_encoding: str = DEFAULT_ENCODING
    allow_encoding_detection: bool = True
    fallback_encodings: list = field(default_factory=lambda: ['utf-8', 'latin-1', 'ascii'])


@dataclass(frozen=True)
class xSchemaPathConfig:
    """📂 Path configuration for schema operations."""
    path_delimiter: str = DEFAULT_PATH_DELIMITER
    allow_nested_access: bool = True
    create_missing_paths: bool = True
    max_path_depth: int = 100


@dataclass(frozen=True)
class xSchemaConfig:
    """Master configuration container for type safety and validation."""
    security: xSchemaSecurityConfig = field(default_factory=xSchemaSecurityConfig)
    performance: xSchemaPerformanceConfig = field(default_factory=xSchemaPerformanceConfig) 
    threading: xSchemaThreadingConfig = field(default_factory=xSchemaThreadingConfig)
    validation: xSchemaValidationConfig = field(default_factory=xSchemaValidationConfig)
    references: xSchemaReferenceConfig = field(default_factory=xSchemaReferenceConfig)
    encoding: xSchemaEncodingConfig = field(default_factory=xSchemaEncodingConfig)
    path: xSchemaPathConfig = field(default_factory=xSchemaPathConfig)
    
    # Processing options
    wrap_nested_fields: bool = False
    
    @classmethod
    def from_kwargs(cls, **kwargs: Any) -> 'xSchemaConfig':
        """Create configuration from keyword arguments with smart defaults."""
        # Extract security options
        security_opts = {k.replace('security_', ''): v for k, v in kwargs.items() 
                        if k.startswith('security_') or k in ('enable_path_security', 'allow_absolute_paths', 'max_path_length', 'max_path_depth')}
        security_opts = {k.replace('enable_path_', 'enable_path_'): v for k, v in security_opts.items()}
        
        # Extract performance options  
        perf_opts = {k.replace('performance_', ''): v for k, v in kwargs.items()
                    if k.startswith('performance_') or k in ('enable_performance_monitoring', 'enable_memory_monitoring', 'max_file_size_mb', 'max_memory_usage_mb', 'max_dict_depth', 'max_to_dict_size_mb')}
        perf_opts = {k.replace('enable_performance_monitoring', 'enable_monitoring'): v for k, v in perf_opts.items()}
        
        # Extract threading options
        thread_opts = {k.replace('threading_', ''): v for k, v in kwargs.items()
                      if k.startswith('threading_') or k in ('enable_thread_safety', 'lock_timeout')}
        
        # Extract validation options
        validation_opts = {k.replace('validation_', ''): v for k, v in kwargs.items()
                          if k.startswith('validation_') or k in ('enable_strict_validation', 'allow_unknown_properties', 'validate_required_fields', 'validate_type_constraints', 'validate_format_constraints', 'validate_enum_constraints', 'validate_numeric_constraints', 'validate_pattern_constraints', 'validate_array_constraints', 'validate_object_constraints', 'max_validation_errors')}
        
        # Extract reference options
        ref_opts = {}
        for k, v in kwargs.items():
            if k == 'reference_mode':
                ref_opts['handle_references'] = v  # Map reference_mode to handle_references
            elif k in ('handle_references', 'resolve_schema_references', 'user_defined_links', 'max_circular_depth'):
                ref_opts[k] = v
            elif k.startswith('reference_'):
                ref_opts[k.replace('reference_', '')] = v
        
        # Extract encoding options
        encoding_opts = {k.replace('encoding_', ''): v for k, v in kwargs.items()
                        if k.startswith('encoding_') or k in ('default_encoding', 'allow_encoding_detection', 'fallback_encodings')}
        
        # Extract path options
        path_opts = {k.replace('path_', ''): v for k, v in kwargs.items()
                    if k.startswith('path_') or k in ('path_delimiter', 'allow_nested_access', 'create_missing_paths', 'max_path_depth')}
        
        return cls(
            security=xSchemaSecurityConfig(**{k: v for k, v in security_opts.items() if k in ('enable_path_security', 'allow_absolute_paths', 'max_path_length', 'max_path_depth')}),
            performance=xSchemaPerformanceConfig(**{k: v for k, v in perf_opts.items() if k in ('enable_monitoring', 'enable_memory_monitoring', 'max_file_size_mb', 'max_memory_usage_mb', 'max_dict_depth', 'max_to_dict_size_mb')}),
            threading=xSchemaThreadingConfig(**{k: v for k, v in thread_opts.items() if k in ('enable_thread_safety', 'lock_timeout')}),
            validation=xSchemaValidationConfig(**{k: v for k, v in validation_opts.items() if k in ('enable_strict_validation', 'allow_unknown_properties', 'validate_required_fields', 'validate_type_constraints', 'validate_format_constraints', 'validate_enum_constraints', 'validate_numeric_constraints', 'validate_pattern_constraints', 'validate_array_constraints', 'validate_object_constraints', 'max_validation_errors')}),
            references=xSchemaReferenceConfig(**{k: v for k, v in ref_opts.items() if k in ('handle_references', 'resolve_schema_references', 'user_defined_links', 'max_circular_depth')}),
            encoding=xSchemaEncodingConfig(**{k: v for k, v in encoding_opts.items() if k in ('default_encoding', 'allow_encoding_detection', 'fallback_encodings')}),
            path=xSchemaPathConfig(**{k: v for k, v in path_opts.items() if k in ('path_delimiter', 'allow_nested_access', 'create_missing_paths', 'max_path_depth')}),
            wrap_nested_fields=kwargs.get('wrap_nested_fields', False)
        ) 