from typing import List, Optional
from .dataset_item import DatasetItem

class Dataset:
    """
    A collection of data items.
    """
    _items_by_id: dict[str, DatasetItem] = {}

    metadata: dict
    items: List[DatasetItem]

    def __init__(self, items: List[DatasetItem] = None, metadata: Optional[dict] = None):
        self.metadata = metadata if metadata else {}
        self.items = items if items else []

    def add(self, item: DatasetItem, merge: bool = False):
        merged = False

        from pprint import pformat
        if item.id:
            if item.id in self._items_by_id:
                if merge:
                    self._items_by_id[item.id].merge(item)
                    merged = True
                else:
                    raise ValueError(f"An item with the ID {item.id} already exists.")
            else:
                self._items_by_id[item.id] = item

        if not merged:
            self.items.append(item)
