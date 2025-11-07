import os
import tempfile
import unittest
from pathlib import Path

from dataset_foundry.utils.filesystem.find_paths import find_paths


class TestFindPaths(unittest.TestCase):
    """Final comprehensive unit tests for the find_paths function."""

    def setUp(self):
        """Set up a temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Create a test directory structure
        self._create_test_structure()

    def tearDown(self):
        """Clean up the temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def _create_test_structure(self):
        """Create a test directory structure."""
        # Create files in root
        (self.temp_path / "file1.txt").write_text("content")
        (self.temp_path / "file2.py").write_text("content")
        (self.temp_path / "file3.log").write_text("content")
        (self.temp_path / "README.md").write_text("content")

        # Create directories
        (self.temp_path / "src").mkdir()
        (self.temp_path / "build").mkdir()
        (self.temp_path / "logs").mkdir()
        (self.temp_path / "temp").mkdir()

        # Create files in subdirectories
        (self.temp_path / "src" / "main.py").write_text("content")
        (self.temp_path / "src" / "utils.py").write_text("content")
        (self.temp_path / "src" / "test.py").write_text("content")
        (self.temp_path / "src" / "helper.txt").write_text("content")

        (self.temp_path / "build" / "output.exe").write_text("content")
        (self.temp_path / "build" / "debug").mkdir()
        (self.temp_path / "build" / "debug" / "app.pdb").write_text("content")

        (self.temp_path / "logs" / "app.log").write_text("content")
        (self.temp_path / "logs" / "error.log").write_text("content")

        (self.temp_path / "temp" / "cache.tmp").write_text("content")
        (self.temp_path / "temp" / "backup.bak").write_text("content")

    def test_basic_functionality(self):
        """Test basic functionality with no patterns."""
        results = find_paths(self.temp_dir)

        # Should find files and directories
        self.assertGreater(len(results), 0)

        # Check that we have both files and directories
        file_types = [item[1] for item in results]
        self.assertIn('file', file_types)
        self.assertIn('directory', file_types)

    def test_include_patterns(self):
        """Test include patterns."""
        results = find_paths(self.temp_dir, include=["*.py"])

        # Should find Python files
        files = [item[0] for item in results if item[1] == 'file']
        self.assertIn("file2.py", files)
        self.assertIn("src/main.py", files)
        self.assertIn("src/utils.py", files)
        self.assertIn("src/test.py", files)

        # Should not find non-Python files
        self.assertNotIn("file1.txt", files)
        self.assertNotIn("file3.log", files)

    def test_exclude_patterns(self):
        """Test exclude patterns."""
        results = find_paths(
            self.temp_dir,
            include=["*.py"],
            exclude=["src/*"]
        )

        # Should find Python files but exclude those in src/
        files = [item[0] for item in results if item[1] == 'file']
        self.assertIn("file2.py", files)
        self.assertNotIn("src/main.py", files)
        self.assertNotIn("src/utils.py", files)
        self.assertNotIn("src/test.py", files)

    def test_directory_patterns(self):
        """Test directory patterns."""
        results = find_paths(self.temp_dir, include=["build/", "logs/"])

        # Should find directories
        directories = [item[0] for item in results if item[1] == 'directory']
        self.assertIn("build", directories)
        self.assertIn("logs", directories)

        # Should find files within those directories
        files = [item[0] for item in results if item[1] == 'file']
        self.assertIn("build/output.exe", files)
        self.assertIn("logs/app.log", files)
        self.assertIn("logs/error.log", files)

    def test_multiple_include_patterns(self):
        """Test multiple include patterns."""
        results = find_paths(self.temp_dir, include=["*.py", "*.log"])

        # Should find both Python and log files
        files = [item[0] for item in results if item[1] == 'file']
        self.assertIn("file2.py", files)
        self.assertIn("file3.log", files)
        self.assertIn("src/main.py", files)
        self.assertIn("logs/app.log", files)
        self.assertIn("logs/error.log", files)

    def test_nested_directory_patterns(self):
        """Test patterns that match nested directories."""
        results = find_paths(self.temp_dir, include=["**/debug/**"])

        # Should find files in nested debug directory
        files = [item[0] for item in results if item[1] == 'file']
        self.assertIn("build/debug/app.pdb", files)

    def test_nonexistent_directory(self):
        """Test behavior with nonexistent directory."""
        with self.assertRaises(ValueError) as context:
            find_paths("/nonexistent/directory")
        self.assertIn("does not exist", str(context.exception))

    def test_empty_directory(self):
        """Test behavior with empty directory."""
        empty_dir = tempfile.mkdtemp()
        try:
            results = find_paths(empty_dir)
            self.assertEqual(results, [])
        finally:
            os.rmdir(empty_dir)

    def test_path_object_input(self):
        """Test that Path objects work as input."""
        results = find_paths(Path(self.temp_dir), include=["*.py"])

        # Should work the same as string input
        files = [item[0] for item in results if item[1] == 'file']
        self.assertIn("file2.py", files)
        self.assertIn("src/main.py", files)

    def test_empty_patterns(self):
        """Test with empty pattern lists."""
        results = find_paths(self.temp_dir, include=[], exclude=[])
        # Should return all files and directories
        self.assertGreater(len(results), 0)

    def test_none_patterns(self):
        """Test with None patterns."""
        results = find_paths(self.temp_dir, include=None, exclude=None)
        # Should return all files and directories
        self.assertGreater(len(results), 0)

    def test_case_sensitivity(self):
        """Test that patterns are case sensitive."""
        # Create a file with different case
        (self.temp_path / "File.TXT").write_text("content")

        results = find_paths(self.temp_dir, include=["*.txt"])

        files = [item[0] for item in results if item[1] == 'file']
        self.assertIn("file1.txt", files)
        self.assertNotIn("File.TXT", files)  # Case sensitive

    def test_performance_with_large_directory(self):
        """Test performance with a larger directory structure."""
        # Create a larger structure
        for i in range(10):
            subdir = self.temp_path / f"subdir{i}"
            subdir.mkdir()
            for j in range(5):
                (subdir / f"file{j}.txt").write_text("content")
                (subdir / f"file{j}.py").write_text("content")

        results = find_paths(self.temp_dir, include=["*.py"])

        # Should find all Python files
        files = [item[0] for item in results if item[1] == 'file']
        self.assertGreater(len(files), 50)  # Should have many Python files

        # All should be Python files
        for file_path in files:
            self.assertTrue(file_path.endswith('.py'))

    def test_edge_cases(self):
        """Test edge cases."""
        # Test with single file
        single_file_dir = tempfile.mkdtemp()
        try:
            (Path(single_file_dir) / "single.txt").write_text("content")
            results = find_paths(single_file_dir, include=["*.txt"])
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0], ("single.txt", "file"))
        finally:
            import shutil
            shutil.rmtree(single_file_dir)

        # Test with single directory
        single_dir_dir = tempfile.mkdtemp()
        try:
            (Path(single_dir_dir) / "single").mkdir()
            results = find_paths(single_dir_dir, include=["single/"])
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0], ("single", "directory"))
        finally:
            import shutil
            shutil.rmtree(single_dir_dir)

    def test_return_type_consistency(self):
        """Test that return types are consistent."""
        results = find_paths(self.temp_dir, include=["*.py"])

        for path, file_type in results:
            self.assertIsInstance(path, str)
            self.assertIn(file_type, ['file', 'directory'])

    def test_relative_paths(self):
        """Test that all returned paths are relative to the base directory."""
        results = find_paths(self.temp_dir, include=["*.py"])

        for path, _ in results:
            # Should not contain absolute path components
            self.assertFalse(path.startswith('/'))
            self.assertFalse('\\' in path)  # No Windows-style paths
            # Should not contain '..' (parent directory references)
            self.assertNotIn('..', path)

    def test_no_duplicates(self):
        """Test that no duplicate paths are returned."""
        results = find_paths(self.temp_dir, include=["*.py"])

        paths = [item[0] for item in results]
        self.assertEqual(len(paths), len(set(paths)), "Found duplicate paths")


if __name__ == '__main__':
    unittest.main()
