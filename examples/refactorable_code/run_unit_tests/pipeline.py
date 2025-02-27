from dataset_foundry.actions.dataset.load_dataset_from_directory import load_dataset_from_directory
from dataset_foundry.actions.item.if_item import if_item
from dataset_foundry.actions.item.log_item import log_item
from dataset_foundry.actions.item.run_unit_tests import run_unit_tests
from dataset_foundry.core.pipeline import Pipeline

pipeline = Pipeline(
    setup=[
        load_dataset_from_directory(include="item_{id|[0-9]*}_{function_name}.json"),
        # TODO: This captures the `_test` file too. Figure out a way to get a good regex here, or
        #       just add an `exclude` pattern and rename `files` to be `include`
        #       [fastfedora 11.Feb.25]
        #
        # load_dataset_from_directory(
        #     files="item_{id|[0-9]*}_{function_name|^(?!.*_test$)[\w-]+$}.py",
        #     property="code",
        #     merge=True,
        # ),
    ],
    steps=[
        run_unit_tests(filename="item_{id}_{function_name}_test.py"),
        log_item(properties=['test_result']),
        if_item("not item.data['test_result'].success", [
            log_item(properties=['test_result.stdout']),
        ])
    ]
)
