#!/usr/bin/env python3
"""
Unit tests for XWSchema configuration.

Tests configuration classes:
- XWSchemaConfig
- ValidationConfig
- GenerationConfig
- PerformanceConfig

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.1
Generation Date: 09-Nov-2025
"""

import pytest
from exonware.xwschema.config import (
    XWSchemaConfig,
    ValidationConfig,
    GenerationConfig,
    PerformanceConfig
)
from exonware.xwschema.defs import ValidationMode, SchemaGenerationMode


@pytest.mark.xwschema_unit
class TestXWSchemaConfig:
    """Test XWSchemaConfig."""
    
    def test_config_init_default(self):
        """Test config initialization with defaults."""
        config = XWSchemaConfig()
        assert config is not None
    
    def test_config_init_with_validation(self):
        """Test config initialization with validation config."""
        validation = ValidationConfig()
        config = XWSchemaConfig(validation=validation)
        assert config.validation == validation
    
    def test_config_init_with_generation(self):
        """Test config initialization with generation config."""
        generation = GenerationConfig()
        config = XWSchemaConfig(generation=generation)
        assert config.generation == generation
    
    def test_config_init_with_performance(self):
        """Test config initialization with performance config."""
        performance = PerformanceConfig()
        config = XWSchemaConfig(performance=performance)
        assert config.performance == performance
    
    def test_config_default_factory(self):
        """Test default() factory method."""
        config = XWSchemaConfig.default()
        assert config is not None
        assert isinstance(config, XWSchemaConfig)
    
    def test_config_copy(self):
        """Test config copy method."""
        config = XWSchemaConfig()
        copied = config.copy()
        assert copied is not None
        assert copied is not config


@pytest.mark.xwschema_unit
class TestValidationConfig:
    """Test ValidationConfig."""
    
    def test_validation_config_init_default(self):
        """Test validation config initialization with defaults."""
        config = ValidationConfig()
        assert config is not None
    
    def test_validation_config_init_with_mode(self):
        """Test validation config initialization with mode."""
        config = ValidationConfig(mode=ValidationMode.STRICT)
        assert config.mode == ValidationMode.STRICT
    
    def test_validation_config_init_with_loose_mode(self):
        """Test validation config initialization with loose mode."""
        config = ValidationConfig(mode=ValidationMode.LAX)
        assert config.mode == ValidationMode.LAX
    
    def test_validation_config_enable_cache(self):
        """Test enabling validation cache."""
        config = ValidationConfig()
        config.enable_cache = True
        assert config.enable_cache is True
    
    def test_validation_config_cache_size(self):
        """Test setting cache size."""
        config = ValidationConfig()
        config.cache_size = 1000
        assert config.cache_size == 1000


@pytest.mark.xwschema_unit
class TestGenerationConfig:
    """Test GenerationConfig."""
    
    def test_generation_config_init_default(self):
        """Test generation config initialization with defaults."""
        config = GenerationConfig()
        assert config is not None
    
    def test_generation_config_init_with_mode(self):
        """Test generation config initialization with mode."""
        config = GenerationConfig(mode=SchemaGenerationMode.MINIMAL)
        assert config.mode == SchemaGenerationMode.MINIMAL
    
    def test_generation_config_init_with_infer_mode(self):
        """Test generation config initialization with infer mode."""
        config = GenerationConfig(mode=SchemaGenerationMode.INFER)
        assert config.mode == SchemaGenerationMode.INFER
    
    def test_generation_config_init_with_comprehensive_mode(self):
        """Test generation config initialization with comprehensive mode."""
        config = GenerationConfig(mode=SchemaGenerationMode.COMPREHENSIVE)
        assert config.mode == SchemaGenerationMode.COMPREHENSIVE
    
    def test_generation_config_init_with_strict_mode(self):
        """Test generation config initialization with strict mode."""
        config = GenerationConfig(mode=SchemaGenerationMode.STRICT)
        assert config.mode == SchemaGenerationMode.STRICT


@pytest.mark.xwschema_unit
class TestPerformanceConfig:
    """Test PerformanceConfig."""
    
    def test_performance_config_init_default(self):
        """Test performance config initialization with defaults."""
        config = PerformanceConfig()
        assert config is not None
    
    def test_performance_config_enable_cache(self):
        """Test enabling performance cache."""
        config = PerformanceConfig()
        config.enable_cache = True
        assert config.enable_cache is True
    
    def test_performance_config_cache_size(self):
        """Test setting cache size."""
        config = PerformanceConfig()
        config.cache_size = 5000
        assert config.cache_size == 5000
    
    def test_performance_config_enable_parallel(self):
        """Test enabling parallel processing."""
        config = PerformanceConfig()
        config.enable_parallel = True
        assert config.enable_parallel is True

