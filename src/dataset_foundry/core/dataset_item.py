from typing import Callable, List, Union

class DataHistoryRecord:
    step: str
    data: dict

class DatasetItem:
    """
    A single item in a dataset.
    """
    _id: str = None
    _data_history: List[DataHistoryRecord] = []

    # TODO: Think about converting this to a @property [fastfedora 11.Feb.25]
    data: dict = {}

    def __init__(self, id: str = None, data: dict = None):
        self._id = id
        self.data = data if data else {}

    @property
    def id(self) -> str:
        return self._id

    def push(self, data: dict, step: Union[Callable, str]):
        step_name = step.__name__ if callable(step) else (step or f"{len(self._data_history) + 1}")
        self._data_history.append({
            "step": step_name,
            "data": data
        })
        self.data.update(data)

    def merge(self, item: "DatasetItem", step: Union[Callable, str] = "merge"):
        self.push(item.data, step)
