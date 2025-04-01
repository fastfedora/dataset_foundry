from pathlib import Path

from dataset_foundry.actions.dataset.load_dataset_from_directory import load_dataset_from_directory
from dataset_foundry.actions.item.generate_item import generate_item
from dataset_foundry.actions.item.if_item import if_item
from dataset_foundry.actions.item.log_item import log_item
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.core.key import Key
from dataset_foundry.core.template import Template
from dataset_foundry.utils.collections.omit import omit

pipeline = ItemPipeline(
    name="add_refactor_task",
    metadata={
        "version": "0.1.0",
        "author": "fastfedora",
        "description": "Add tasks describing specific refactors to perform to each info.yaml file",
    },
    config=Path(__file__).parent / "config.yaml",
    setup=[
        load_dataset_from_directory(include="{id}/info.yaml"),
        load_dataset_from_directory(include="{id}/source.py", property="code", merge=True),
    ],
    steps=[
        log_item(message=Template("Generating refactor tasks for {id}...")),
        generate_item(prompt=Key("context.prompts.generate_task")),
        parse_item(code_block="yaml", output_key="refactor_tasks"),
        if_item("not skip_saving_refactor_tasks", [
            save_item(
                contents=(lambda item: {
                    'id': item.id,
                **omit(['messages', 'response', 'output', 'code'], item.data),
                }),
                filename=Template("{id}/info.yaml"),
                format="yaml"
            ),
        ]),
    ]
)
