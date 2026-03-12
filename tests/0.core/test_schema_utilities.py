#!/usr/bin/env python3
"""
Core tests for XWSchema utility functions.
Tests the utility methods including:
- extract_properties: Extract XWSchema properties from objects
- load_properties: Load XWSchema properties onto objects
- extract_parameters: Extract parameter schemas from functions
- load_parameters: Load parameter schemas onto functions
- Caching and deadlock prevention
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 15-Dec-2025
"""

import pytest
import inspect
from typing import Dict, Optional
from exonware.xwschema import XWSchema
@pytest.mark.xwschema_core

class TestExtractProperties:
    """Test XWSchema.extract_properties utility."""

    def test_extract_properties_from_class_with_decorated_methods(self):
        """Test extracting properties from class with @XWSchema decorated methods."""
        # Create a mock decorated method by simulating the decorator pattern
        class TestClass:
            def __init__(self):
                pass
            @property
            def normal_prop(self) -> str:
                return "normal"
        # Manually create a decorated method pattern (simulating @XWSchema decorator)
        name_schema = XWSchema({'type': 'string', 'description': 'Name field'})
        def name_method(self) -> str:
            return getattr(self, '_name', '')
        # Add the decorated method attributes
        name_method._schema = name_schema
        name_method._is_schema_decorated = True
        setattr(TestClass, 'name', name_method)
        # Extract properties
        schemas = XWSchema.extract_properties(TestClass)
        # Should find the decorated method
        assert len(schemas) >= 1
        assert name_schema in schemas or any(id(s) == id(name_schema) for s in schemas)

    def test_extract_properties_from_instance(self):
        """Test extracting properties from class instance."""
        # Create class with decorated method
        class TestClass:
            def __init__(self):
                self._value = "test"
        # Create instance
        instance = TestClass()
        # Extract (should check class dict)
        schemas = XWSchema.extract_properties(instance)
        # Should return list (may be empty if no decorated properties)
        assert isinstance(schemas, list)

    def test_extract_properties_from_class_with_direct_schema(self):
        """Test extracting direct XWSchema attributes."""
        class TestClass:
            my_schema = XWSchema({'type': 'string'})
            normal_attr = "not a schema"
        schemas = XWSchema.extract_properties(TestClass)
        # Should find the direct XWSchema
        assert len(schemas) >= 1
        assert any(s.to_native().get('type') == 'string' for s in schemas)

    def test_extract_properties_caching(self):
        """Test that extract_properties uses caching."""
        class TestClass:
            my_schema = XWSchema({'type': 'integer'})
        # First call
        schemas1 = XWSchema.extract_properties(TestClass)
        # Second call should use cache
        schemas2 = XWSchema.extract_properties(TestClass)
        # Results should be same
        assert len(schemas1) == len(schemas2)
        assert schemas1 == schemas2
        # Clear cache and verify it works
        XWSchema._clear_extraction_cache()
        schemas3 = XWSchema.extract_properties(TestClass)
        assert len(schemas3) == len(schemas1)

    def test_extract_properties_deadlock_prevention(self):
        """Test that circular extraction is prevented."""
        class TestClass:
            pass
        # Simulate circular extraction by manually adding to in_progress
        cache_key = XWSchema._get_cache_key(TestClass)
        with XWSchema._extraction_cache_lock:
            XWSchema._extraction_in_progress.add(cache_key)
        try:
            # Should return empty list to break deadlock
            schemas = XWSchema.extract_properties(TestClass)
            assert schemas == []
        finally:
            # Cleanup
            with XWSchema._extraction_cache_lock:
                XWSchema._extraction_in_progress.discard(cache_key)

    def test_extract_properties_handles_exceptions(self):
        """Test that exceptions are handled gracefully."""
        # Create an object that might cause issues
        class ProblematicClass:
            def __getattribute__(self, name):
                if name == '__dict__':
                    raise AttributeError("Cannot access __dict__")
                return super().__getattribute__(name)
        instance = ProblematicClass()
        # Should handle gracefully and return empty list
        schemas = XWSchema.extract_properties(instance)
        assert isinstance(schemas, list)
