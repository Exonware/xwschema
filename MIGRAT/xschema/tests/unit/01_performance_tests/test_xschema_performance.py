"""
xSchema Performance Tests - Version Comparison Suite
==================================================

Comprehensive performance tests for xSchema across different formats:
- JSON
- XML  
- TOML
- YAML

Tests each available xSchema version and provides detailed performance metrics
including time and memory usage for each format, with version comparison tables.
"""

import pytest
import json
import tempfile
import os
import sys
import time
import psutil
import gc
import statistics
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from contextlib import contextmanager

# Add src to path for imports
src_path = str(Path(__file__).parent.parent.parent.parent.parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Also add the project root to handle relative imports
project_root = str(Path(__file__).parent.parent.parent.parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Performance test configuration
SCHEMA_CREATION_ITERATIONS = 1000
VALIDATION_ITERATIONS = 1000
SERIALIZATION_ITERATIONS = 1000
PROPERTY_ACCESS_ITERATIONS = 1000

# Import available xSchema versions
schema_versions = {}

try:
    from xlib.xschema.legacy.facade import xSchema as LegacySchema
    schema_versions['legacy'] = LegacySchema
    print("✅ xSchema legacy version loaded")
except ImportError as e:
    print(f"⚠️ xSchema legacy version not available: {e}")

try:
    from xlib.xschema.new.facade import xSchema as NewSchema
    schema_versions['new'] = NewSchema
    print("✅ xSchema new version loaded")
except ImportError as e:
    print(f"⚠️ xSchema new version not available: {e}")

try:
    from xlib.xschema.new_2.facade import xSchema as New2Schema
    schema_versions['new_2'] = New2Schema
    print("✅ xSchema new_2 version loaded")
except ImportError as e:
    print(f"⚠️ xSchema new_2 version not available: {e}")

try:
    from xlib.xschema.new_3.facade import xSchema as New3Schema
    schema_versions['new_3'] = New3Schema
    print("✅ xSchema new_3 version loaded")
except ImportError as e:
    print(f"⚠️ xSchema new_3 version not available: {e}")

if not schema_versions:
    pytest.skip("No xSchema versions available", allow_module_level=True)


@dataclass
class FormatPerformanceResult:
    """Container for format-specific performance test results."""
    format_name: str
    version: str
    operation: str
    time_taken: float
    memory_used: int
    iterations: int
    success: bool
    error: Optional[str] = None
    output: Optional[Any] = None  # Store actual output for comparison


class FormatPerformanceBenchmark:
    """Benchmark class for format-specific performance testing."""
    
    def __init__(self):
        self.results: List[FormatPerformanceResult] = []
        self.process = psutil.Process()
        self.verification_results = {}  # Store verification data
    
    def measure_performance(self, format_name: str, version: str, operation: str, iterations: int = 1):
        """Measure performance of a function over multiple iterations."""
        # Force garbage collection before measurement
        gc.collect()
        
        start_time = time.time()
        start_memory = self.process.memory_info().rss
        
        def measure_func(func):
            try:
                # Execute the operation multiple times and capture output from last iteration
                output = None
                for i in range(iterations):
                    output = func()
                
                success = True
                error = None
            except Exception as e:
                success = False
                error = str(e)
                output = None
            
            end_time = time.time()
            end_memory = self.process.memory_info().rss
            
            # Force garbage collection after measurement
            gc.collect()
            
            time_taken = (end_time - start_time) / iterations
            memory_used = end_memory - start_memory
            
            result = FormatPerformanceResult(
                format_name=format_name,
                version=version,
                operation=operation,
                time_taken=time_taken,
                memory_used=memory_used,
                iterations=iterations,
                success=success,
                error=error,
                output=output
            )
            
            # Store verification data to ensure operations actually did work
            key = f"{format_name}_{version}_{operation}"
            self.verification_results[key] = {
                'iterations': iterations,
                'time_taken': time_taken,
                'memory_used': memory_used,
                'success': success,
                'output': output
            }
            
            self.results.append(result)
        
        return measure_func
    
    def print_format_comparison(self, format_name: str):
        """Print version comparison table for a specific format."""
        format_results = [r for r in self.results if r.format_name == format_name]
        
        if not format_results:
            print(f"\n❌ No results for {format_name.upper()}")
            return
        
        print(f"\n📊 {format_name.upper()} - Version Comparison")
        print("=" * 100)
        
        # Group by operation
        operations = set(r.operation for r in format_results)
        
        for operation in sorted(operations):
            op_results = [r for r in format_results if r.operation == operation]
            
            print(f"\n🔧 {operation.upper()}")
            print("-" * 80)
            print(f"{'Version':<12} {'Time (ms)':<12} {'Memory (KB)':<12} {'Status':<8} {'Winner?':<8}")
            print("-" * 80)
            
            # Sort by time to find winner
            successful_results = [r for r in op_results if r.success]
            if successful_results:
                fastest = min(successful_results, key=lambda x: x.time_taken)
            
            for result in sorted(op_results, key=lambda x: x.version):
                time_ms = result.time_taken * 1000
                memory_kb = result.memory_used / 1024
                status = "✅ PASS" if result.success else "❌ FAIL"
                
                # Determine if this is the winner (fastest successful result)
                winner = ""
                if result.success and successful_results:
                    if result.time_taken == fastest.time_taken:
                        winner = "🏆 YES"
                
                print(f"{result.version:<12} {time_ms:<12.3f} {memory_kb:<12.1f} {status:<8} {winner:<8}")
                
                if result.error:
                    print(f"    Error: {result.error}")
    
    def print_final_summary(self):
        """Print final summary showing best version for each format."""
        print("\n🏆 FINAL SUMMARY - Best Version for Each Format")
        print("=" * 80)
        
        formats = ['json', 'xml', 'toml', 'yaml']
        operations = ['schema_creation', 'validation', 'serialization', 'property_access']
        
        # Create summary table
        print(f"{'Format':<8} {'Best Version':<15} {'Avg Time (ms)':<15} {'Avg Memory (KB)':<15}")
        print("-" * 80)
        
        for format_name in formats:
            format_results = [r for r in self.results if r.format_name == format_name and r.success]
            
            if not format_results:
                print(f"{format_name:<8} {'N/A':<15} {'N/A':<15} {'N/A':<15}")
                continue
            
            # Group by version
            version_stats = {}
            for version in schema_versions.keys():
                version_results = [r for r in format_results if r.version == version]
                if version_results:
                    avg_time = statistics.mean(r.time_taken for r in version_results) * 1000
                    avg_memory = statistics.mean(r.memory_used for r in version_results) / 1024
                    version_stats[version] = (avg_time, avg_memory)
            
            if version_stats:
                # Find best version (lowest average time)
                best_version = min(version_stats.keys(), key=lambda v: version_stats[v][0])
                best_time, best_memory = version_stats[best_version]
                
                print(f"{format_name:<8} {best_version:<15} {best_time:<15.3f} {best_memory:<15.1f}")
        
        print("\n📈 DETAILED BREAKDOWN BY OPERATION")
        print("=" * 80)
        
        for operation in operations:
            print(f"\n🔧 {operation.upper()}")
            print("-" * 60)
            print(f"{'Format':<8} {'Best Version':<15} {'Time (ms)':<12}")
            print("-" * 60)
            
            for format_name in formats:
                op_results = [r for r in self.results 
                            if r.format_name == format_name 
                            and r.operation == operation 
                            and r.success]
                
                if op_results:
                    fastest = min(op_results, key=lambda x: x.time_taken)
                    time_ms = fastest.time_taken * 1000
                    print(f"{format_name:<8} {fastest.version:<15} {time_ms:<12.3f}")
                else:
                    print(f"{format_name:<8} {'N/A':<15} {'N/A':<12}")

    def print_output_comparison(self):
        """Print comparison of outputs between versions to verify they're equivalent."""
        print(f"\n🔍 OUTPUT COMPARISON")
        print("=" * 50)
        
        formats = ['json', 'xml', 'toml', 'yaml']
        operations = ['schema_creation', 'validation', 'serialization', 'property_access']
        
        for format_name in formats:
            print(f"\n📋 {format_name.upper()}")
            print("-" * 40)
            
            for operation in operations:
                print(f"\n🔧 {operation.upper()}")
                
                # Get all successful results for this format and operation
                op_results = [r for r in self.results 
                            if r.format_name == format_name 
                            and r.operation == operation 
                            and r.success 
                            and r.output is not None]
                
                if not op_results:
                    print("  ❌ No successful results with outputs")
                    continue
                
                # Compare outputs
                outputs = {}
                for result in op_results:
                    outputs[result.version] = result.output
                
                if len(outputs) < 2:
                    print("  ⚠️  Only one version has output")
                    continue
                
                # Check if all outputs are equal
                first_output = list(outputs.values())[0]
                all_equal = all(output == first_output for output in outputs.values())
                
                if all_equal:
                    print("  ✅ All versions produce identical outputs")
                    # Show a sample of the output
                    if isinstance(first_output, dict):
                        print(f"    Sample output keys: {list(first_output.keys())[:5]}")
                    elif isinstance(first_output, (list, tuple)):
                        print(f"    Sample output length: {len(first_output)}")
                    else:
                        print(f"    Sample output type: {type(first_output).__name__}")
                else:
                    print("  ❌ Outputs differ between versions!")
                    for version, output in outputs.items():
                        print(f"    {version}: {type(output).__name__} - {str(output)[:100]}...")


# Test data for different formats
TEST_DATA = {
    'json': {
        'schema': {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0},
                "email": {"type": "string", "format": "email"},
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                        "zip": {"type": "string"}
                    },
                    "required": ["street", "city"]
                },
                "hobbies": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["name", "age"]
        },
        'valid_data': {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com",
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "zip": "12345"
            },
            "hobbies": ["reading", "swimming"]
        }
    },
    'xml': {
        'schema': {
            "type": "object",
            "properties": {
                "person": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                        "email": {"type": "string"},
                        "address": {
                            "type": "object",
                            "properties": {
                                "street": {"type": "string"},
                                "city": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        'valid_data': {
            "person": {
                "name": "Jane Smith",
                "age": 25,
                "email": "jane@example.com",
                "address": {
                    "street": "456 Oak Ave",
                    "city": "Somewhere"
                }
            }
        }
    },
    'toml': {
        'schema': {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "owner": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "organization": {"type": "string"}
                    }
                },
                "database": {
                    "type": "object",
                    "properties": {
                        "server": {"type": "string"},
                        "ports": {
                            "type": "array",
                            "items": {"type": "integer"}
                        }
                    }
                }
            }
        },
        'valid_data': {
            "title": "TOML Example",
            "owner": {
                "name": "Tom Preston-Werner",
                "organization": "GitHub"
            },
            "database": {
                "server": "192.168.1.1",
                "ports": [8001, 8001, 8002]
            }
        }
    },
    'yaml': {
        'schema': {
            "type": "object",
            "properties": {
                "apiVersion": {"type": "string"},
                "kind": {"type": "string"},
                "metadata": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "labels": {
                            "type": "object",
                            "additionalProperties": {"type": "string"}
                        }
                    }
                },
                "spec": {
                    "type": "object",
                    "properties": {
                        "replicas": {"type": "integer"},
                        "template": {
                            "type": "object",
                            "properties": {
                                "containers": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "image": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        'valid_data': {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "nginx-deployment",
                "labels": {
                    "app": "nginx"
                }
            },
            "spec": {
                "replicas": 3,
                "template": {
                    "containers": [
                        {
                            "name": "nginx",
                            "image": "nginx:1.14.2"
                        }
                    ]
                }
            }
        }
    }
}


class TestFormatPerformance:
    """Test performance across different formats."""
    
    @pytest.fixture
    def perf_benchmark(self):
        """Create benchmark instance."""
        return FormatPerformanceBenchmark()
    
    def test_json_performance(self, perf_benchmark):
        """Test JSON format performance."""
        print("\n🧪 Testing JSON Performance...")
        
        for version_name, SchemaClass in schema_versions.items():
            print(f"  Testing {version_name}...")
            
            # Schema creation - create schema multiple times
            measure_func = perf_benchmark.measure_performance('json', version_name, 'schema_creation', SCHEMA_CREATION_ITERATIONS)
            def create_schema():
                if version_name == 'legacy':
                    return SchemaClass.from_native(TEST_DATA['json']['schema'])
                else:
                    return SchemaClass(TEST_DATA['json']['schema'])
            measure_func(create_schema)
            
            # Create schema once for validation and other tests
            try:
                if version_name == 'legacy':
                    schema = SchemaClass.from_native(TEST_DATA['json']['schema'])
                else:
                    schema = SchemaClass(TEST_DATA['json']['schema'])
            except Exception as e:
                print(f"    ⚠️  Schema creation failed for {version_name}: {e}")
                # Don't create schema - let subsequent operations fail naturally
            
            # Validation - validate multiple times with different data variations
            measure_func = perf_benchmark.measure_performance('json', version_name, 'validation', VALIDATION_ITERATIONS)
            def validate_data():
                # Test with valid data
                if hasattr(schema, 'validate_data'):
                    schema.validate_data(TEST_DATA['json']['valid_data'])
                elif hasattr(schema, 'validate'):
                    schema.validate(TEST_DATA['json']['valid_data'])
                
                # Test with slightly modified data to ensure validation is actually working
                modified_data = TEST_DATA['json']['valid_data'].copy()
                if 'age' in modified_data:
                    modified_data['age'] = 25  # Different age
                if hasattr(schema, 'validate_data'):
                    schema.validate_data(modified_data)
                elif hasattr(schema, 'validate'):
                    schema.validate(modified_data)
            measure_func(validate_data)
            
            # Serialization - serialize multiple times
            measure_func = perf_benchmark.measure_performance('json', version_name, 'serialization', SERIALIZATION_ITERATIONS)
            def serialize_schema():
                if hasattr(schema, 'to_native'):
                    return schema.to_native()
                elif hasattr(schema, 'to_dict'):
                    return schema.to_dict()
            measure_func(serialize_schema)
            
            # Property access - access properties multiple times with more complex operations
            measure_func = perf_benchmark.measure_performance('json', version_name, 'property_access', PROPERTY_ACCESS_ITERATIONS)
            def access_properties():
                if hasattr(schema, 'properties'):
                    props = schema.properties
                    # Do some actual work with properties
                    if props:
                        _ = len(props)
                        _ = list(props.keys())
                        # Access nested properties recursively
                        for key, value in props.items():
                            if hasattr(value, 'properties'):
                                _ = value.properties
                            if hasattr(value, 'type'):
                                _ = value.type
                if hasattr(schema, 'type'):
                    _ = schema.type
                # Access nested properties if they exist
                if hasattr(schema, 'get'):
                    _ = schema.get('properties', {})
                # Test additional property access methods
                if hasattr(schema, 'keys'):
                    _ = list(schema.keys())
                if hasattr(schema, 'items'):
                    _ = list(schema.items())
            measure_func(access_properties)
        
        perf_benchmark.print_format_comparison('json')
    
    def test_xml_performance(self, perf_benchmark):
        """Test XML format performance."""
        print("\n🧪 Testing XML Performance...")
        
        for version_name, SchemaClass in schema_versions.items():
            print(f"  Testing {version_name}...")
            
            # Schema creation - create schema multiple times
            measure_func = perf_benchmark.measure_performance('xml', version_name, 'schema_creation', SCHEMA_CREATION_ITERATIONS)
            def create_schema():
                if version_name == 'legacy':
                    return SchemaClass.from_native(TEST_DATA['xml']['schema'])
                else:
                    return SchemaClass(TEST_DATA['xml']['schema'])
            measure_func(create_schema)
            
            # Create schema once for validation and other tests
            try:
                if version_name == 'legacy':
                    schema = SchemaClass.from_native(TEST_DATA['xml']['schema'])
                else:
                    schema = SchemaClass(TEST_DATA['xml']['schema'])
            except Exception as e:
                print(f"    ⚠️  Schema creation failed for {version_name}: {e}")
                # Don't create schema - let subsequent operations fail naturally
            
            # Validation - validate multiple times
            measure_func = perf_benchmark.measure_performance('xml', version_name, 'validation', VALIDATION_ITERATIONS)
            def validate_data():
                if hasattr(schema, 'validate_data'):
                    schema.validate_data(TEST_DATA['xml']['valid_data'])
                elif hasattr(schema, 'validate'):
                    schema.validate(TEST_DATA['xml']['valid_data'])
            measure_func(validate_data)
            
            # Serialization - serialize multiple times
            measure_func = perf_benchmark.measure_performance('xml', version_name, 'serialization', SERIALIZATION_ITERATIONS)
            def serialize_schema():
                if hasattr(schema, 'to_native'):
                    return schema.to_native()
                elif hasattr(schema, 'to_dict'):
                    return schema.to_dict()
            measure_func(serialize_schema)
            
            # Property access - access properties multiple times with more complex operations
            measure_func = perf_benchmark.measure_performance('xml', version_name, 'property_access', PROPERTY_ACCESS_ITERATIONS)
            def access_properties():
                if hasattr(schema, 'properties'):
                    props = schema.properties
                    # Do some actual work with properties
                    if props:
                        _ = len(props)
                        _ = list(props.keys())
                        # Access nested properties recursively
                        for key, value in props.items():
                            if hasattr(value, 'properties'):
                                _ = value.properties
                            if hasattr(value, 'type'):
                                _ = value.type
                if hasattr(schema, 'type'):
                    _ = schema.type
                # Access nested properties if they exist
                if hasattr(schema, 'get'):
                    _ = schema.get('properties', {})
                # Test additional property access methods
                if hasattr(schema, 'keys'):
                    _ = list(schema.keys())
                if hasattr(schema, 'items'):
                    _ = list(schema.items())
            measure_func(access_properties)
        
        perf_benchmark.print_format_comparison('xml')
    
    def test_toml_performance(self, perf_benchmark):
        """Test TOML format performance."""
        print("\n🧪 Testing TOML Performance...")
        
        for version_name, SchemaClass in schema_versions.items():
            print(f"  Testing {version_name}...")
            
            # Schema creation - create schema multiple times
            measure_func = perf_benchmark.measure_performance('toml', version_name, 'schema_creation', SCHEMA_CREATION_ITERATIONS)
            def create_schema():
                if version_name == 'legacy':
                    return SchemaClass.from_native(TEST_DATA['toml']['schema'])
                else:
                    return SchemaClass(TEST_DATA['toml']['schema'])
            measure_func(create_schema)
            
            # Create schema once for validation and other tests
            try:
                if version_name == 'legacy':
                    schema = SchemaClass.from_native(TEST_DATA['toml']['schema'])
                else:
                    schema = SchemaClass(TEST_DATA['toml']['schema'])
            except Exception as e:
                print(f"    ⚠️  Schema creation failed for {version_name}: {e}")
                # Don't create schema - let subsequent operations fail naturally
            
            # Validation - validate multiple times
            measure_func = perf_benchmark.measure_performance('toml', version_name, 'validation', VALIDATION_ITERATIONS)
            def validate_data():
                if hasattr(schema, 'validate_data'):
                    schema.validate_data(TEST_DATA['toml']['valid_data'])
                elif hasattr(schema, 'validate'):
                    schema.validate(TEST_DATA['toml']['valid_data'])
            measure_func(validate_data)
            
            # Serialization - serialize multiple times
            measure_func = perf_benchmark.measure_performance('toml', version_name, 'serialization', SERIALIZATION_ITERATIONS)
            def serialize_schema():
                if hasattr(schema, 'to_native'):
                    return schema.to_native()
                elif hasattr(schema, 'to_dict'):
                    return schema.to_dict()
            measure_func(serialize_schema)
            
            # Property access - access properties multiple times with more complex operations
            measure_func = perf_benchmark.measure_performance('toml', version_name, 'property_access', PROPERTY_ACCESS_ITERATIONS)
            def access_properties():
                if hasattr(schema, 'properties'):
                    props = schema.properties
                    # Do some actual work with properties
                    if props:
                        _ = len(props)
                        _ = list(props.keys())
                        # Access nested properties recursively
                        for key, value in props.items():
                            if hasattr(value, 'properties'):
                                _ = value.properties
                            if hasattr(value, 'type'):
                                _ = value.type
                if hasattr(schema, 'type'):
                    _ = schema.type
                # Access nested properties if they exist
                if hasattr(schema, 'get'):
                    _ = schema.get('properties', {})
                # Test additional property access methods
                if hasattr(schema, 'keys'):
                    _ = list(schema.keys())
                if hasattr(schema, 'items'):
                    _ = list(schema.items())
            measure_func(access_properties)
        
        perf_benchmark.print_format_comparison('toml')
    
    def test_yaml_performance(self, perf_benchmark):
        """Test YAML format performance."""
        print("\n🧪 Testing YAML Performance...")
        
        for version_name, SchemaClass in schema_versions.items():
            print(f"  Testing {version_name}...")
            
            # Schema creation - create schema multiple times
            measure_func = perf_benchmark.measure_performance('yaml', version_name, 'schema_creation', SCHEMA_CREATION_ITERATIONS)
            def create_schema():
                if version_name == 'legacy':
                    return SchemaClass.from_native(TEST_DATA['yaml']['schema'])
                else:
                    return SchemaClass(TEST_DATA['yaml']['schema'])
            measure_func(create_schema)
            
            # Create schema once for validation and other tests
            try:
                if version_name == 'legacy':
                    schema = SchemaClass.from_native(TEST_DATA['yaml']['schema'])
                else:
                    schema = SchemaClass(TEST_DATA['yaml']['schema'])
            except Exception as e:
                print(f"    ⚠️  Schema creation failed for {version_name}: {e}")
                # Don't create schema - let subsequent operations fail naturally
            
            # Validation - validate multiple times
            measure_func = perf_benchmark.measure_performance('yaml', version_name, 'validation', VALIDATION_ITERATIONS)
            def validate_data():
                if hasattr(schema, 'validate_data'):
                    schema.validate_data(TEST_DATA['yaml']['valid_data'])
                elif hasattr(schema, 'validate'):
                    schema.validate(TEST_DATA['yaml']['valid_data'])
            measure_func(validate_data)
            
            # Serialization - serialize multiple times
            measure_func = perf_benchmark.measure_performance('yaml', version_name, 'serialization', SERIALIZATION_ITERATIONS)
            def serialize_schema():
                if hasattr(schema, 'to_native'):
                    return schema.to_native()
                elif hasattr(schema, 'to_dict'):
                    return schema.to_dict()
            measure_func(serialize_schema)
            
            # Property access - access properties multiple times with more complex operations
            measure_func = perf_benchmark.measure_performance('yaml', version_name, 'property_access', PROPERTY_ACCESS_ITERATIONS)
            def access_properties():
                if hasattr(schema, 'properties'):
                    props = schema.properties
                    # Do some actual work with properties
                    if props:
                        _ = len(props)
                        _ = list(props.keys())
                        # Access nested properties recursively
                        for key, value in props.items():
                            if hasattr(value, 'properties'):
                                _ = value.properties
                            if hasattr(value, 'type'):
                                _ = value.type
                if hasattr(schema, 'type'):
                    _ = schema.type
                # Access nested properties if they exist
                if hasattr(schema, 'get'):
                    _ = schema.get('properties', {})
                # Test additional property access methods
                if hasattr(schema, 'keys'):
                    _ = list(schema.keys())
                if hasattr(schema, 'items'):
                    _ = list(schema.items())
            measure_func(access_properties)
        
        perf_benchmark.print_format_comparison('yaml')
    
    def test_performance_summary(self, perf_benchmark):
        """Print overall performance summary."""
        # Run all format tests first
        self.test_json_performance(perf_benchmark)
        self.test_xml_performance(perf_benchmark)
        self.test_toml_performance(perf_benchmark)
        self.test_yaml_performance(perf_benchmark)
        
        # Print final summary
        perf_benchmark.print_final_summary()
        
        # Print test statistics
        print(f"\n📊 Test Statistics")
        print("=" * 50)
        print(f"Total tests run: {len(perf_benchmark.results)}")
        successful = len([r for r in perf_benchmark.results if r.success])
        print(f"Successful: {successful}")
        print(f"Failed: {len(perf_benchmark.results) - successful}")
        print(f"Success rate: {(successful/len(perf_benchmark.results)*100):.1f}%")
        
        # Print verification summary
        print(f"\n🔍 VERIFICATION SUMMARY")
        print("=" * 50)
        print(f"Total operations measured: {len(perf_benchmark.verification_results)}")
        
        # Check for suspicious results (very fast operations that might be cached/no-ops)
        suspicious_count = 0
        for key, data in perf_benchmark.verification_results.items():
            if data['time_taken'] < 0.000001:  # Less than 1 microsecond
                suspicious_count += 1
                print(f"⚠️  Suspiciously fast operation: {key} ({data['time_taken']*1000000:.3f} μs)")
        
        if suspicious_count == 0:
            print("✅ All operations appear to be doing actual work")
        else:
            print(f"⚠️  {suspicious_count} operations may be cached or no-ops")
        
        # Print output comparison
        perf_benchmark.print_output_comparison()
    



if __name__ == "__main__":
    # Run the tests directly
    perf_benchmark = FormatPerformanceBenchmark()
    test_instance = TestFormatPerformance()
    
    print("🚀 xSchema Version Comparison Performance Tests")
    print("=" * 60)
    print(f"Available versions: {list(schema_versions.keys())}")
    print(f"Testing formats: JSON, XML, TOML, YAML")
    
    test_instance.test_performance_summary(perf_benchmark)
