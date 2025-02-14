from dataset_foundry.actions.dataset.generate_dataset import generate_dataset
from dataset_foundry.actions.dataset.load_context import load_context
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.key import Key
from dataset_foundry.core.pipeline import Pipeline

pipeline = Pipeline(
    setup=[
      load_context(filename="config.yaml"),
      generate_dataset(prompt=Key("prompts.generate")),
    ],
    actions=[
      parse_item(code_block="yaml", output_key="output"),
      save_item(contents=(lambda item: item.data["output"]), filename="specs.yaml")
    ]
)
