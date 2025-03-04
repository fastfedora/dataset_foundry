from typing import Callable, TypeAlias

from ..core.dataset import Dataset

DatasetAction: TypeAlias = Callable[[Dataset, 'Context'], None] # type: ignore - circular import