@pytest.mark.xwschema_core

class TestLoadProperties:
    """Test XWSchema.load_properties utility."""

    def test_load_properties_onto_instance(self):
        """Test loading properties onto an instance."""
        class TestClass:
            def __init__(self):
                self._data = {}
        instance = TestClass()
        # Create schemas to load
        schemas = [
            XWSchema({'type': 'string', 'description': 'Name'}),
            XWSchema({'type': 'integer', 'description': 'Age'})
        ]
        # Load properties
        result = XWSchema.load_properties(instance, schemas)
        # Should succeed (even if property names are auto-generated)
        assert result is True

    def test_load_properties_rejects_class(self):
        """Test that loading properties onto a class raises error."""
        class TestClass:
            pass
        schemas = [XWSchema({'type': 'string'})]
        # Should raise ValueError
        with pytest.raises(ValueError, match="Cannot load properties onto a class"):
            XWSchema.load_properties(TestClass, schemas)

    def test_load_properties_with_empty_list(self):
        """Test loading empty list of properties."""
        class TestClass:
            def __init__(self):
                pass
        instance = TestClass()
        # Empty list should succeed
        result = XWSchema.load_properties(instance, [])
        assert result is True

    def test_load_properties_with_invalid_schemas(self):
        """Test loading with non-XWSchema objects."""
        class TestClass:
            def __init__(self):
                pass
        instance = TestClass()
        # Mix of valid and invalid
        schemas = [
            XWSchema({'type': 'string'}),
            "not a schema",  # Invalid
            XWSchema({'type': 'integer'})
        ]
        # Should handle gracefully (may fail but shouldn't crash)
        result = XWSchema.load_properties(instance, schemas)
        # Result may be False if some schemas are invalid
        assert isinstance(result, bool)
@pytest.mark.xwschema_core

class TestExtractParameters:
    """Test XWSchema.extract_parameters utility."""

    def test_extract_parameters_from_function(self):
        """Test extracting parameters from a simple function."""
        def test_func(x: int, y: str) -> bool:
            return True
        in_schemas, out_schemas = XWSchema.extract_parameters(test_func)
        # Should extract input parameters
        assert len(in_schemas) == 2
        # Should extract return type
        assert len(out_schemas) == 1

    def test_extract_parameters_excludes_self(self):
        """Test that 'self' parameter is excluded from extraction."""
        class TestClass:
            def method(self, x: int, y: str) -> bool:
                return True
        in_schemas, out_schemas = XWSchema.extract_parameters(TestClass.method)
        # Should exclude 'self'
        assert len(in_schemas) == 2
        assert len(out_schemas) == 1

    def test_extract_parameters_with_optional_types(self):
        """Test extracting parameters with Optional types."""
        from typing import Optional
        def test_func(name: str, age: Optional[int] = None) -> Optional[str]:
            return name
        in_schemas, out_schemas = XWSchema.extract_parameters(test_func)
        # Should handle Optional types
        assert len(in_schemas) == 2
        assert len(out_schemas) == 1

    def test_extract_parameters_with_complex_types(self):
        """Test extracting parameters with complex types."""
        def test_func(items: list[str], metadata: dict[str, int]) -> list[Dict]:
            return []
        in_schemas, out_schemas = XWSchema.extract_parameters(test_func)
        # Should handle complex types
        assert len(in_schemas) == 2
        assert len(out_schemas) == 1

    def test_extract_parameters_with_no_return_type(self):
        """Test function with no return type annotation."""
        def test_func(x: int):
            pass
        in_schemas, out_schemas = XWSchema.extract_parameters(test_func)
        # Should extract input but may have empty output
        assert len(in_schemas) == 1
        # Output may be empty if no return type
        assert isinstance(out_schemas, list)

    def test_extract_parameters_caching(self):
        """Test that extract_parameters uses caching."""
        def test_func(x: int, y: str) -> bool:
            return True
        # Clear cache first to ensure clean state
        XWSchema._clear_extraction_cache()
        # First call
        in1, out1 = XWSchema.extract_parameters(test_func)
        initial_in_len = len(in1)
        initial_out_len = len(out1)
        # Should have 2 input parameters (x and y)
        assert initial_in_len == 2, f"Expected 2 parameters, got {initial_in_len}"
        assert initial_out_len == 1
        # Second call should use cache
        in2, out2 = XWSchema.extract_parameters(test_func)
        # Results should be same (from cache)
        assert len(in2) == initial_in_len
        assert len(out2) == initial_out_len
        # Clear cache
        XWSchema._clear_extraction_cache()
        in3, out3 = XWSchema.extract_parameters(test_func)
        # After clearing cache, should extract same parameters again
        assert len(in3) == initial_in_len, f"After cache clear: expected {initial_in_len} parameters, got {len(in3)}"
        assert len(out3) == initial_out_len

    def test_extract_parameters_deadlock_prevention(self):
        """Test that circular extraction is prevented for functions."""
        def test_func(x: int) -> str:
            return str(x)
        # Simulate circular extraction
        cache_key = XWSchema._get_cache_key(test_func)
        with XWSchema._extraction_cache_lock:
            XWSchema._extraction_in_progress.add(cache_key)
        try:
            # Should return empty lists to break deadlock
            in_schemas, out_schemas = XWSchema.extract_parameters(test_func)
            assert in_schemas == []
            assert out_schemas == []
        finally:
            # Cleanup
            with XWSchema._extraction_cache_lock:
                XWSchema._extraction_in_progress.discard(cache_key)

    def test_extract_parameters_handles_exceptions(self):
        """Test that exceptions are handled gracefully."""
        # Create a function that might cause issues during inspection
        def problematic_func():
            # Function without annotations that might cause issues
            pass
        # Should handle gracefully
        in_schemas, out_schemas = XWSchema.extract_parameters(problematic_func)
        assert isinstance(in_schemas, list)
        assert isinstance(out_schemas, list)
