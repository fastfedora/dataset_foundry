import importlib
from typing import Callable, Optional, Union

from ...core.context import Context
from ...core.dataset import Dataset
from ...core.pipeline import Pipeline
from ...core.key import Key
from ...types.dataset_action import DatasetAction
from ...utils.params.resolve_dataset_value import resolve_dataset_value

def run_pipeline(
        pipeline: Union[Callable,Key,Pipeline,str],
        args: Optional[Union[Callable,Key,dict]] = None,
    ) -> DatasetAction:
    async def run_pipeline_action(dataset: Dataset, context: Context):
        resolved_pipeline = resolve_dataset_value(
            pipeline,
            dataset,
            context,
            required_as="pipeline"
        )
        resolved_args = resolve_dataset_value(args, dataset, context)

        if isinstance(resolved_pipeline, str):
            resolved_pipeline = importlib.import_module(resolved_pipeline).pipeline

        if isinstance(resolved_pipeline, Pipeline):
            await resolved_pipeline.run(dataset, context, resolved_args)
        else:
            raise ValueError(f"The pipeline {resolved_pipeline} is not a valid pipeline")

    return run_pipeline_action
