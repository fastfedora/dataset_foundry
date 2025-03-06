from pathlib import Path

from dataset_foundry.actions.dataset.generate_dataset import generate_dataset
from dataset_foundry.actions.item.log_item import log_item
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.key import Key
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.core.template import Template

pipeline = ItemPipeline(
    name="generate_spec",
    metadata={
        "version": "0.1.0",
        "author": "fastfedora",
        "description": "Generate a spec for refactorable code using both functions and classes",
    },
    config=Path(__file__).parent / "config.yaml",
    # TODO: Think about a way to specify the parameters a pipeline accepts [fastfedora 4.Mar.25]
    # params={
    #     "num_samples": {
    #         "type": "int",
    #         "default": 10,
    #     },
    # },
    # metadata={
    #     "version": 1,
    # },
    setup=[
      generate_dataset(prompt=Key("context.prompts.generate_functions_and_classes")),
    ],
    steps=[
      log_item(message=Template("Generating spec for {id}...")),
      parse_item(code_block="yaml", output_key="specs"),
      save_item(contents=Key("specs"), filename="specs.yaml")
    ]
)
