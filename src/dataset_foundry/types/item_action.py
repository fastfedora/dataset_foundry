from typing import Callable, TypeAlias

from ..core.dataset_item import DatasetItem
from ..core.context import Context

ItemAction: TypeAlias = Callable[[DatasetItem, Context], None]
