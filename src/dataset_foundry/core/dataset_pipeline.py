import logging
from pathlib import Path
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
            steps: List[PipelineAction],
            name: Optional[str] = None,
            config: Optional[Path|str|dict] = {},
            metadata: Optional[dict] = {},
            setup: Optional[List[PipelineAction]] = None,
            teardown: Optional[List[PipelineAction]] = None
        ):
        """
        Initialize the item pipeline.

        Args:
            steps (List[PipelineAction]): The steps to execute on each item.
            name (str): The name of the pipeline.
            config (Path|str|dict): The configuration, or path to a config file, for the pipeline.
            metadata (dict): Metadata about the pipeline.
            setup (Optional[List[PipelineAction]]): The steps to setup the dataset before processing
            teardown (Optional[List[PipelineAction]]): The steps to cleanup resources after
                processing.
        """
        super().__init__(
            name=name,
            config=config,
            metadata=metadata,
            setup=setup,
            teardown=teardown
        )
        self._steps = steps

    async def execute(self, dataset: Optional[Dataset], context: Optional[Context]) -> None:
        """
        Execute the data-processing steps of this pipeline.

        Args:
            dataset (Dataset): The dataset to process.
            context (Context): The context to use for processing.
        """
        logger.info(f"Processing {len(self._steps)} dataset pipeline steps")
        await super()._do_steps(self._steps, dataset, context)
