from dataset_foundry.actions.dataset.reset_dataset import reset_dataset
from dataset_foundry.actions.dataset.run_pipeline import run_pipeline
from dataset_foundry.actions.dataset.load_dataset import load_dataset
from dataset_foundry.actions.item.do_item_steps import do_item_steps
from dataset_foundry.actions.item.if_item import if_item
from dataset_foundry.actions.item.set_item_property import set_item_property
from dataset_foundry.actions.item.while_item import while_item
from dataset_foundry.core.template import Template
from dataset_foundry.core.item_pipeline import ItemPipeline

root_module = "examples.refactorable_code"

pipeline = ItemPipeline(
    name="generate_refactorable_code",
    setup=[
        run_pipeline(pipeline=f"{root_module}.generate_spec.pipeline"),
        reset_dataset(), # `generate_spec` creates one item per spec file, not one per sample
        load_dataset(filename="specs.yaml", property="spec"),
    ],
    steps=[
        set_item_property(key="status", value="not-done"),
        while_item("item.data['status'] != 'done' and iteration < 2", [
            do_item_steps(pipeline=f"{root_module}.generate_all_from_spec.pipeline"),
            set_item_property(key="function_name", value=Template("{spec.name}")),
            do_item_steps(pipeline=f"{root_module}.regenerate_unit_tests.pipeline"),
            if_item("item.data['unit_tests_pass'] == 'true'", [
                set_item_property(key="status", value="done"),
            ]),
        ]),
    ]
)
