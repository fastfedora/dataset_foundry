from dataset_foundry.actions.dataset.reset_dataset import reset_dataset
from dataset_foundry.actions.dataset.run_pipeline import run_pipeline
from dataset_foundry.core.dataset_pipeline import DatasetPipeline

root_module = "examples.refactorable_code"

pipeline = DatasetPipeline(
    name="generate_refactorable_code",
    steps=[
        run_pipeline(pipeline=f"{root_module}.generate_spec.pipeline"),
        reset_dataset(), # `generate_spec` creates one item per spec file, not one per sample
        run_pipeline(pipeline=f"{root_module}.generate_all_from_spec.pipeline"),
        reset_dataset(), # Next pipeline not setup yet to use previous pipeline's output
        run_pipeline(pipeline=f"{root_module}.regenerate_unit_tests.pipeline"),
    ],
)
