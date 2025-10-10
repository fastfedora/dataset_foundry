import logging
import anyio
from pathlib import Path
from typing import List, Optional

from ..types.item_action import ItemAction
from .pipeline_service import pipeline_service
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
            metadata: Optional[dict] = {},
            setup: Optional[List[PipelineAction]] = None,
            teardown: Optional[List[PipelineAction]] = None,
        ):
        """
        Initialize the item pipeline.

        Args:
            steps (List[ItemAction]): The steps to execute on each item.
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
        max_concurrent_items = context.params.get("max_concurrent_items", 1)
        limiter = anyio.CapacityLimiter(max_concurrent_items)

        logger.info(f"Processing {len(dataset.items)} dataset items (concurrency: {max_concurrent_items})")

        async def process_with_limit(data_item: DatasetItem):
            await limiter.acquire()
            try:
                info = pipeline_service.start_item(data_item)
                try:
                    await self.process_data_item(data_item, context)
                    pipeline_service.stop_item(info, status="success")
                except Exception:
                    pipeline_service.stop_item(info, status="error")
                    raise
            finally:
                limiter.release()

        if dataset.items:
            async with anyio.create_task_group() as tg:
                for item in dataset.items:
                    tg.start_soon(process_with_limit, item)

    async def process_data_item(self, item: Optional[DatasetItem], context: Optional[Context]):
        for action in self._steps:
            try:
                await action(item, context)
            except Exception as e:
                logger.error(
                    f"Error during item pipeline {self.name} in step {action.__name__}"
                    f" processing item {item.id}: {e}"
                )
                raise e
