import logging
from typing import List, Optional, Callable

from .dataset import Dataset
from .dataset_item import DatasetItem
from .context import Context
from .pipeline import Pipeline

logger = logging.getLogger(__name__)

class ItemPipeline(Pipeline):
    """
    A pipeline that can be used to process a dataset of items.
    """
    _item_steps: List[Callable]

    def __init__(
            self,
            name: str,
            steps: List[Callable],
            setup: Optional[List[Callable]] = None,
            teardown: Optional[List[Callable]] = None
        ):
        """
        Initialize the item pipeline.

        Args:
            name (str): The name of the pipeline.
            steps (List[Callable]): The steps to execute on each item.
            setup (Optional[List[Callable]]): The steps to setup the dataset before processing
            teardown (Optional[List[Callable]]): The steps to cleanup resources after processing.
        """
        super().__init__(name=name, setup=setup, teardown=teardown)
        self._item_steps = steps

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
        for action in self._item_steps:
            await action(item, context)
