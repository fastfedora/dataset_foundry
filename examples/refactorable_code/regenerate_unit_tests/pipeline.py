from pathlib import Path

from dataset_foundry.actions.dataset.load_dataset_from_directory import load_dataset_from_directory
from dataset_foundry.actions.item.generate_item import generate_item
from dataset_foundry.actions.item.if_item import if_item
from dataset_foundry.actions.item.log_item import log_item
from dataset_foundry.actions.item.save_item_chat import save_item_chat
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.run_unit_tests import run_unit_tests
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.actions.item.set_item_property import set_item_property
from dataset_foundry.actions.item.while_item import while_item
from dataset_foundry.core.key import Key
from dataset_foundry.core.template import Template
from dataset_foundry.core.item_pipeline import ItemPipeline

pipeline = ItemPipeline(
    name="regenerate_unit_tests",
    metadata={
        "version": "0.1.0",
        "author": "fastfedora",
        "description": "Regenerate unit tests until they pass or the retry limit is reached",
    },
    config=Path(__file__).parent / "config.yaml",
    setup=[
        # TODO: Can we make this conditional based on whether data items already exist? [fastfedora 28.Feb.25]
        load_dataset_from_directory(include="{id}/info.yaml"),
        load_dataset_from_directory(include="{id}/source.py", property="code", merge=True),
        load_dataset_from_directory(include="{id}/test.py", property="unit_tests", merge=True),
    ],
    steps=[
        set_item_property(key="unit_tests_pass", value="false"),
        while_item("unit_tests_pass != 'true' and iteration < 2", [
            run_unit_tests(filename=Template("{id}/test.py"), property="original_result"),
            log_item(properties=['original_result']),
            if_item("original_result.success", [
                set_item_property(key="unit_tests_pass", value="true"),
            ]),
            if_item("unit_tests_pass != 'true'", [
                log_item(message=Template("Regenerating unit tests for {id}...")),
                generate_item(prompt=Key("context.prompts.regenerate_unit_tests")),
                if_item("context.log_level == 'debug'", [
                    log_item(properties=['original_result.stdout']),
                ]),
                save_item_chat(filename=Template("{id}/chat_{metadata.created_at}_regenerate_unit_tests.yaml")),
                parse_item(code_block="python", output_key="unit_tests"),
                save_item(
                    contents=(lambda item: item.data["unit_tests"]),
                    filename=Template("{id}/test_updated.py"),
                ),
                run_unit_tests(
                    filename=Template("{id}/test_updated.py"),
                    property="updated_result"
                ),
                log_item(properties=['updated_result']),
                if_item("context.log_level == 'debug' and not updated_result.success", [
                    log_item(properties=['updated_result.stdout']),
                ]),
                if_item("updated_result.num_passed > original_result.num_passed", [
                    save_item(
                        contents=(lambda item: item.data["unit_tests"]),
                        filename=Template("{id}/test.py")
                    ),
                    if_item("updated_result.success", [
                        set_item_property(key="unit_tests_pass", value="true"),
                    ]),
                ]),
                # TODO: Delete `_updated.py` file [fastfedora 15.Feb.25]
            ])
        ]),
    ]
)
