import logging
from typing import List, Optional

from .dataset import Dataset
from .context import Context
from .pipeline import Pipeline, PipelineAction

logger = logging.getLogger(__name__)

class DatasetPipeline(Pipeline):
    """
    A pipeline that can be used to process a dataset.
    """
    _steps: List[PipelineAction]

    def __init__(
            self,
            name: str,
            steps: List[PipelineAction],
            setup: Optional[List[PipelineAction]] = None,
            teardown: Optional[List[PipelineAction]] = None
        ):
        """
        Initialize the item pipeline.

        Args:
            name (str): The name of the pipeline.
            steps (List[PipelineAction]): The steps to execute on each item.
            setup (Optional[List[PipelineAction]]): The steps to setup the dataset before processing
            teardown (Optional[List[PipelineAction]]): The steps to cleanup resources after
                processing.
        """
        super().__init__(name=name, setup=setup, teardown=teardown)
        self._steps = steps

    async def execute(self, dataset: Optional[Dataset], context: Optional[Context]) -> None:
        """
        Execute the data-processing steps of this pipeline.

        Args:
            dataset (Dataset): The dataset to process.
            context (Context): The context to use for processing.
        """
        logger.info(f"Processing {len(self.steps)} dataset pipeline steps")
        await super._do_steps(self._steps, dataset, context)
