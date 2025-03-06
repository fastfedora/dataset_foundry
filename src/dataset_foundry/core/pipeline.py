from abc import ABC, abstractmethod
import logging
from pathlib import Path
from typing import List, Optional, TypeAlias

from ..types.dataset_action import DatasetAction
from .config import Config
from .dataset import Dataset

logger = logging.getLogger(__name__)

PipelineAction: TypeAlias = DatasetAction | 'Pipeline'

class Pipeline(ABC):
    """
    A pipeline that can be used to process data.
    """
    _setup_steps: Optional[List[PipelineAction]] = None
    _teardown_steps: Optional[List[PipelineAction]] = None

    name: Optional[str] = None
    """
    The name of the pipeline.
    """

    metadata: dict = {}
    """
    Metadata about the pipeline.
    """

    config: Config
    """
    The configuration used by the pipeline.
    """

    def __init__(
            self,
            name: Optional[str] = None,
            config: Optional[Path|str|dict] = {},
            metadata: Optional[dict] = {},
            setup: Optional[List[PipelineAction]] = None,
            teardown: Optional[List[PipelineAction]] = None
        ):
        """
        Initialize the pipeline.

        Args:
            name (Optional[str]): The name of the pipeline.
            config (Path|str|dict): The configuration, or path to a config file, for the pipeline.
            metadata (dict): Metadata about the pipeline.
            setup (Optional[List[PipelineAction]]): The setup steps to run before processing.
            teardown (Optional[List[PipelineAction]]): The teardown steps to run after processing.
        """
        self.name = name
        self.config = Config(config)
        self.metadata = metadata
        self._setup_steps = setup
        self._teardown_steps = teardown

    async def _do_steps(
            self,
            steps: List[PipelineAction],
            dataset: Dataset,
            context: 'Context', # type: ignore - avoid circular import
        ) -> Dataset:
        for step in steps:
            # TODO: Consider removing this in favor of `run_pipeline` [fastfedora 27.Feb.25]
            if isinstance(step, Pipeline):
                dataset = await step.run(dataset, context)
            else:
                try:
                    await step(dataset, context)
                except Exception as e:
                    logger.error(f"Error during pipeline {self.name} in step {step.__name__}: {e}")
                    raise e

        return dataset

    async def run(
            self,
            dataset: Optional[Dataset] = None,
            context: Optional['Context'] = None, # type: ignore - avoid circular import
            params: Optional[dict] = None,
        ) -> Dataset:
        """
        Run the pipeline.

        Args:
            dataset (Optional[Dataset]): The dataset to process.
            context (Optional[Context]): The parent context, if running within another pipeline.
            params (Optional[dict]): The parameters to pass to the pipeline.
        """
        from .context import Context # avoid circular import

        dataset = dataset if dataset else Dataset()
        context = context.create_child(self, dataset, params) if context \
            else Context(self, dataset, params)

        if self.name:
            logger.info(f"Running pipeline: {self.name}")

        await self.setup(dataset, context)
        await self.execute(dataset, context)
        await self.teardown(dataset, context)

        return dataset

    async def setup(
            self,
            dataset: Optional[Dataset],
            context: 'Context', # type: ignore - avoid circular import
        ) -> Dataset:
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
            await self._do_steps(self._setup_steps, dataset, context)

    @abstractmethod
    async def execute(
            self,
            dataset: Optional[Dataset],
            context: Optional['Context'], # type: ignore - avoid circular import
        ) -> None:
        """
        Execute the data-processing steps of this pipeline.

        Args:
            dataset (Dataset): The dataset to process.
            context (Context): The context to use for processing.
        """
        pass

    async def teardown(
            self,
            dataset: Optional[Dataset],
            context: Optional['Context'], # type: ignore - avoid circular import
        ) -> None:
        """
        Clean up any resources used by this pipeline and finalize the dataset.

        Args:
            dataset (Optional[Dataset]): The dataset to process.
            context (Optional[Context]): The context to use for processing.
        """
        if self._teardown_steps:
            logger.info("Tearing down pipeline")
            await self._do_steps(self._teardown_steps, dataset, context)
