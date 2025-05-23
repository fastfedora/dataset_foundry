from dataset_foundry.actions.dataset.load_dataset_from_directory import load_dataset_from_directory
from dataset_foundry.actions.item.if_item import if_item
from dataset_foundry.actions.item.log_item import log_item
from dataset_foundry.actions.item.run_unit_tests import run_unit_tests
from dataset_foundry.actions.item.set_item_property import set_item_property
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.core.template import Template

pipeline = ItemPipeline(
    name="run_unit_tests",
    metadata={
        "version": "0.1.0",
        "author": "fastfedora",
    },
    setup=[
        load_dataset_from_directory(include="{id}/info.yaml"),
    ],
    steps=[
        run_unit_tests(filename=Template("{id}/test.py")),
        log_item(properties=['test_result']),
        if_item("test_result.success", [
            set_item_property(key="unit_tests_pass", value="true"),
        ], [
            set_item_property(key="unit_tests_pass", value="false"),
            if_item("context.log_level == 'debug'", [
                log_item(properties=['test_result.stdout']),
            ]),
        ]),
    ]
)
