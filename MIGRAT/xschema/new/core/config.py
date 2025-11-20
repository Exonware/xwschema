"""
Performance Configuration for XSchema Composition API

Central configuration system to control performance-impacting features.
Allows switching between development and production modes for optimal performance.
"""

import os
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class PerformanceConfig:
    """Configuration for XSchema performance settings."""
    
    # Core performance flags
    production_mode: bool = False
    enable_logging: bool = True
    enable_debug_logging: bool = True
    enable_validation: bool = True
    enable_performance_monitoring: bool = False
    enable_schema_validation: bool = True
    
    # Caching and pooling
    enable_schema_caching: bool = True
    enable_processor_caching: bool = True
    cache_size_limit: int = 1000
    pool_size_limit: int = 100
    
    # Memory and size limits
    max_schema_size_mb: float = 50.0
    max_memory_mb: float = 256.0
    
    # Hot path optimizations
    enable_direct_access: bool = True
    enable_inline_methods: bool = True
    enable_fast_validation: bool = True
    
    @classmethod
    def from_environment(cls) -> 'PerformanceConfig':
        """Create configuration from environment variables."""
        return cls(
            production_mode=os.getenv('XSCHEMA_PRODUCTION', 'false').lower() == 'true',
            enable_logging=os.getenv('XSCHEMA_LOGGING', 'true').lower() == 'true',
            enable_debug_logging=os.getenv('XSCHEMA_DEBUG', 'true').lower() == 'true',
            enable_validation=os.getenv('XSCHEMA_VALIDATION', 'true').lower() == 'true',
            enable_performance_monitoring=os.getenv('XSCHEMA_MONITORING', 'false').lower() == 'true',
            cache_size_limit=int(os.getenv('XSCHEMA_CACHE_SIZE', '1000')),
            pool_size_limit=int(os.getenv('XSCHEMA_POOL_SIZE', '100')),
        )
    
    def set_production_mode(self):
        """Optimize all settings for production performance."""
        self.production_mode = True
        self.enable_logging = False
        self.enable_debug_logging = False
        self.enable_validation = False
        self.enable_performance_monitoring = False
        self.enable_schema_validation = False
        
        # Additional production optimizations
        self.enable_schema_caching = False  # Disable caching overhead
        self.enable_processor_caching = False
        self.enable_direct_access = True
        self.enable_inline_methods = True
        self.enable_fast_validation = True
    
    def set_development_mode(self):
        """Enable all features for development."""
        self.production_mode = False
        self.enable_logging = True
        self.enable_debug_logging = True
        self.enable_validation = True
        self.enable_performance_monitoring = True
        self.enable_schema_validation = True
    
    def get_runtime_config(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        return {
            'production_mode': self.production_mode,
            'enable_logging': self.enable_logging,
            'enable_validation': self.enable_validation,
            'enable_performance_monitoring': self.enable_performance_monitoring,
            'cache_size_limit': self.cache_size_limit,
            'pool_size_limit': self.pool_size_limit,
        }


# Global configuration instance
_config = None

def get_config() -> PerformanceConfig:
    """Get global performance configuration."""
    global _config
    if _config is None:
        _config = PerformanceConfig.from_environment()
    return _config

def set_config(config: PerformanceConfig):
    """Set global performance configuration."""
    global _config
    _config = config

def enable_production_mode():
    """Enable production mode optimizations."""
    config = get_config()
    config.set_production_mode()

def enable_development_mode():
    """Enable development mode with all features."""
    config = get_config()
    config.set_development_mode()

def get_validation_patterns() -> Dict[str, Any]:
    """Get validation patterns for schema operations."""
    return {
        'strict': {
            'enable_type_checking': True,
            'enable_required_fields': True,
            'enable_format_validation': True,
            'enable_enum_validation': True,
        },
        'relaxed': {
            'enable_type_checking': False,
            'enable_required_fields': False,
            'enable_format_validation': False,
            'enable_enum_validation': False,
        }
    }
