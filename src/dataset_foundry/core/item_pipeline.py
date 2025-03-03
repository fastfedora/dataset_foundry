import logging
from pathlib import Path
from typing import List, Optional

from ..types.item_action import ItemAction
from .dataset import Dataset
from .dataset_item import DatasetItem
from .context import Context
from .pipeline import Pipeline, PipelineAction

logger = logging.getLogger(__name__)

class ItemPipeline(Pipeline):
    """
    A pipeline that can be used to process a dataset of items.
    """
    _steps: List[ItemAction]

    def __init__(
            self,
            steps: List[ItemAction],
            name: Optional[str] = None,
            config: Optional[Path|str|dict] = {},
            setup: Optional[List[PipelineAction]] = None,
            teardown: Optional[List[PipelineAction]] = None
        ):
        """
        Initialize the item pipeline.

        Args:
            name (str): The name of the pipeline.
            steps (List[ItemAction]): The steps to execute on each item.
            setup (Optional[List[PipelineAction]]): The steps to setup the dataset before processing
            teardown (Optional[List[PipelineAction]]): The steps to cleanup resources after
                processing.
        """
        super().__init__(name=name, config=config, setup=setup, teardown=teardown)
        self._steps = steps

    async def execute(self, dataset: Optional[Dataset], context: Optional[Context]) -> None:
        """
        Execute the data-processing steps of this pipeline.

        Args:
            dataset (Dataset): The dataset to process.
            context (Context): The context to use for processing.
        """
        logger.info(f"Processing {len(dataset.items)} dataset items")
        for item in dataset.items:
            # TODO: Add error handling [twl 7.Feb.25]
            await self.process_data_item(item, context)

    async def process_data_item(self, item: Optional[DatasetItem], context: Optional[Context]):
        # TODO: Add error handling [twl 7.Feb.25]
        for action in self._steps:
            try:
                await action(item, context)
            except Exception as e:
                logger.error(f"Error during item pipeline {self.name} in step {action}: {e}")
                raise e

