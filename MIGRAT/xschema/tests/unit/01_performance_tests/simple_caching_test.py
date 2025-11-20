"""
Simple Caching Investigation

Quick test to understand caching behavior across xschema versions.
"""

import time
import gc
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../../..'))

def test_schema_creation():
    """Test schema creation across versions."""
    print("🔍 Testing Schema Creation")
    print("=" * 50)
    
    # Test data
    test_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0}
        },
        "required": ["name", "age"]
    }
    
    # Test legacy
    try:
        from src.xlib.xschema.legacy.facade import xSchema as LegacyXSchema
        print("\n📋 LEGACY:")
        
        # Cold start
        start = time.time()
        schema1 = LegacyXSchema(test_schema)
        cold_time = time.time() - start
        
        # Warm start
        start = time.time()
        schema2 = LegacyXSchema(test_schema)
        warm_time = time.time() - start
        
        print(f"  Cold: {cold_time*1000000:.3f} μs")
        print(f"  Warm: {warm_time*1000000:.3f} μs")
        print(f"  Speedup: {cold_time/warm_time:.2f}x" if warm_time > 0 else "  Speedup: N/A")
        print(f"  Suspicious: {warm_time < 0.000001}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test new
    try:
        from src.xlib.xschema.new.facade import xSchema as NewXSchema
        print("\n📋 NEW:")
        
        # Cold start
        start = time.time()
        schema1 = NewXSchema(test_schema)
        cold_time = time.time() - start
        
        # Warm start
        start = time.time()
        schema2 = NewXSchema(test_schema)
        warm_time = time.time() - start
        
        print(f"  Cold: {cold_time*1000000:.3f} μs")
        print(f"  Warm: {warm_time*1000000:.3f} μs")
        print(f"  Speedup: {cold_time/warm_time:.2f}x" if warm_time > 0 else "  Speedup: N/A")
        print(f"  Suspicious: {warm_time < 0.000001}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test new_2
    try:
        from src.xlib.xschema.new_2.facade import xSchema as New2XSchema
        print("\n📋 NEW_2:")
        
        # Cold start
        start = time.time()
        schema1 = New2XSchema(test_schema)
        cold_time = time.time() - start
        
        # Warm start
        start = time.time()
        schema2 = New2XSchema(test_schema)
        warm_time = time.time() - start
        
        print(f"  Cold: {cold_time*1000000:.3f} μs")
        print(f"  Warm: {warm_time*1000000:.3f} μs")
        print(f"  Speedup: {cold_time/warm_time:.2f}x" if warm_time > 0 else "  Speedup: N/A")
        print(f"  Suspicious: {warm_time < 0.000001}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test new_3
    try:
        from src.xlib.xschema.new_3.facade import xSchema as New3XSchema
        print("\n📋 NEW_3:")
        
        # Cold start
        start = time.time()
        schema1 = New3XSchema(test_schema)
        cold_time = time.time() - start
        
        # Warm start
        start = time.time()
        schema2 = New3XSchema(test_schema)
        warm_time = time.time() - start
        
        print(f"  Cold: {cold_time*1000000:.3f} μs")
        print(f"  Warm: {warm_time*1000000:.3f} μs")
        print(f"  Speedup: {cold_time/warm_time:.2f}x" if warm_time > 0 else "  Speedup: N/A")
        print(f"  Suspicious: {warm_time < 0.000001}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")

def test_xnode_caching():
    """Test xNode caching behavior."""
    print("\n🔍 Testing xNode Caching")
    print("=" * 50)
    
    try:
        from src.xlib.xnode.facade import xNode
        
        test_data = {"name": "John", "age": 30}
        
        # Cold start
        start = time.time()
        node1 = xNode.from_native(test_data)
        cold_time = time.time() - start
        
        # Warm start
        start = time.time()
        node2 = xNode.from_native(test_data)
        warm_time = time.time() - start
        
        print(f"  Cold: {cold_time*1000000:.3f} μs")
        print(f"  Warm: {warm_time*1000000:.3f} μs")
        print(f"  Speedup: {cold_time/warm_time:.2f}x" if warm_time > 0 else "  Speedup: N/A")
        print(f"  Suspicious: {warm_time < 0.000001}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")

def test_xdata_caching():
    """Test xData caching behavior."""
    print("\n🔍 Testing xData Caching")
    print("=" * 50)
    
    try:
        from src.xlib.xdata import xData
        
        test_data = {"name": "John", "age": 30}
        
        # Cold start
        start = time.time()
        data1 = xData.from_native(test_data)
        cold_time = time.time() - start
        
        # Warm start
        start = time.time()
        data2 = xData.from_native(test_data)
        warm_time = time.time() - start
        
        print(f"  Cold: {cold_time*1000000:.3f} μs")
        print(f"  Warm: {warm_time*1000000:.3f} μs")
        print(f"  Speedup: {cold_time/warm_time:.2f}x" if warm_time > 0 else "  Speedup: N/A")
        print(f"  Suspicious: {warm_time < 0.000001}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")

def main():
    """Run all tests."""
    print("🚀 Simple Caching Investigation")
    print("=" * 60)
    
    test_schema_creation()
    test_xnode_caching()
    test_xdata_caching()
    
    print("\n✅ Investigation complete!")

if __name__ == "__main__":
    main()
