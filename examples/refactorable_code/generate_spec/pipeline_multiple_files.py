from dataset_foundry.actions.dataset.generate_dataset import generate_dataset
from dataset_foundry.actions.dataset.load_context import load_context
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.key import Key
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.utils.parse.extract_code_block import extract_code_block

import yaml

def output_parser(content):
    return yaml.safe_load(extract_code_block(content, "yaml"))

pipeline = ItemPipeline(
    setup=[
        load_context(filename="config.yaml"),
        generate_dataset(
            prompt=Key("prompts.generate"),
            parser=(lambda _content, _context: output_parser),
        ),
    ],
    steps=[
        save_item(filename="spec_{id}.yaml", format="yaml")
    ]
)