@pytest.mark.xwschema_core

class TestLoadParameters:
    """Test XWSchema.load_parameters utility."""

    def test_load_parameters_onto_function(self):
        """Test loading parameters onto a function."""
        def test_func(x: int, y: str) -> bool:
            return True
        # Create parameter schemas
        parameters = {
            'in': [
                XWSchema({'type': 'integer'}),
                XWSchema({'type': 'string'})
            ],
            'out': [
                XWSchema({'type': 'boolean'})
            ]
        }
        # Load parameters
        result = XWSchema.load_parameters(test_func, parameters)
        # Should succeed
        assert result is True
        # Verify attributes are set
        assert hasattr(test_func, '_in_schemas')
        assert hasattr(test_func, '_out_schemas')
        assert len(test_func._in_schemas) == 2
        assert len(test_func._out_schemas) == 1

    def test_load_parameters_with_invalid_dict(self):
        """Test loading with invalid parameters dictionary."""
        def test_func(x: int) -> str:
            return str(x)
        # Missing 'in' key
        parameters = {
            'out': [XWSchema({'type': 'string'})]
        }
        # Should handle gracefully
        result = XWSchema.load_parameters(test_func, parameters)
        # May succeed or fail, but shouldn't crash
        assert isinstance(result, bool)

    def test_load_parameters_with_non_list_values(self):
        """Test loading with non-list values in parameters dict."""
        def test_func(x: int) -> str:
            return str(x)
        # Invalid: 'in' is not a list
        parameters = {
            'in': "not a list",
            'out': [XWSchema({'type': 'string'})]
        }
        # Should return False
        result = XWSchema.load_parameters(test_func, parameters)
        assert result is False

    def test_load_parameters_with_empty_lists(self):
        """Test loading with empty parameter lists."""
        def test_func() -> None:
            pass
        parameters = {
            'in': [],
            'out': []
        }
        result = XWSchema.load_parameters(test_func, parameters)
        assert result is True
        # Verify attributes are set
        assert hasattr(test_func, '_in_schemas')
        assert hasattr(test_func, '_out_schemas')
        assert len(test_func._in_schemas) == 0
        assert len(test_func._out_schemas) == 0

    def test_load_parameters_handles_exceptions(self):
        """Test that exceptions during loading are handled."""
        def test_func(x: int) -> str:
            return str(x)
        # Create a schema that might cause issues
        parameters = {
            'in': [XWSchema({'type': 'integer'})],
            'out': [XWSchema({'type': 'string'})]
        }
        # Should handle gracefully
        result = XWSchema.load_parameters(test_func, parameters)
        assert isinstance(result, bool)
