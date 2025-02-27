from dataset_foundry.actions.dataset.load_dataset import load_dataset
from dataset_foundry.actions.dataset.load_context import load_context
from dataset_foundry.actions.dataset.load_context import load_context
from dataset_foundry.actions.item.generate_item import generate_item
from dataset_foundry.actions.item.save_item_chat import save_item_chat
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.key import Key
from dataset_foundry.core.pipeline import Pipeline
from dataset_foundry.utils.collections.omit import omit

pipeline = Pipeline(
    setup=[
        load_context(filename="config.yaml"),
        load_dataset(filename="specs.yaml", property="spec"),
    ],
    actions=[
        generate_item(prompt=Key("prompts.generate")),
        save_item_chat(filename="chat_generate_all_from_spec_{id}.yaml"),
        parse_item(xml_block="function", output_key="code"),
        parse_item(xml_block="unit_tests", output_key="unit_tests"),
        save_item(contents=Key("code"), filename="item_{id}_{spec.name}.py"),
        save_item(contents=Key("unit_tests"), filename="item_{id}_{spec.name}_test.py"),
        save_item(
            contents=(lambda item: {
                'id': item.id,
                **omit(['code', 'response', 'messages', 'output', 'unit_tests'], item.data),
            }),
            filename="item_{id}_{spec.name}.json",
            format="json"
        ),
    ]
)
