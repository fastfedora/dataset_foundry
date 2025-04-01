import argparse
from pathlib import Path
import yaml
import shutil

def load_info(info_file: Path) -> dict:
    """Load info.yaml file"""
    if not info_file.exists():
        return {}

    with open(info_file) as f:
        return yaml.safe_load(f)

def save_info(info_file: Path, data: dict):
    """Save info.yaml file"""
    with open(info_file, 'w') as f:
        yaml.safe_dump(data, f, sort_keys=False)

def renumber_sample(sample_dir: Path, new_index: int) -> None:
    """Renumber a single sample directory"""
    info_file = sample_dir / 'info.yaml'
    info = load_info(info_file)

    # Get name from info.yaml
    name = info.get('name', 'unknown')

    # Update ID in info.yaml
    new_id = f"{new_index:03d}_{name}"
    info['id'] = new_id
    save_info(info_file, info)

    # Rename directory
    new_dir = sample_dir.parent / f"{new_index:03d}_{name}"
    if new_dir != sample_dir:
        shutil.move(str(sample_dir), str(new_dir))

def main():
    parser = argparse.ArgumentParser(description='Renumber samples in a dataset')
    parser.add_argument('dataset_dir', help='Directory containing the dataset')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir).resolve()
    if not dataset_dir.is_dir():
        print(f"Error: {dataset_dir} is not a directory")
        return

    # Get all sample directories and sort them
    sample_dirs = sorted([
        d for d in dataset_dir.iterdir()
        if d.is_dir()
    ])

    # Process each sample directory
    for index, sample_dir in enumerate(sample_dirs, start=1):
        if args.dry_run:
            print(f"Would renumber {sample_dir.name} to {index:03d}_...")
        else:
            print(f"Renumbering {sample_dir.name}...")
            renumber_sample(sample_dir, index)

# python renumber_dataset.py datasets/my_dataset --dry-run
# python renumber_dataset.py datasets/my_dataset
if __name__ == '__main__':
    main()