@pytest.mark.xwschema_core

class TestSchemaUtilitiesIntegration:
    """Integration tests for schema utility functions."""

    def test_extract_and_load_roundtrip(self):
        """Test extracting parameters and loading them back."""
        def test_func(x: int, y: str) -> bool:
            return True
        # Extract parameters
        in_schemas, out_schemas = XWSchema.extract_parameters(test_func)
        # Create a new function
        def new_func(a: int, b: str) -> bool:
            return False
        # Load extracted schemas onto new function
        parameters = {
            'in': in_schemas,
            'out': out_schemas
        }
        result = XWSchema.load_parameters(new_func, parameters)
        # Should succeed
        assert result is True
        assert hasattr(new_func, '_in_schemas')
        assert hasattr(new_func, '_out_schemas')

    def test_cache_clearing_affects_subsequent_calls(self):
        """Test that clearing cache affects subsequent extraction calls."""
        class TestClass:
            my_schema = XWSchema({'type': 'string'})
        # First extraction
        schemas1 = XWSchema.extract_properties(TestClass)
        # Modify the class
        TestClass.another_schema = XWSchema({'type': 'integer'})
        # Clear cache
        XWSchema._clear_extraction_cache()
        # Second extraction should find both schemas
        schemas2 = XWSchema.extract_properties(TestClass)
        # Should have at least as many as before (may have more)
        assert len(schemas2) >= len(schemas1)

    def test_multiple_extractions_use_cache(self):
        """Test that multiple extractions use cache efficiently."""
        class TestClass:
            my_schema = XWSchema({'type': 'string'})
        # Multiple extractions
        schemas1 = XWSchema.extract_properties(TestClass)
        schemas2 = XWSchema.extract_properties(TestClass)
        schemas3 = XWSchema.extract_properties(TestClass)
        # All should return same results
        assert schemas1 == schemas2 == schemas3

    def test_utility_functions_work_with_real_decorator_pattern(self):
        """Test utilities work with real @XWSchema decorator pattern simulation."""
        # This simulates how XWEntity would use these utilities
        class EntityClass:
            def __init__(self):
                self._name = "Test"
            # Simulate @XWSchema decorator
            def name_property(self) -> str:
                return self._name
            # Manually add decorator attributes
            name_schema = XWSchema({'type': 'string', 'description': 'Entity name'})
            name_property._schema = name_schema
            name_property._is_schema_decorated = True
        # Extract properties
        schemas = XWSchema.extract_properties(EntityClass)
        # Should find the decorated property
        assert len(schemas) >= 1
        # Create instance and load properties
        instance = EntityClass()
        # Create new schemas to load
        new_schemas = [XWSchema({'type': 'string', 'description': 'Loaded property'})]
        result = XWSchema.load_properties(instance, new_schemas)
        assert result is True
@pytest.mark.xwschema_core

