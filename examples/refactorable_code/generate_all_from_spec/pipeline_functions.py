from pathlib import Path

from dataset_foundry.actions.dataset.load_dataset import load_dataset
from dataset_foundry.actions.item.generate_item import generate_item
from dataset_foundry.actions.item.save_item_chat import save_item_chat
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.key import Key
from dataset_foundry.core.template import Template
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.utils.collections.omit import omit

pipeline = ItemPipeline(
    name="generate_all_from_spec_functions",
    config=Path(__file__).parent / "config.yaml",
    setup=[
        load_dataset(filename="specs.yaml", property="spec"),
    ],
    steps=[
        generate_item(prompt=Key("prompts.generate_functions")),
        save_item_chat(filename=Template("chat_generate_all_from_spec_{id}.yaml")),
        parse_item(xml_block="function", output_key="code"),
        parse_item(xml_block="unit_tests", output_key="unit_tests"),
        save_item(contents=Key("code"), filename=Template("item_{id}_{spec.name}.py")),
        save_item(contents=Key("unit_tests"), filename=Template("item_{id}_{spec.name}_test.py")),
        save_item(
            contents=(lambda item: {
                'id': item.id,
                **omit(['code', 'response', 'messages', 'output', 'unit_tests'], item.data),
            }),
            filename=Template("item_{id}_{spec.name}.json"),
            format="json"
        ),
    ]
)
