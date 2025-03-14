from dataset_foundry.actions.dataset.if_dataset import if_dataset
from dataset_foundry.actions.dataset.reset_dataset import reset_dataset
from dataset_foundry.actions.dataset.run_pipeline import run_pipeline
from dataset_foundry.actions.dataset.load_dataset_from_directory import load_dataset_from_directory
from dataset_foundry.actions.item.log_item import log_item
from dataset_foundry.actions.item.do_item_steps import do_item_steps
from dataset_foundry.actions.item.if_item import if_item
from dataset_foundry.actions.item.set_item_property import set_item_property
from dataset_foundry.actions.item.while_item import while_item
from dataset_foundry.core.template import Template
from dataset_foundry.core.item_pipeline import ItemPipeline

root_module = "examples.refactorable_code"

pipeline = ItemPipeline(
    name="generate_refactorable_code_using_scenarios",
    metadata={
        "version": "0.1.0",
        "author": "fastfedora",
        "description": "Generate refactorable code using scenario -> spec -> code + unit tests",
    },
    setup=[
        if_dataset('not path_exists(f"{context.output_dir}/scenarios.yaml")', [
            run_pipeline(pipeline=f"{root_module}.generate_scenarios.pipeline"),
            reset_dataset(), # `generate_spec` creates one item per spec file, not one per sample
        ]),
        if_dataset('not path_exists(f"{context.output_dir}/spec_*.yaml")', [
            run_pipeline(pipeline=f"{root_module}.generate_spec_from_scenarios.pipeline"),
            reset_dataset(), # `generate_spec` creates one item per spec file, not one per sample
        ]),
        load_dataset_from_directory(
            include="spec_{id}.yaml",
            property="spec",
            merge=True,
        ),
    ],
    steps=[
        set_item_property(key="status", value="not-done"),
        while_item("status != 'done' and iteration < 2", [
            if_item('path_exists(f"{context.output_dir}/{id}/source.py")', [
                do_item_steps(pipeline=f"{root_module}.run_unit_tests.pipeline"),
                if_item("unit_tests_pass == 'true'", [
                    set_item_property(key="status", value="done"),
                    log_item(message=Template(
                        "Skipping sample {id} because it already exists and unit tests pass"
                    )),
                ]),
            ]),
            if_item("status != 'done'", [
                do_item_steps(pipeline=f"{root_module}.generate_all_from_spec.pipeline_separate_specs"),
                do_item_steps(pipeline=f"{root_module}.regenerate_unit_tests.pipeline"),
                if_item("unit_tests_pass == 'true'", [
                    set_item_property(key="status", value="done"),
                ]),
            ]),
        ]),
    ]
)
