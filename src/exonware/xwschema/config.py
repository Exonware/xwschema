#!/usr/bin/env python3
"""
#exonware/xwschema/src/exonware/xwschema/config.py

XWSchema Configuration System

This module provides fluent configuration for xwschema with builder pattern
and sensible defaults for different use cases.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 09-Nov-2025
"""

from dataclasses import dataclass, field, replace
from typing import Optional, Any
from pathlib import Path
import copy

from .defs import SchemaFormat, ValidationMode, SchemaGenerationMode


# ==============================================================================
# DEFAULT CONSTANTS
# ==============================================================================

DEFAULT_CACHE_SIZE = 1000
DEFAULT_MAX_SCHEMA_SIZE_MB = 10
DEFAULT_MAX_NESTING_DEPTH = 50
DEFAULT_TIMEOUT_SECONDS = 30


# ==============================================================================
# VALIDATION CONFIGURATION
# ==============================================================================

@dataclass
class ValidationConfig:
    """Validation configuration."""
    
    mode: ValidationMode = ValidationMode.STRICT
    stop_on_first_error: bool = False
    collect_all_errors: bool = True
    enable_type_coercion: bool = False
    enable_format_validation: bool = True
    enable_custom_validators: bool = True
    max_errors: int = 100
    
    @classmethod
    def strict(cls) -> 'ValidationConfig':
        """Strict validation mode."""
        return cls(
            mode=ValidationMode.STRICT,
            stop_on_first_error=False,
            collect_all_errors=True,
            enable_type_coercion=False,
            enable_format_validation=True
        )
    
    @classmethod
    def lax(cls) -> 'ValidationConfig':
        """Lax validation mode (warnings only)."""
        return cls(
            mode=ValidationMode.LAX,
            stop_on_first_error=False,
            collect_all_errors=True,
            enable_type_coercion=True,
            enable_format_validation=False
        )


# ==============================================================================
# GENERATION CONFIGURATION
# ==============================================================================

@dataclass
class GenerationConfig:
    """Schema generation configuration."""
    
    mode: SchemaGenerationMode = SchemaGenerationMode.INFER
    include_examples: bool = False
    include_descriptions: bool = False
    infer_required: bool = True
    infer_enums: bool = True
    infer_patterns: bool = False
    infer_ranges: bool = False
    max_enum_values: int = 10
    
    @classmethod
    def minimal(cls) -> 'GenerationConfig':
        """Minimal schema generation (types only)."""
        return cls(
            mode=SchemaGenerationMode.MINIMAL,
            include_examples=False,
            include_descriptions=False,
            infer_required=False,
            infer_enums=False
        )
    
    @classmethod
    def comprehensive(cls) -> 'GenerationConfig':
        """Comprehensive schema generation."""
        return cls(
            mode=SchemaGenerationMode.COMPREHENSIVE,
            include_examples=True,
            include_descriptions=True,
            infer_required=True,
            infer_enums=True,
            infer_patterns=True,
            infer_ranges=True
        )


# ==============================================================================
# PERFORMANCE CONFIGURATION
# ==============================================================================

@dataclass
class PerformanceConfig:
    """Performance configuration for optimization."""
    
    enable_caching: bool = True
    cache_size: int = DEFAULT_CACHE_SIZE
    enable_validation_cache: bool = True
    enable_schema_cache: bool = True
    enable_parallel_validation: bool = False
    max_workers: int = 4
    
    @classmethod
    def fast(cls) -> 'PerformanceConfig':
        """High performance mode."""
        return cls(
            enable_caching=True,
            cache_size=5000,
            enable_validation_cache=True,
            enable_schema_cache=True,
            enable_parallel_validation=True,
            max_workers=8
        )
    
    @classmethod
    def memory_optimized(cls) -> 'PerformanceConfig':
        """Memory-efficient mode."""
        return cls(
            enable_caching=False,
            cache_size=100,
            enable_validation_cache=False,
            enable_schema_cache=False,
            enable_parallel_validation=False
        )


# ==============================================================================
# MAIN CONFIGURATION
# ==============================================================================

@dataclass
class XWSchemaConfig:
    """
    Main configuration for XWSchema.
    
    Provides fluent builder pattern and sensible defaults.
    """
    
    # Format settings
    default_format: SchemaFormat = SchemaFormat.JSON_SCHEMA
    auto_detect_format: bool = True
    
    # Validation settings
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    
    # Generation settings
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    
    # Performance settings
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Security settings
    max_schema_size_mb: int = DEFAULT_MAX_SCHEMA_SIZE_MB
    max_nesting_depth: int = DEFAULT_MAX_NESTING_DEPTH
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    
    # Schema reference resolution
    enable_reference_resolution: bool = True
    reference_base_path: Optional[Path] = None
    
    @classmethod
    def default(cls) -> 'XWSchemaConfig':
        """Create default configuration."""
        return cls()
    
    @classmethod
    def strict(cls) -> 'XWSchemaConfig':
        """Create strict validation configuration."""
        return cls(
            validation=ValidationConfig.strict(),
            generation=GenerationConfig.minimal()
        )
    
    @classmethod
    def fast(cls) -> 'XWSchemaConfig':
        """Create high-performance configuration."""
        return cls(
            performance=PerformanceConfig.fast(),
            validation=ValidationConfig.strict()
        )
    
    @classmethod
    def development(cls) -> 'XWSchemaConfig':
        """Create development-friendly configuration."""
        return cls(
            validation=ValidationConfig.lax(),
            generation=GenerationConfig.comprehensive(),
            performance=PerformanceConfig.fast()
        )
    
    def copy(self) -> 'XWSchemaConfig':
        """Create a deep copy of this configuration."""
        return copy.deepcopy(self)

