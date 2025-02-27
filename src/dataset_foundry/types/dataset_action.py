from typing import Callable, TypeAlias

from ..core.dataset import Dataset
from ..core.context import Context

DatasetAction: TypeAlias = Callable[[Dataset, Context], None]
