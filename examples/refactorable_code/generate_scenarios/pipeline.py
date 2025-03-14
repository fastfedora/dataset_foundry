from pathlib import Path

from dataset_foundry.actions.dataset.generate_dataset import generate_dataset
from dataset_foundry.actions.item.log_item import log_item
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.key import Key
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.core.template import Template

pipeline = ItemPipeline(
    name="generate_scenarios",
    metadata={
        "version": "0.1.0",
        "author": "fastfedora",
        "description": "Generate scenarios for refactorable code",
    },
    config=Path(__file__).parent / "config.yaml",
    setup=[
      generate_dataset(prompt=Key("context.prompts.generate_scenarios")),
    ],
    steps=[
      log_item(message=Template("Generating scenario for {id}...")),
      parse_item(code_block="yaml", output_key="scenarios"),
      save_item(contents=Key("scenarios"), filename="scenarios.yaml")
    ]
)
