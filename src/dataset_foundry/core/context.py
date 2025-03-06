from typing import Optional

from .config import Config
from .pipeline import Pipeline
from .dataset import Dataset

class Context:
    """
    A context object that can be used to store and retrieve data.
    """

    _pipeline: Pipeline
    _params: dict
    _dataset: Dataset
    _parent: Optional['Context'] = None

    @property
    def pipeline(self) -> Pipeline:
        """
        The pipeline this context is for.
        """
        return self._pipeline

    @property
    def config(self) -> Config:
        """
        The configuration for the pipeline.
        """
        return self.pipeline.config

    @property
    def params(self) -> dict:
        """
        The parameters that were passed to the pipeline.
        """
        return self._params

    @property
    def dataset(self) -> Dataset:
        """
        The dataset that is being processed by the pipeline.
        """
        return self._dataset

    @property
    def parent(self) -> 'Context':
        """
        The parent context of this context.
        """
        return self._parent

    def __init__(self, pipeline: Pipeline, dataset: Dataset, params: Optional[dict] = None):
        """
        Initialize the context.

        Args:
            pipeline (Pipeline): The pipeline this is the context for.
            dataset (Dataset): The dataset that being processed by the pipeline.
            params (dict): The parameters that were passed to the pipeline.
        """
        self._pipeline = pipeline
        self._params = params or {}
        self._dataset = dataset

        # TODO: Scan `params` and `config` for any keys that match the attributes of this object,
        #       (pipeline, config, params, dataset) and log a warning. [fastfedora 4.Mar.25]

    def __getitem__(self, key: str):
        """
        Get the value from the context associated with `key`. For this object, keys and attributes
        are equivalent.

        If `key` is `pipeline`, `config`, `params` or `dataset`, returns the corresponding property
        of this context; otherwise, returns a value by searching the `params` and then the `config`
        for the given `key`.

        Args:
            key (str): The key to retrieve from the context.

        Returns:
            Any: The value associated with the given `key`.
        """
        if key in ["pipeline", "config", "params", "dataset"]:
            return getattr(self, key)
        elif key in self.params:
            return self.params[key]
        elif key in self.config:
            return self.config[key]
        else:
            raise KeyError(f"Key {key} not found in context")

    def __getattr__(self, key: str):
        """
        Get the value from the context associated with `key`. For this object, keys and attributes
        are equivalent.

        If `key` is `pipeline`, `config`, `params` or `dataset`, returns the corresponding property
        of this context; otherwise, returns a value by searching the `params` and then the `config`
        for the given `key`.

        Args:
            key (str): The key to retrieve from the context.

        Returns:
            Any: The value associated with the given `key`.
        """
        return self[key]

    def __contains__(self, key: str) -> bool:
        """
        Check if the context contains a key.

        Args:
            key (str): The key to check for in the context.

        Returns:
            bool: True if the key is in the context, False otherwise.
        """
        return key in ["pipeline", "config", "params", "dataset"] or \
            key in self.params or key in self.config

    def create_child(
            self,
            pipeline: Optional[Pipeline] = None,
            dataset: Optional[Dataset] = None,
            params: Optional[dict] = None,
            merge_params: bool = True,
        ) -> 'Context':
        """
        Create a child context that inherits from this context.

        Args:
            pipeline (Optional[Pipeline]): The pipeline to use for the child context.
            dataset (Optional[Dataset]): The dataset to use for the child context.
            params (Optional[dict]): The parameters to use for the child context.
            merge_params (bool): Whether to merge the parameters of the parent context with
                `params`, with keys in `params` taking precedence. Defaults to `True`.
        """
        if merge_params:
            params = {**self.params, **(params or {})}

        context = Context(pipeline or self.pipeline, dataset or self.dataset, params)
        context._parent = self

        return context
