from pathlib import Path

from dataset_foundry.actions.dataset.generate_dataset import generate_dataset
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.key import Key
from dataset_foundry.core.item_pipeline import ItemPipeline

pipeline = ItemPipeline(
    name="generate_spec_functions",
    config=Path(__file__).parent / "config.yaml",
    setup=[
      generate_dataset(prompt=Key("prompts.generate_functions")),
    ],
    steps=[
      parse_item(code_block="yaml", output_key="specs"),
      save_item(contents=Key("specs"), filename="specs.yaml")
    ]
)
