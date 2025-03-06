from dataset_foundry.actions.dataset.load_dataset_from_directory import load_dataset_from_directory
from dataset_foundry.actions.item.if_item import if_item
from dataset_foundry.actions.item.log_item import log_item
from dataset_foundry.actions.item.run_unit_tests import run_unit_tests
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.core.template import Template

pipeline = ItemPipeline(
    name="run_unit_tests",
    setup=[
        load_dataset_from_directory(include="{id|[0-9]*}_{function_name}/info.yaml"),
    ],
    steps=[
        run_unit_tests(filename=Template("{id}_{function_name}/test.py")),
        log_item(properties=['test_result']),
        if_item("context.log_level == 'debug' and not test_result.success", [
            log_item(properties=['test_result.stdout']),
        ])
    ]
)
