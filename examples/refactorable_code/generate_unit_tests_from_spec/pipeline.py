from pathlib import Path

from dataset_foundry.actions.dataset.load_context import load_context
from dataset_foundry.actions.dataset.load_dataset import load_dataset
from dataset_foundry.actions.item.generate_item import generate_item
from dataset_foundry.actions.item.save_item_chat import save_item_chat
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.key import Key
from dataset_foundry.core.item_pipeline import ItemPipeline

pipeline = ItemPipeline(
    name="generate_unit_tests_from_spec",
    setup=[
        load_context(dir=Path(__file__).parent, filename="config.yaml"),
        load_dataset(filename="specs.yaml"),
    ],
    steps=[
        generate_item(prompt=Key("prompts.generate")),
        save_item_chat(filename="chat_{id}_unit_tests_from_spec.yaml"),
        parse_item(code_block="python", output_key="code"),
        save_item(
            contents=(lambda item: item.data["code"]),
            filename="item_{id}_{name}_test.py",
        ),
    ]
)
