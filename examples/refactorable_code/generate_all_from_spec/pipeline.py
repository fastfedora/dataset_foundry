from pathlib import Path

from dataset_foundry.actions.dataset.load_dataset import load_dataset
from dataset_foundry.actions.item.generate_item import generate_item
from dataset_foundry.actions.item.log_item import log_item
from dataset_foundry.actions.item.save_item_chat import save_item_chat
from dataset_foundry.actions.item.set_item_property import set_item_property
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.key import Key
from dataset_foundry.core.template import Template
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.utils.collections.pick import pick

pipeline = ItemPipeline(
    name="generate_all_from_spec",
    config=Path(__file__).parent / "config.yaml",
    setup=[
        load_dataset(filename="specs.yaml", property="spec"),
    ],
    steps=[
        log_item(message=Template("Generating code and unit tests for {id}...")),
        set_item_property(key="folder", value=Template("{id}_{spec.name}")),
        set_item_property(key="source", value="source.py"),
        set_item_property(key="test", value="test.py"),
        generate_item(prompt=Key("context.prompts.generate_functions_and_classes")),
        save_item_chat(filename=Template("chat_generate_all_from_spec_{id}.yaml")),
        parse_item(xml_block="code", output_key="code"),
        parse_item(xml_block="unit_tests", output_key="unit_tests"),
        save_item(contents=Key("code"), filename=Template("{folder}/source.py")),
        save_item(contents=Key("unit_tests"), filename=Template("{folder}/test.py")),
        save_item(
            contents=(lambda item: {
                'id': item.id,
                'name': item.data['spec']['name'],
                'language': item.data['spec']['language'],
                **pick(['spec', 'source', 'test'], item.data),
            }),
            filename=Template("{folder}/info.yaml"),
            format="yaml"
        ),
    ]
)