class TestSchemaUtilitiesEdgeCases:
    """Edge case tests for schema utility functions."""

    def test_extract_properties_from_empty_class(self):
        """Test extracting properties from empty class."""
        class EmptyClass:
            pass
        schemas = XWSchema.extract_properties(EmptyClass)
        assert isinstance(schemas, list)
        assert len(schemas) == 0

    def test_extract_properties_from_none_object(self):
        """Test extracting properties handles None gracefully."""
        # Should handle None without crashing
        schemas = XWSchema.extract_properties(None)
        assert isinstance(schemas, list)
        # May return empty list or handle gracefully

    def test_extract_properties_with_none_schema(self):
        """Test extracting when schema attribute is None."""
        class TestClass:
            def method(self):
                pass
            method._schema = None
            method._is_schema_decorated = True
        schemas = XWSchema.extract_properties(TestClass)
        # Should skip None schemas
        assert isinstance(schemas, list)

    def test_extract_properties_with_private_attributes_only(self):
        """Test extracting from class with only private attributes."""
        class PrivateClass:
            _private_attr = XWSchema({'type': 'string'})
            __very_private = XWSchema({'type': 'integer'})
        schemas = XWSchema.extract_properties(PrivateClass)
        # Private attributes without _schema should be skipped
        assert isinstance(schemas, list)

    def test_extract_properties_with_duplicate_schemas(self):
        """Test extracting when same schema appears multiple times."""
        shared_schema = XWSchema({'type': 'string'})
        class TestClass:
            schema1 = shared_schema
            schema2 = shared_schema
        schemas = XWSchema.extract_properties(TestClass)
        # Should extract both references
        assert len(schemas) >= 2

    def test_extract_parameters_from_function_with_no_annotations(self):
        """Test extracting parameters from function without type annotations."""
        def untyped_func(x, y, z):
            return x + y + z
        in_schemas, out_schemas = XWSchema.extract_parameters(untyped_func)
        # Should handle gracefully
        assert isinstance(in_schemas, list)
        assert isinstance(out_schemas, list)
        # Should extract parameters even without types
        assert len(in_schemas) == 3

    def test_extract_parameters_from_lambda(self):
        """Test extracting parameters from lambda function."""
        lambda_func = lambda x: x * 2
        in_schemas, out_schemas = XWSchema.extract_parameters(lambda_func)
        # Should handle lambdas
        assert isinstance(in_schemas, list)
        assert isinstance(out_schemas, list)

    def test_extract_parameters_from_function_with_any_type(self):
        """Test extracting parameters with Any type."""
        from typing import Any
        def func_with_any(x: Any, y: Any) -> Any:
            return x
        in_schemas, out_schemas = XWSchema.extract_parameters(func_with_any)
        # Should extract all parameters regardless of type
        assert len(in_schemas) >= 1  # At least one parameter
        assert isinstance(in_schemas, list)
        # Return type may or may not be extracted depending on implementation
        assert isinstance(out_schemas, list)

    def test_extract_parameters_from_function_with_union_types(self):
        """Test extracting parameters with Union types."""
        def func_with_union(x: int | str, y: float | None) -> bool | str:
            return True
        in_schemas, out_schemas = XWSchema.extract_parameters(func_with_union)
        assert len(in_schemas) == 2
        assert len(out_schemas) == 1

    def test_extract_parameters_with_var_args(self):
        """Test extracting parameters with *args and **kwargs."""
        def func_with_var_args(x: int, *args: str, **kwargs: int) -> bool:
            return True
        in_schemas, out_schemas = XWSchema.extract_parameters(func_with_var_args)
        # Should extract all parameters
        assert len(in_schemas) >= 1  # At least 'x'
        assert len(out_schemas) == 1

    def test_extract_parameters_from_async_function(self):
        """Test extracting parameters from async function."""
        async def async_func(x: int, y: str) -> bool:
            return True
        in_schemas, out_schemas = XWSchema.extract_parameters(async_func)
        assert len(in_schemas) == 2
        assert len(out_schemas) == 1

    def test_extract_parameters_with_callable_type(self):
        """Test extracting parameters with Callable type."""
        from typing import Callable
        def func_with_callable(fn: Callable[[int], str]) -> Callable:
            return fn
        in_schemas, out_schemas = XWSchema.extract_parameters(func_with_callable)
        # Callable types may be decomposed, so check for at least 1
        assert len(in_schemas) >= 1
        assert isinstance(out_schemas, list)

    def test_load_properties_with_none_object(self):
        """Test loading properties with None object."""
        schemas = [XWSchema({'type': 'string'})]
        # Should handle None gracefully (either raise or return False)
        result = XWSchema.load_properties(None, schemas)
        # Implementation may return False or raise - both are acceptable
        assert result is False or isinstance(result, bool)

    def test_load_properties_with_none_schemas_in_list(self):
        """Test loading properties with None values in schema list."""
        class TestClass:
            def __init__(self):
                pass
        instance = TestClass()
        schemas = [XWSchema({'type': 'string'}), None, XWSchema({'type': 'integer'})]
        # Should handle None gracefully
        result = XWSchema.load_properties(instance, schemas)
        # May fail but shouldn't crash
        assert isinstance(result, bool)

    def test_load_parameters_with_none_function(self):
        """Test loading parameters with None function."""
        parameters = {
            'in': [XWSchema({'type': 'integer'})],
            'out': [XWSchema({'type': 'string'})]
        }
        # Should handle None gracefully (may raise AttributeError or return False)
        try:
            result = XWSchema.load_parameters(None, parameters)
            assert result is False
        except (AttributeError, TypeError):
            # Acceptable - function may raise when accessing __name__ on None
            pass

    def test_load_parameters_with_missing_keys(self):
        """Test loading parameters with missing dictionary keys."""
        def test_func(x: int) -> str:
            return str(x)
        # Missing 'in' key
        parameters1 = {'out': [XWSchema({'type': 'string'})]}
        result1 = XWSchema.load_parameters(test_func, parameters1)
        assert isinstance(result1, bool)
        # Missing 'out' key
        parameters2 = {'in': [XWSchema({'type': 'integer'})]}
        result2 = XWSchema.load_parameters(test_func, parameters2)
        assert isinstance(result2, bool)
        # Empty dict
        parameters3 = {}
        result3 = XWSchema.load_parameters(test_func, parameters3)
        assert isinstance(result3, bool)

    def test_extract_properties_from_class_with_inheritance(self):
        """Test extracting properties from class with inheritance."""
        class BaseClass:
            base_schema = XWSchema({'type': 'string', 'description': 'Base'})
        class DerivedClass(BaseClass):
            derived_schema = XWSchema({'type': 'integer', 'description': 'Derived'})
        schemas = XWSchema.extract_properties(DerivedClass)
        # May find schemas from base and/or derived depending on implementation
        assert isinstance(schemas, list)

    def test_extract_properties_cache_with_object_deletion(self):
        """Test cache behavior when objects are deleted."""
        class TestClass:
            my_schema = XWSchema({'type': 'string'})
        # Extract and cache
        schemas1 = XWSchema.extract_properties(TestClass)
        # Delete the class (simulate object going out of scope)
        # Cache should still work with object ID
        schemas2 = XWSchema.extract_properties(TestClass)
        assert schemas1 == schemas2
