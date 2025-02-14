from dataset_foundry.actions.dataset.load_dataset_from_directory import load_dataset_from_directory
from dataset_foundry.actions.dataset.load_context import load_context
from dataset_foundry.actions.item.generate_item import generate_item
from dataset_foundry.actions.item.if_item import if_item
from dataset_foundry.actions.item.log_item import log_item
from dataset_foundry.actions.item.save_item_chat import save_item_chat
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.run_unit_tests import run_unit_tests
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.key import Key
from dataset_foundry.core.pipeline import Pipeline

pipeline = Pipeline(
    setup=[
        load_context(filename="config.yaml"),
        load_dataset_from_directory(include="func_{id|[0-9]*}_{function_name}.json"),
        load_dataset_from_directory(
            include="func_{id|[0-9]*}_{function_name}.py",
            exclude="func_{id|[0-9]*}_{function_name}_test.py",
            property="code",
            merge=True,
        ),
        load_dataset_from_directory(
            include="func_{id|[0-9]*}_{function_name}_test.py",
            property="unit_tests",
            merge=True,
        ),
    ],
    actions=[
        run_unit_tests(filename="func_{id}_{function_name}_test.py"),
        log_item(properties=['test_returncode']),
        if_item("item.data['test_returncode'] > 0", [
            log_item(properties=['test_stdout']),
            generate_item(prompt=Key("prompts.regenerate_unit_tests")),
            save_item_chat(filename="chat_{id}_regenerate_unit_tests.yaml"),
            parse_item(code_block="python", output_key="unit_tests"),
            save_item(
                contents=(lambda item: item.data["unit_tests"]),
                filename="func_{id}_{function_name}_test_updated.py",
            ),
            run_unit_tests(filename="func_{id}_{function_name}_test_updated.py"),
            log_item(properties=['test_returncode']),
            if_item("item.data['test_returncode'] > 0", [
                log_item(properties=['test_stdout']),
            ]),
        ])
    ]
)
