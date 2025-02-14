import logging
from typing import List, Optional, Callable

from .dataset import Dataset
from .dataset_item import DatasetItem
from .context import Context

logger = logging.getLogger(__name__)

class Pipeline:
    """
    A pipeline that can be used to process a dataset.
    """
    _process_actions: List[Callable]
    _setup_actions: List[Callable] = None
    _teardown_actions: List[Callable] = None

    def __init__(
            self,
            actions: List[Callable],
            setup: Optional[List[Callable]] = None,
            teardown: Optional[List[Callable]] = None
        ):
        self._process_actions = actions
        self._setup_actions = setup
        self._teardown_actions = teardown

    async def run(
            self,
            dataset: Optional[Dataset] = None,
            context: Optional[Context] = None,
            args: Optional[dict] = None,
        ):
        dataset = dataset if dataset else Dataset()
        context = context if context else Context()

        if args:
            context.update(args)

        await self.setup(dataset, context)
        await self.process_dataset(dataset, context)
        await self.teardown(dataset, context)

    async def setup(self, dataset: Dataset, context: Context):
        if self._setup_actions:
            logger.info("Setting up pipeline")
            for action in self._setup_actions:
                # TODO: Add error handling [twl 7.Feb.25]
                await action(dataset, context)

    async def process_dataset(self, dataset: Optional[Dataset], context: Optional[Context]):
        logger.info(f"Processing {len(dataset.items)} dataset items")
        for item in dataset.items:
            # TODO: Add error handling [twl 7.Feb.25]
            await self.process_data_item(item, context)

    async def teardown(self, dataset: Optional[Dataset], context: Optional[Context]):
        if self._teardown_actions:
            logger.info("Tearing down pipeline")
            for action in self._teardown_actions:
                await action(dataset, context)

    async def process_data_item(self, item: Optional[DatasetItem], context: Optional[Context]):
        # TODO: Add error handling [twl 7.Feb.25]
        for action in self._process_actions:
            await action(item, context)
