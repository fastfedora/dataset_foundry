import argparse
from pathlib import Path

def clean_sample(sample_dir: Path, dry_run: bool = False) -> bool:
    """Remove test_updated.py from a sample directory if it exists"""
    test_file = sample_dir / 'test_updated.py'
    if test_file.exists():
        if dry_run:
            print(f"Would remove {test_file}")
        else:
            print(f"Removing {test_file}")
            test_file.unlink()
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description='Clean test_updated.py files from dataset')
    parser.add_argument('dataset_dir', help='Directory containing the dataset')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir).resolve()
    if not dataset_dir.is_dir():
        print(f"Error: {dataset_dir} is not a directory")
        return

    # Process each sample directory
    cleaned = 0
    for sample_dir in dataset_dir.iterdir():
        if sample_dir.is_dir():
            if clean_sample(sample_dir, args.dry_run):
                cleaned += 1

    action = "Would remove" if args.dry_run else "Removed"
    print(f"\n{action} test_updated.py from {cleaned} samples")

if __name__ == '__main__':
    # python clean_dataset.py datasets/my_dataset --dry-run
    # python clean_dataset.py datasets/my_dataset
    main()