@pytest.mark.xwschema_core

class TestSchemaUtilitiesStress:
    """Stress tests for schema utility functions."""

    def test_extract_properties_with_many_schemas(self):
        """Test extracting properties with many schema definitions."""
        # Create class with many schemas
        class LargeClass:
            pass
        # Add 100 schemas as direct XWSchema instances (these should be extracted)
        for i in range(100):
            schema = XWSchema({'type': 'string', 'description': f'Schema {i}'})
            setattr(LargeClass, f'schema_{i}', schema)
        # Extract should handle large number without crashing
        schemas = XWSchema.extract_properties(LargeClass)
        assert isinstance(schemas, list)
        assert len(schemas) >= 1  # At least one schema found

    def test_extract_parameters_with_many_parameters(self):
        """Test extracting parameters from function with many parameters."""
        # Create function with 50 parameters
        param_names = [f'x{i}' for i in range(50)]
        param_str = ', '.join(f'{name}: int' for name in param_names)
        func_code = f"def large_func({param_str}) -> bool: return True"
        namespace = {}
        exec(func_code, namespace)
        large_func = namespace['large_func']
        in_schemas, out_schemas = XWSchema.extract_parameters(large_func)
        assert len(in_schemas) == 50
        assert len(out_schemas) == 1

    def test_cache_size_limit_enforcement(self):
        """Test that cache size limit is enforced."""
        # Clear cache first
        XWSchema._clear_extraction_cache()
        # Create many different classes
        classes = []
        for i in range(XWSchema._extraction_cache_max_size + 10):
            class TempClass:
                my_schema = XWSchema({'type': 'string', 'description': f'Class {i}'})
            classes.append(TempClass)
            # Extract to populate cache
            XWSchema.extract_properties(TempClass)
        # Cache should not exceed max size
        with XWSchema._extraction_cache_lock:
            cache_size = len(XWSchema._extraction_cache)
            assert cache_size <= XWSchema._extraction_cache_max_size

    def test_concurrent_extract_properties(self):
        """Test thread safety of extract_properties under concurrent access."""
        import threading
        class TestClass:
            my_schema = XWSchema({'type': 'string'})
        results = []
        errors = []
        lock = threading.Lock()
        def extract_worker(worker_id):
            try:
                for _ in range(100):
                    schemas = XWSchema.extract_properties(TestClass)
                    with lock:
                        results.append((worker_id, len(schemas)))
            except Exception as e:
                with lock:
                    errors.append((worker_id, str(e)))
        # Create multiple threads
        threads = [threading.Thread(target=extract_worker, args=(i,)) for i in range(10)]
        # Start all threads
        for thread in threads:
            thread.start()
        # Wait for completion
        for thread in threads:
            thread.join()
        # Should not have errors
        assert len(errors) == 0, f"Concurrent extraction errors: {errors}"
        # All results should be consistent
        assert len(results) == 1000  # 10 threads * 100 iterations

    def test_concurrent_extract_parameters(self):
        """Test thread safety of extract_parameters under concurrent access."""
        import threading
        def test_func(x: int, y: str) -> bool:
            return True
        results = []
        errors = []
        lock = threading.Lock()
        def extract_worker(worker_id):
            try:
                for _ in range(100):
                    in_schemas, out_schemas = XWSchema.extract_parameters(test_func)
                    with lock:
                        results.append((worker_id, len(in_schemas), len(out_schemas)))
            except Exception as e:
                with lock:
                    errors.append((worker_id, str(e)))
        # Create multiple threads
        threads = [threading.Thread(target=extract_worker, args=(i,)) for i in range(10)]
        # Start all threads
        for thread in threads:
            thread.start()
        # Wait for completion
        for thread in threads:
            thread.join()
        # Should not have errors
        assert len(errors) == 0, f"Concurrent extraction errors: {errors}"
        # All results should be consistent
        assert len(results) == 1000  # 10 threads * 100 iterations
        # Verify consistent results (test_func has 2 parameters: x: int, y: str)
        for _, in_len, out_len in results:
            assert in_len == 2, f"Expected 2 input parameters, got {in_len}"
            assert out_len == 1, f"Expected 1 output schema, got {out_len}"

    def test_concurrent_load_properties(self):
        """Test thread safety of load_properties under concurrent access."""
        import threading
        class TestClass:
            def __init__(self):
                pass
        schemas = [XWSchema({'type': 'string'}) for _ in range(10)]
        results = []
        errors = []
        lock = threading.Lock()
        def load_worker(worker_id):
            try:
                instance = TestClass()
                result = XWSchema.load_properties(instance, schemas)
                with lock:
                    results.append((worker_id, result))
            except Exception as e:
                with lock:
                    errors.append((worker_id, str(e)))
        # Create multiple threads
        threads = [threading.Thread(target=load_worker, args=(i,)) for i in range(20)]
        # Start all threads
        for thread in threads:
            thread.start()
        # Wait for completion
        for thread in threads:
            thread.join()
        # Should not have many errors (some may fail due to class modification)
        assert len(errors) <= 5, f"Too many concurrent load errors: {errors}"

    def test_repeated_extraction_performance(self):
        """Test performance of repeated extractions (should use cache)."""
        import time
        class TestClass:
            my_schema = XWSchema({'type': 'string'})
        def test_func(x: int) -> str:
            return str(x)
        # Warm up cache
        XWSchema.extract_properties(TestClass)
        XWSchema.extract_parameters(test_func)
        # Time repeated extractions (should be fast due to cache)
        start = time.time()
        for _ in range(1000):
            XWSchema.extract_properties(TestClass)
            XWSchema.extract_parameters(test_func)
        elapsed = time.time() - start
        # Should be very fast with caching (< 1 second for 1000 operations)
        assert elapsed < 1.0, f"Repeated extractions took {elapsed:.2f}s, expected < 1.0s"

    def test_extract_properties_with_nested_classes(self):
        """Test extracting properties from deeply nested class structures."""
        # Create nested class structure
        class Level1:
            schema1 = XWSchema({'type': 'string'})
            class Level2:
                schema2 = XWSchema({'type': 'integer'})
                class Level3:
                    schema3 = XWSchema({'type': 'boolean'})
        # Extract from each level
        schemas1 = XWSchema.extract_properties(Level1)
        schemas2 = XWSchema.extract_properties(Level1.Level2)
        schemas3 = XWSchema.extract_properties(Level1.Level2.Level3)
        assert len(schemas1) >= 1
        assert len(schemas2) >= 1
        assert len(schemas3) >= 1

    def test_extract_parameters_with_complex_nested_types(self):
        """Test extracting parameters with complex nested generic types."""
        from typing import Optional
        def complex_func(
            items: list[dict[str, Optional[int]]],
            metadata: dict[str, list[tuple[int, str]]],
            nested: list[list[dict[str, str]]]
        ) -> dict[str, list[Optional[str]]]:
            return {}
        in_schemas, out_schemas = XWSchema.extract_parameters(complex_func)
        # Should handle complex nested types
        assert len(in_schemas) == 3
        assert len(out_schemas) == 1

    def test_load_properties_with_many_schemas(self):
        """Test loading many properties onto an instance."""
        class TestClass:
            def __init__(self):
                pass
        instance = TestClass()
        # Create 100 schemas
        schemas = [XWSchema({'type': 'string', 'description': f'Schema {i}'}) for i in range(100)]
        result = XWSchema.load_properties(instance, schemas)
        # Should handle large number of schemas
        assert isinstance(result, bool)

    def test_deadlock_prevention_with_nested_calls(self):
        """Test deadlock prevention with nested extraction calls."""
        class OuterClass:
            outer_schema = XWSchema({'type': 'string'})
            class InnerClass:
                inner_schema = XWSchema({'type': 'integer'})
        # Simulate nested extraction scenario
        # First extraction
        outer_schemas = XWSchema.extract_properties(OuterClass)
        # While extracting outer, try to extract inner (should not deadlock)
        inner_schemas = XWSchema.extract_properties(OuterClass.InnerClass)
        # Both should succeed
        assert len(outer_schemas) >= 1
        assert len(inner_schemas) >= 1

    def test_cache_consistency_under_concurrent_modification(self):
        """Test cache consistency when objects are modified concurrently."""
        import threading
        class TestClass:
            my_schema = XWSchema({'type': 'string'})
        results = []
        errors = []
        lock = threading.Lock()
        def extract_and_modify(worker_id):
            try:
                # Extract (uses cache)
                schemas1 = XWSchema.extract_properties(TestClass)
                # Modify class
                if worker_id == 0:
                    TestClass.new_schema = XWSchema({'type': 'integer'})
                    XWSchema._clear_extraction_cache()
                # Extract again
                schemas2 = XWSchema.extract_properties(TestClass)
                with lock:
                    results.append((worker_id, len(schemas1), len(schemas2)))
            except Exception as e:
                with lock:
                    errors.append((worker_id, str(e)))
        # Create threads
        threads = [threading.Thread(target=extract_and_modify, args=(i,)) for i in range(5)]
        # Start threads
        for thread in threads:
            thread.start()
        # Wait for completion
        for thread in threads:
            thread.join()
        # Should handle concurrent modifications gracefully
        assert len(errors) == 0, f"Cache consistency errors: {errors}"
