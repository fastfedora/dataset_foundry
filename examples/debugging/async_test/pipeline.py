from dataset_foundry.actions.dataset.if_dataset import if_dataset
from dataset_foundry.actions.dataset.run_pipeline import run_pipeline
from dataset_foundry.actions.dataset.load_dataset import load_dataset
from dataset_foundry.actions.dataset.reset_dataset import reset_dataset
from dataset_foundry.actions.item.log_item import log_item
from dataset_foundry.actions.item.log_counter import log_counter
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.core.template import Template

root_module = "examples.debugging"

pipeline = ItemPipeline(
    name="async_test",
    metadata={
        "version": "0.1.0",
        "author": "fastfedora",
        "description": "Generate scenarios and run an async log counter for each one",
    },
    options={
        "max_concurrent_items": 3,
    },
    setup=[
        if_dataset('not path_exists(f"{context.output_dir}/scenarios.yaml")', [
            run_pipeline(pipeline=f"{root_module}.generate_scenarios.pipeline"),
        ]),
        reset_dataset(), # `generate_spec` creates one item per spec file, not one per sample
        load_dataset(
            filename="scenarios.yaml",
            property="scenario",
            id_generator=lambda index, data: f"{index+1:03d}_{data['name']}",
        ),
    ],
    steps=[
        log_item(message=Template("Running async test for {id}...")),
        log_counter(start=1, count=10, interval=1000, message=Template("[{id}] Iteration {count}")),
    ]
)
