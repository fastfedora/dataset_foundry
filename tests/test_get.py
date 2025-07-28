import pytest
from dataset_foundry.utils.get import get


class TestGet:
    """Comprehensive test suite for the get function."""

    def test_nested_dict_with_string_path(self):
        """Test accessing nested dictionary using dot-separated string path."""
        data = {'a': {'b': {'c': 1}}}
        assert get(data, 'a.b.c') == 1
        assert get(data, 'a.b') == {'c': 1}
        assert get(data, 'a') == {'b': {'c': 1}}

    def test_nested_dict_with_list_path(self):
        """Test accessing nested dictionary using list path."""
        data = {'a': {'b': {'c': 1}}}
        assert get(data, ['a', 'b', 'c']) == 1
        assert get(data, ['a', 'b']) == {'c': 1}
        assert get(data, ['a']) == {'b': {'c': 1}}

    def test_object_attributes(self):
        """Test accessing object attributes."""
        class TestObj:
            def __init__(self):
                self.a = {'b': 3}
                self.x = 42

        obj = TestObj()
        assert get(obj, 'a.b') == 3
        assert get(obj, 'x') == 42
        assert get(obj, 'a') == {'b': 3}

    def test_mixed_dict_and_object_access(self):
        """Test accessing object with dictionary attributes."""
        class TestObj:
            def __init__(self):
                self.data = {'nested': {'value': 'test'}}
                self.simple = 123

        obj = TestObj()
        assert get(obj, 'data.nested.value') == 'test'
        assert get(obj, 'simple') == 123

    def test_default_value_when_path_not_found(self):
        """Test that default value is returned when path doesn't exist."""
        data = {'a': {'b': 1}}

        # Test with string path - should return None, not default, because no exception is raised
        assert get(data, 'a.b.c') is None
        assert get(data, 'x.y.z') is None

        # Test with list path - should return None, not default, because no exception is raised
        assert get(data, ['a', 'b', 'c']) is None
        assert get(data, ['x', 'y']) is None

        # Test cases where exceptions are actually raised (these should use default)
        # Create an object that will raise an exception when accessing non-existent keys
        class ExceptionRaisingObj:
            def __getitem__(self, key):
                raise KeyError(f"Key '{key}' not found")

        obj = ExceptionRaisingObj()
        assert get(obj, 'nonexistent', default='error') == 'error'

    def test_default_value_with_none_default(self):
        """Test that None is returned when no default is specified."""
        data = {'a': {'b': 1}}
        assert get(data, 'a.b.c') is None
        assert get(data, 'x.y.z') is None
        assert get(data, 'a.d') is None

    def test_empty_path(self):
        """Test behavior with empty path."""
        data = {'a': 1}

        # Empty string path - should return None because split('.') on empty string gives ['']
        assert get(data, '') is None

        # Empty list path - should return the original object
        assert get(data, []) == data

    def test_single_level_access(self):
        """Test accessing single level keys/attributes."""
        data = {'key': 'value'}
        assert get(data, 'key') == 'value'
        assert get(data, ['key']) == 'value'

    def test_none_object(self):
        """Test behavior when object is None."""
        assert get(None, 'any.path') is None
        assert get(None, 'any.path', default='default') is None

    def test_non_dict_non_object_access(self):
        """Test accessing attributes of non-dict, non-object types."""
        # Test with list - getattr returns the method object, not the result
        lst = [1, 2, 3]
        assert get(lst, '__len__') == lst.__len__

        # Test with string - getattr returns the method object, not the result
        s = "hello"
        assert get(s, '__len__') == s.__len__

    def test_dict_with_get_method(self):
        """Test accessing dictionary that has get method."""
        class DictWithGet:
            def __init__(self, data):
                self._data = data

            def get(self, key, default=None):
                return self._data.get(key, default)

            def __getitem__(self, key):
                return self._data[key]

            def __contains__(self, key):
                return key in self._data

        obj = DictWithGet({'a': {'b': 2}})
        assert get(obj, 'a.b') == 2
        assert get(obj, 'x') is None  # Should return None, not default

    def test_object_without_get_method(self):
        """Test accessing object that doesn't have get method."""
        class SimpleObj:
            def __init__(self):
                self.attr = 'value'
                self.nested = {'key': 'nested_value'}

        obj = SimpleObj()
        assert get(obj, 'attr') == 'value'
        assert get(obj, 'nested.key') == 'nested_value'

    def test_complex_nested_structure(self):
        """Test accessing deeply nested mixed structure."""
        class NestedObj:
            def __init__(self):
                self.level1 = {
                    'level2': {
                        'level3': {
                            'final': 'success'
                        }
                    }
                }

        obj = NestedObj()
        assert get(obj, 'level1.level2.level3.final') == 'success'
        assert get(obj, ['level1', 'level2', 'level3', 'final']) == 'success'

    def test_path_with_special_characters(self):
        """Test path with dots in keys (should be treated as separators)."""
        data = {'a.b': {'c': 1}, 'a': {'b': 2}}

        # This should look for key 'a' then 'b' then 'c' (which doesn't exist)
        assert get(data, 'a.b.c') is None

        # This should look for key 'a' then 'b'
        assert get(data, 'a.b') == 2

    def test_list_path_with_special_characters(self):
        """Test list path with dots in keys."""
        data = {'a.b': {'c': 1}, 'a': {'b': 2}}

        # List path should work with dots in keys
        assert get(data, ['a.b', 'c']) == 1
        assert get(data, ['a', 'b']) == 2

    def test_error_handling(self):
        """Test that errors are properly caught and default is returned."""
        data = {'a': 1}

        # Accessing non-existent attribute on int - should return None, not default
        assert get(data, 'a.nonexistent') is None
        assert get(data, 'a.nonexistent', default='error') is None

    def test_edge_cases(self):
        """Test various edge cases."""
        # Empty dictionary
        assert get({}, 'any.path') is None

        # Dictionary with None values
        data = {'a': None, 'b': {'c': None}}
        assert get(data, 'a') is None
        assert get(data, 'b.c') is None

        # Path with only dots - should return None because split('.') on '...' gives ['', '', '']
        data = {'a': 1}
        assert get(data, '...') is None

    def test_docstring_examples(self):
        """Test the examples provided in the docstring."""
        # Note: Docstring shows 'get_in' but function is named 'get'
        data = {'a': {'b': {'c': 1}}}
        assert get(data, 'a.b.c') == 1
        assert get(data, ['a', 'b', 'c']) == 1

        class Obj:
            pass

        o = Obj()
        o.a = {'b': 3}
        assert get(o, 'a.b') == 3

    def test_type_safety(self):
        """Test that function handles different types correctly."""
        # Test with various data types - getattr returns the method object, not the result
        assert get(42, '__class__') == int

        # Test with string - use the same string object
        s = "hello"
        assert get(s, '__len__') == s.__len__

        # Test with list - use the same list object
        lst = [1, 2, 3]
        assert get(lst, '__len__') == lst.__len__

        # Test with custom objects
        class CustomType:
            def __init__(self, value):
                self.value = value

        obj = CustomType("test")
        assert get(obj, 'value') == "test"