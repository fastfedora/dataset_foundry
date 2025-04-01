from pathlib import Path

from dataset_foundry.actions.dataset.load_dataset import load_dataset
from dataset_foundry.actions.item.generate_item import generate_item
from dataset_foundry.actions.item.save_item_chat import save_item_chat
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.actions.item.set_item_property import set_item_property
from dataset_foundry.core.key import Key
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.core.template import Template

pipeline = ItemPipeline(
    name="generate_unit_tests_from_spec",
    metadata={
        "version": "0.1.0",
        "author": "fastfedora",
        "description": "Generate unit tests from a spec",
    },
    config=Path(__file__).parent / "config.yaml",
    setup=[
        load_dataset(
            filename="specs.yaml",
            id_generator=lambda index, data: f"{index+1:03d}_{data['name']}",
        ),
    ],
    steps=[
        set_item_property(key="source", value="source.py"),
        set_item_property(key="test", value="test.py"),
        generate_item(prompt=Key("context.prompts.generate")),
        save_item_chat(filename=Template("{id}/chat_{metadata.created_at}_unit_tests_from_spec.yaml")),
        parse_item(code_block="python", output_key="code"),
        save_item(contents=Key("code"), filename=Template("{id}/{test}")),
    ]
)
