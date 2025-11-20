"""
Caching Investigation Test

This test investigates the caching behavior across all xschema versions
to understand why some operations are suspiciously fast.
"""

import time
import gc
import psutil
import threading
from typing import Dict, Any, List
from dataclasses import dataclass
from collections import defaultdict

# Import all xschema versions
from src.xlib.xschema.legacy.facade import xSchema as LegacyXSchema
from src.xlib.xschema.new.facade import xSchema as NewXSchema
from src.xlib.xschema.new_2.facade import xSchema as New2XSchema
from src.xlib.xschema.new_3.facade import xSchema as New3XSchema

# Import xnode and xdata for investigation
from src.xlib.xnode.facade import xNode
from src.xlib.xdata import xData

@dataclass
class CacheInvestigationResult:
    """Result of a cache investigation."""
    version: str
    operation: str
    time_taken: float
    memory_before: int
    memory_after: int
    memory_delta: int
    cache_hits: int
    cache_misses: int
    is_cached: bool
    output_type: str
    output_size: int
    suspicious: bool

class CacheInvestigator:
    """Investigates caching behavior across xschema versions."""
    
    def __init__(self):
        self.results = []
        self.process = psutil.Process()
        
    def get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        return self.process.memory_info().rss
    
    def measure_operation(self, func, *args, **kwargs) -> Dict[str, Any]:
        """Measure operation performance and memory usage."""
        # Force garbage collection
        gc.collect()
        
        # Get memory before
        memory_before = self.get_memory_usage()
        
        # Measure time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Get memory after
        memory_after = self.get_memory_usage()
        
        return {
            'time_taken': end_time - start_time,
            'memory_before': memory_before,
            'memory_after': memory_after,
            'memory_delta': memory_after - memory_before,
            'result': result,
            'result_type': type(result).__name__,
            'result_size': len(str(result)) if result else 0
        }
    
    def investigate_schema_creation(self, schema_data: Dict[str, Any]) -> List[CacheInvestigationResult]:
        """Investigate schema creation across all versions."""
        results = []
        
        # Test data
        test_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["name", "age"]
        }
        
        versions = [
            ("legacy", LegacyXSchema),
            ("new", NewXSchema),
            ("new_2", New2XSchema),
            ("new_3", New3XSchema)
        ]
        
        for version_name, schema_class in versions:
            print(f"\n🔍 Investigating {version_name} schema creation...")
            
            # First creation (cold)
            cold_result = self.measure_operation(
                lambda: schema_class(test_schema)
            )
            
            # Second creation (potentially cached)
            warm_result = self.measure_operation(
                lambda: schema_class(test_schema)
            )
            
            # Check if there's a significant speedup
            speedup = cold_result['time_taken'] / warm_result['time_taken'] if warm_result['time_taken'] > 0 else 1
            
            results.append(CacheInvestigationResult(
                version=version_name,
                operation="schema_creation_cold",
                time_taken=cold_result['time_taken'],
                memory_before=cold_result['memory_before'],
                memory_after=cold_result['memory_after'],
                memory_delta=cold_result['memory_delta'],
                cache_hits=0,
                cache_misses=1,
                is_cached=False,
                output_type=cold_result['result_type'],
                output_size=cold_result['result_size'],
                suspicious=cold_result['time_taken'] < 0.000001
            ))
            
            results.append(CacheInvestigationResult(
                version=version_name,
                operation="schema_creation_warm",
                time_taken=warm_result['time_taken'],
                memory_before=warm_result['memory_before'],
                memory_after=warm_result['memory_after'],
                memory_delta=warm_result['memory_delta'],
                cache_hits=1 if speedup > 2 else 0,
                cache_misses=0 if speedup > 2 else 1,
                is_cached=speedup > 2,
                output_type=warm_result['result_type'],
                output_size=warm_result['result_size'],
                suspicious=warm_result['time_taken'] < 0.000001
            ))
            
            print(f"  Cold: {cold_result['time_taken']*1000000:.3f} μs")
            print(f"  Warm: {warm_result['time_taken']*1000000:.3f} μs")
            print(f"  Speedup: {speedup:.2f}x")
            print(f"  Suspicious: {warm_result['time_taken'] < 0.000001}")
        
        return results
    
    def investigate_validation(self, schema_data: Dict[str, Any], test_data: Dict[str, Any]) -> List[CacheInvestigationResult]:
        """Investigate validation across all versions."""
        results = []
        
        versions = [
            ("legacy", LegacyXSchema),
            ("new", NewXSchema),
            ("new_2", New2XSchema),
            ("new_3", New3XSchema)
        ]
        
        for version_name, schema_class in versions:
            print(f"\n🔍 Investigating {version_name} validation...")
            
            # Create schema
            schema = schema_class(schema_data)
            
            # First validation (cold)
            cold_result = self.measure_operation(
                lambda: schema.validate_data(test_data) if hasattr(schema, 'validate_data') else schema.validate(test_data)
            )
            
            # Second validation (potentially cached)
            warm_result = self.measure_operation(
                lambda: schema.validate_data(test_data) if hasattr(schema, 'validate_data') else schema.validate(test_data)
            )
            
            # Check if there's a significant speedup
            speedup = cold_result['time_taken'] / warm_result['time_taken'] if warm_result['time_taken'] > 0 else 1
            
            results.append(CacheInvestigationResult(
                version=version_name,
                operation="validation_cold",
                time_taken=cold_result['time_taken'],
                memory_before=cold_result['memory_before'],
                memory_after=cold_result['memory_after'],
                memory_delta=cold_result['memory_delta'],
                cache_hits=0,
                cache_misses=1,
                is_cached=False,
                output_type=cold_result['result_type'],
                output_size=cold_result['result_size'],
                suspicious=cold_result['time_taken'] < 0.000001
            ))
            
            results.append(CacheInvestigationResult(
                version=version_name,
                operation="validation_warm",
                time_taken=warm_result['time_taken'],
                memory_before=warm_result['memory_before'],
                memory_after=warm_result['memory_after'],
                memory_delta=warm_result['memory_delta'],
                cache_hits=1 if speedup > 2 else 0,
                cache_misses=0 if speedup > 2 else 1,
                is_cached=speedup > 2,
                output_type=warm_result['result_type'],
                output_size=warm_result['result_size'],
                suspicious=warm_result['time_taken'] < 0.000001
            ))
            
            print(f"  Cold: {cold_result['time_taken']*1000000:.3f} μs")
            print(f"  Warm: {warm_result['time_taken']*1000000:.3f} μs")
            print(f"  Speedup: {speedup:.2f}x")
            print(f"  Suspicious: {warm_result['time_taken'] < 0.000001}")
        
        return results
    
    def investigate_xnode_caching(self) -> List[CacheInvestigationResult]:
        """Investigate xNode caching behavior."""
        results = []
        
        print(f"\n🔍 Investigating xNode caching...")
        
        # Test data
        test_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com",
            "address": {
                "street": "123 Main St",
                "city": "Anytown"
            }
        }
        
        # First xNode creation (cold)
        cold_result = self.measure_operation(
            lambda: xNode.from_native(test_data)
        )
        
        # Second xNode creation (potentially cached)
        warm_result = self.measure_operation(
            lambda: xNode.from_native(test_data)
        )
        
        # Check if there's a significant speedup
        speedup = cold_result['time_taken'] / warm_result['time_taken'] if warm_result['time_taken'] > 0 else 1
        
        results.append(CacheInvestigationResult(
            version="xnode",
            operation="creation_cold",
            time_taken=cold_result['time_taken'],
            memory_before=cold_result['memory_before'],
            memory_after=cold_result['memory_after'],
            memory_delta=cold_result['memory_delta'],
            cache_hits=0,
            cache_misses=1,
            is_cached=False,
            output_type=cold_result['result_type'],
            output_size=cold_result['result_size'],
            suspicious=cold_result['time_taken'] < 0.000001
        ))
        
        results.append(CacheInvestigationResult(
            version="xnode",
            operation="creation_warm",
            time_taken=warm_result['time_taken'],
            memory_before=warm_result['memory_before'],
            memory_after=warm_result['memory_after'],
            memory_delta=warm_result['memory_delta'],
            cache_hits=1 if speedup > 2 else 0,
            cache_misses=0 if speedup > 2 else 1,
            is_cached=speedup > 2,
            output_type=warm_result['result_type'],
            output_size=warm_result['result_size'],
            suspicious=warm_result['time_taken'] < 0.000001
        ))
        
        print(f"  Cold: {cold_result['time_taken']*1000000:.3f} μs")
        print(f"  Warm: {warm_result['time_taken']*1000000:.3f} μs")
        print(f"  Speedup: {speedup:.2f}x")
        print(f"  Suspicious: {warm_result['time_taken'] < 0.000001}")
        
        return results
    
    def investigate_xdata_caching(self) -> List[CacheInvestigationResult]:
        """Investigate xData caching behavior."""
        results = []
        
        print(f"\n🔍 Investigating xData caching...")
        
        # Test data
        test_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        
        # First xData creation (cold)
        cold_result = self.measure_operation(
            lambda: xData.from_native(test_data)
        )
        
        # Second xData creation (potentially cached)
        warm_result = self.measure_operation(
            lambda: xData.from_native(test_data)
        )
        
        # Check if there's a significant speedup
        speedup = cold_result['time_taken'] / warm_result['time_taken'] if warm_result['time_taken'] > 0 else 1
        
        results.append(CacheInvestigationResult(
            version="xdata",
            operation="creation_cold",
            time_taken=cold_result['time_taken'],
            memory_before=cold_result['memory_before'],
            memory_after=cold_result['memory_after'],
            memory_delta=cold_result['memory_delta'],
            cache_hits=0,
            cache_misses=1,
            is_cached=False,
            output_type=cold_result['result_type'],
            output_size=cold_result['result_size'],
            suspicious=cold_result['time_taken'] < 0.000001
        ))
        
        results.append(CacheInvestigationResult(
            version="xdata",
            operation="creation_warm",
            time_taken=warm_result['time_taken'],
            memory_before=warm_result['memory_before'],
            memory_after=warm_result['memory_after'],
            memory_delta=warm_result['memory_delta'],
            cache_hits=1 if speedup > 2 else 0,
            cache_misses=0 if speedup > 2 else 1,
            is_cached=speedup > 2,
            output_type=warm_result['result_type'],
            output_size=warm_result['result_size'],
            suspicious=warm_result['time_taken'] < 0.000001
        ))
        
        print(f"  Cold: {cold_result['time_taken']*1000000:.3f} μs")
        print(f"  Warm: {warm_result['time_taken']*1000000:.3f} μs")
        print(f"  Speedup: {speedup:.2f}x")
        print(f"  Suspicious: {warm_result['time_taken'] < 0.000001}")
        
        return results
    
    def run_comprehensive_investigation(self) -> Dict[str, Any]:
        """Run comprehensive caching investigation."""
        print("🚀 Starting Comprehensive Caching Investigation")
        print("=" * 60)
        
        # Test data
        schema_data = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["name", "age"]
        }
        
        test_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        
        all_results = []
        
        # Investigate each component
        all_results.extend(self.investigate_schema_creation(schema_data))
        all_results.extend(self.investigate_validation(schema_data, test_data))
        all_results.extend(self.investigate_xnode_caching())
        all_results.extend(self.investigate_xdata_caching())
        
        # Analyze results
        analysis = self.analyze_results(all_results)
        
        # Print summary
        self.print_summary(analysis)
        
        return analysis
    
    def analyze_results(self, results: List[CacheInvestigationResult]) -> Dict[str, Any]:
        """Analyze investigation results."""
        analysis = {
            'total_operations': len(results),
            'suspicious_operations': len([r for r in results if r.suspicious]),
            'cached_operations': len([r for r in results if r.is_cached]),
            'by_version': defaultdict(list),
            'by_operation': defaultdict(list),
            'performance_stats': {},
            'cache_effectiveness': {}
        }
        
        # Group by version
        for result in results:
            analysis['by_version'][result.version].append(result)
        
        # Group by operation
        for result in results:
            analysis['by_operation'][result.operation].append(result)
        
        # Calculate performance stats
        for version, version_results in analysis['by_version'].items():
            times = [r.time_taken for r in version_results]
            analysis['performance_stats'][version] = {
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'suspicious_count': len([r for r in version_results if r.suspicious]),
                'cached_count': len([r for r in version_results if r.is_cached])
            }
        
        # Calculate cache effectiveness
        for operation, operation_results in analysis['by_operation'].items():
            if len(operation_results) >= 2:
                cold_results = [r for r in operation_results if 'cold' in r.operation]
                warm_results = [r for r in operation_results if 'warm' in r.operation]
                
                if cold_results and warm_results:
                    avg_cold = sum(r.time_taken for r in cold_results) / len(cold_results)
                    avg_warm = sum(r.time_taken for r in warm_results) / len(warm_results)
                    
                    analysis['cache_effectiveness'][operation] = {
                        'avg_cold_time': avg_cold,
                        'avg_warm_time': avg_warm,
                        'speedup': avg_cold / avg_warm if avg_warm > 0 else 1,
                        'effective': avg_cold / avg_warm > 2 if avg_warm > 0 else False
                    }
        
        return analysis
    
    def print_summary(self, analysis: Dict[str, Any]):
        """Print investigation summary."""
        print(f"\n📊 CACHING INVESTIGATION SUMMARY")
        print("=" * 60)
        print(f"Total operations tested: {analysis['total_operations']}")
        print(f"Suspicious operations: {analysis['suspicious_operations']}")
        print(f"Cached operations: {analysis['cached_operations']}")
        
        print(f"\n🔍 PERFORMANCE BY VERSION")
        print("-" * 40)
        for version, stats in analysis['performance_stats'].items():
            print(f"{version.upper():<10} | "
                  f"Avg: {stats['avg_time']*1000000:>8.3f} μs | "
                  f"Min: {stats['min_time']*1000000:>8.3f} μs | "
                  f"Max: {stats['max_time']*1000000:>8.3f} μs | "
                  f"Suspicious: {stats['suspicious_count']:>2} | "
                  f"Cached: {stats['cached_count']:>2}")
        
        print(f"\n⚡ CACHE EFFECTIVENESS")
        print("-" * 40)
        for operation, stats in analysis['cache_effectiveness'].items():
            print(f"{operation:<25} | "
                  f"Cold: {stats['avg_cold_time']*1000000:>8.3f} μs | "
                  f"Warm: {stats['avg_warm_time']*1000000:>8.3f} μs | "
                  f"Speedup: {stats['speedup']:>6.2f}x | "
                  f"Effective: {'✅' if stats['effective'] else '❌'}")
        
        # Identify problematic areas
        print(f"\n⚠️  PROBLEMATIC AREAS")
        print("-" * 40)
        
        suspicious_versions = [v for v, stats in analysis['performance_stats'].items() 
                             if stats['suspicious_count'] > 0]
        
        if suspicious_versions:
            print(f"Suspicious operations found in: {', '.join(suspicious_versions)}")
            print("These versions may be using aggressive caching or no-ops.")
        
        ineffective_caches = [op for op, stats in analysis['cache_effectiveness'].items() 
                            if not stats['effective']]
        
        if ineffective_caches:
            print(f"Ineffective caching in: {', '.join(ineffective_caches)}")
            print("These operations don't benefit from caching.")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 40)
        
        if analysis['suspicious_operations'] > analysis['total_operations'] * 0.3:
            print("❌ HIGH SUSPICION: Over 30% of operations are suspiciously fast.")
            print("   This suggests aggressive caching or no-ops are being used.")
            print("   Consider implementing actual work in these operations.")
        
        if analysis['cached_operations'] < analysis['total_operations'] * 0.1:
            print("⚠️  LOW CACHING: Less than 10% of operations benefit from caching.")
            print("   Consider implementing caching for frequently accessed operations.")
        
        print("✅ Investigation complete!")

def main():
    """Run the caching investigation."""
    investigator = CacheInvestigator()
    results = investigator.run_comprehensive_investigation()
    return results

if __name__ == "__main__":
    main()
