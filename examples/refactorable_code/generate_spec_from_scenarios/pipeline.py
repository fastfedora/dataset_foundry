from pathlib import Path

from dataset_foundry.actions.dataset.load_dataset import load_dataset
from dataset_foundry.actions.dataset.save_dataset import save_dataset
from dataset_foundry.actions.item.generate_item import generate_item
from dataset_foundry.actions.item.log_item import log_item
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.key import Key
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.core.template import Template

pipeline = ItemPipeline(
    name="generate_spec_from_scenarios",
    metadata={
        "version": "0.1.0",
        "author": "fastfedora",
        "description": "Generate a spec from scenarios",
    },
    config=Path(__file__).parent / "config.yaml",
    setup=[
      load_dataset(
        filename="scenarios.yaml",
        property="scenario",
        id_generator=lambda index, data: f"{index+1:03d}_{data['name']}"
      ),
    ],
    steps=[
      log_item(message=Template("Generating spec for {id}...")),
      generate_item(prompt=Key("context.prompts.generate_spec_functions")),
      parse_item(code_block="yaml", output_key="spec"),
      save_item(contents=Key("spec"), filename=Template("spec_{id}.yaml"))
    ],
    teardown=[
      # TODO: This isn't working as expected.
      save_dataset(filename="specs.yaml", property="spec"),
    ]
)
