from abc import ABC, abstractmethod
import logging
from typing import List, Optional, Callable

from .dataset import Dataset
from .context import Context

logger = logging.getLogger(__name__)

class Pipeline(ABC):
    """
    A pipeline that can be used to process data.
    """
    _setup_steps: Optional[List[Callable]] = None
    _teardown_steps: Optional[List[Callable]] = None

    name: Optional[str] = None

    def __init__(
            self,
            name: Optional[str] = None,
            setup: Optional[List[Callable]] = None,
            teardown: Optional[List[Callable]] = None
        ):
        """
        Initialize the pipeline.

        Args:
            name (Optional[str]): The name of the pipeline.
            setup (Optional[List[Callable]]): The setup steps to run before processing.
            teardown (Optional[List[Callable]]): The teardown steps to run after processing.
        """
        self.name = name
        self._setup_steps = setup
        self._teardown_steps = teardown

    async def run(
            self,
            dataset: Optional[Dataset] = None,
            context: Optional[Context] = None,
            args: Optional[dict] = None,
        ) -> Dataset:
        """
        Run the pipeline.

        Args:
            dataset (Optional[Dataset]): The dataset to process.
            context (Optional[Context]): The context to use for processing.
            args (Optional[dict]): The arguments to pass to the pipeline.
        """
        dataset = dataset if dataset else Dataset()
        context = context if context else Context()

        if args:
            context.update(args)

        await self.setup(dataset, context)
        await self.execute(dataset, context)
        await self.teardown(dataset, context)

    async def setup(self, dataset: Optional[Dataset], context: Context) -> Dataset:
        """
        Setup the pipeline and prepare the dataset for processing.

        Args:
            dataset (Optional[Dataset]): An existing dataset to process, if any.
            context (Context): The context to use for processing.

        Returns:
            Dataset: The dataset after setup.
        """
        if self._setup_steps:
            logger.info("Setting up pipeline")
            for action in self._setup_steps:
                # TODO: Add error handling [twl 7.Feb.25]
                await action(dataset, context)

    @abstractmethod
    async def execute(self, dataset: Optional[Dataset], context: Optional[Context]) -> None:
        """
        Execute the data-processing steps of this pipeline.

        Args:
            dataset (Dataset): The dataset to process.
            context (Context): The context to use for processing.
        """
        pass

    async def teardown(self, dataset: Optional[Dataset], context: Optional[Context]) -> None:
        """
        Clean up any resources used by this pipeline and finalize the dataset.

        Args:
            dataset (Optional[Dataset]): The dataset to process.
            context (Optional[Context]): The context to use for processing.
        """
        if self._teardown_steps:
            logger.info("Tearing down pipeline")
            for action in self._teardown_steps:
                # TODO: Add error handling [twl 7.Feb.25]
                await action(dataset, context)
