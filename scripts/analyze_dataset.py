import argparse
from pathlib import Path
import ast
import statistics
from typing import Dict, List, NamedTuple

class CodeStats(NamedTuple):
    """Statistics for a single code sample"""
    name: str
    source_lines: int
    test_count: int
    source_type: str  # 'class' or 'function'

def count_tests(test_file: Path) -> int:
    """Count number of test functions in a test file"""
    if not test_file.exists():
        return 0

    with open(test_file) as f:
        tree = ast.parse(f.read())

    return len([
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name.startswith('test_')
    ])

def analyze_source(source_file: Path) -> tuple[int, str]:
    """Analyze source file to get line count and top-level definition type"""
    if not source_file.exists():
        return 0, 'unknown'

    with open(source_file) as f:
        content = f.read()
        tree = ast.parse(content)

    # Get first class or function definition
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            return len(content.splitlines()), 'class'
        elif isinstance(node, ast.FunctionDef):
            return len(content.splitlines()), 'function'

    return len(content.splitlines()), 'unknown'

def analyze_sample(sample_dir: Path) -> CodeStats:
    """Analyze a single sample directory"""
    source_file = sample_dir / 'source.py'
    test_file = sample_dir / 'test.py'

    source_lines, source_type = analyze_source(source_file)
    test_count = count_tests(test_file)

    return CodeStats(
        name=sample_dir.name,
        source_lines=source_lines,
        test_count=test_count,
        source_type=source_type
    )

def print_summary(stats: List[CodeStats]):
    """Print summary statistics for the dataset"""
    if not stats:
        print("No samples found")
        return

    lines = [s.source_lines for s in stats]
    print("\nDataset Summary:")
    print(f"Total samples: {len(stats)}")
    print(f"\nLines of code per file:")
    print(f"  Min: {min(lines)}")
    print(f"  Max: {max(lines)}")
    print(f"  Avg: {statistics.mean(lines):.1f}")

    by_type = {'class': 0, 'function': 0, 'unknown': 0}
    for s in stats:
        by_type[s.source_type] += 1
    print(f"\nSource types:")
    print(f"  Classes: {by_type['class']}")
    print(f"  Functions: {by_type['function']}")

    total_tests = sum(s.test_count for s in stats)
    print(f"\nUnit tests:")
    print(f"  Total: {total_tests}")
    print(f"  Avg per sample: {total_tests/len(stats):.1f}")

def print_details(stats: List[CodeStats]):
    """Print details for each sample"""
    print("\nSample Details:")
    print(f"{'Name':<40} {'Lines':<8} {'Tests':<8} {'Type':<10}")
    print("-" * 66)
    for s in sorted(stats, key=lambda x: x.name):
        print(f"{s.name:<40} {s.source_lines:<8} {s.test_count:<8} {s.source_type:<10}")
def main():
    parser = argparse.ArgumentParser(description='Analyze code samples in a dataset')
    parser.add_argument('dataset_dir', help='Directory containing the dataset')
    parser.add_argument('--details', action='store_true',
                       help='Show details for each sample')
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir).resolve()
    if not dataset_dir.is_dir():
        print(f"Error: {dataset_dir} is not a directory")
        return

    # Analyze each sample directory
    stats = []
    for sample_dir in dataset_dir.iterdir():
        if sample_dir.is_dir():
            stats.append(analyze_sample(sample_dir))

    print_summary(stats)
    if args.details:
        print_details(stats)

if __name__ == '__main__':
    main()