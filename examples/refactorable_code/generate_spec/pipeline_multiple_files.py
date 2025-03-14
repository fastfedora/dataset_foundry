from pathlib import Path

from dataset_foundry.actions.dataset.generate_dataset import generate_dataset
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.key import Key
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.utils.parse.extract_code_block import extract_code_block
from dataset_foundry.core.template import Template

import yaml

def output_parser(content):
    return yaml.safe_load(extract_code_block(content, "yaml"))

pipeline = ItemPipeline(
    name="generate_spec_multiple_files",
    metadata={
        "version": "0.1.0",
        "author": "fastfedora",
        "description": "Generate a spec for refactorable code",
    },
    config=Path(__file__).parent / "config.yaml",
    setup=[
        generate_dataset(
            prompt=Key("context.prompts.generate_functions_and_classes"),
            parser=(lambda _content, _context: output_parser),
        ),
    ],
    steps=[
        save_item(filename=Template("spec_{id}.yaml"), format="yaml")
    ]
)
