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
        load_dataset_from_directory(include="item_{id|[0-9]*}_{function_name}.json"),
        load_dataset_from_directory(
            include="item_{id|[0-9]*}_{function_name}.py",
            exclude="item_{id|[0-9]*}_{function_name}_test*.py",
            property="code",
            merge=True,
        ),
        load_dataset_from_directory(
            include="item_{id|[0-9]*}_{function_name}_test.py",
            property="unit_tests",
            merge=True,
        ),
    ],
    actions=[
        run_unit_tests(filename="item_{id}_{function_name}_test.py", property="original_result"),
        log_item(properties=['original_result']),
        if_item("not item.data['original_result'].success", [
            log_item(message="Regenerating unit tests for {id}..."),
            log_item(properties=['original_result.stdout']),
            generate_item(prompt=Key("prompts.regenerate_unit_tests")),
            save_item_chat(filename="chat_{id}_regenerate_unit_tests.yaml"),
            parse_item(code_block="python", output_key="unit_tests"),
            save_item(
                contents=(lambda item: item.data["unit_tests"]),
                filename="item_{id}_{function_name}_test_updated.py",
            ),
            run_unit_tests(
                filename="item_{id}_{function_name}_test_updated.py",
                property="updated_result"
            ),
            log_item(properties=['updated_result']),
            if_item("not item.data['updated_result'].success", [
                log_item(properties=['updated_result.stdout']),
            ]),
            if_item("item.data['updated_result'].num_passed > item.data['original_result'].num_passed", [
                save_item(
                    contents=(lambda item: item.data["unit_tests"]),
                    filename="item_{id}_{function_name}_test.py"
                ),
                # TODO: Delete `_updated.py` file [fastfedora 15.Feb.25]
            ]),
        ])
    ]
)
