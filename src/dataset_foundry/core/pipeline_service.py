import logging
import time
import uuid
from contextvars import Token
from typing import Any, Callable, Dict, List, Literal, Optional, TYPE_CHECKING

from ..types.pipeline_execution_info import PipelineExecutionId, PipelineExecutionInfo
from ..types.dataset_item_execution_info import DatasetItemExecutionInfo, DatasetItemExecutionStatus
from .dataset_item import DatasetItem
from .event_emitter import EventEmitter
from .execution_context import current_pipeline_execution_id, current_item_id

if TYPE_CHECKING:
    from .pipeline import Pipeline
    from .dataset import Dataset
    from .context import Context

PipelineServiceEventType = Literal[
    "item_added",
    "item_removed",
    "item_updated",
    "pipeline_started",
    "pipeline_ended",
]


class PipelineService:
    """
    Tracks running pipelines and their items, sending events when they start and stop.
    """

    def __init__(self):
        """
        Initialize the pipeline service.
        """
        self._log = logging.getLogger(__name__)
        self._pipelines: Dict[PipelineExecutionId, PipelineExecutionInfo] = {}
        self._items: Dict[PipelineExecutionId, Dict[str, DatasetItemExecutionInfo]] = {}
        self._events = EventEmitter[PipelineServiceEventType]()

    @property
    def pipelines(self) -> List[PipelineExecutionInfo]:
        """Get all pipelines registered with the service."""
        return list(self._pipelines.values())

    @property
    def items(self) -> List[DatasetItemExecutionInfo]:
        """Get all items across all pipeline executions."""
        # Flatten in insertion order of executions and then items within
        flat: List[DatasetItemExecutionInfo] = []
        for exec_items in self._items.values():
            for info in exec_items.values():
                flat.append(info)
        return flat

    def start_pipeline(self, pipeline: 'Pipeline', dataset: 'Dataset', context: 'Context') -> Token:
        """
        Start a new pipeline execution.

        Args:
            pipeline: The pipeline to start.
            dataset: The dataset to process.
            context: The context to use for processing.

        Returns:
            Token: The token used to track the pipeline execution.
        """
        execution_id = str(uuid.uuid4())
        execution_token = current_pipeline_execution_id.set(execution_id)
        self._pipelines[execution_id] = PipelineExecutionInfo(
            execution_id=execution_id,
            execution_token=execution_token,
            pipeline=pipeline,
            dataset=dataset,
            context=context,
            start_time=time.time(),
        )

        for item in dataset.items:
            self._add_item_info(execution_id, item)

        self._emit("pipeline_started", { "execution_id": execution_id })

        return execution_token

    def stop_pipeline(self, execution_token: Token) -> None:
        """
        Stop a pipeline execution.

        Args:
            execution_token: The token used to track the pipeline execution.

        Raises:
            ValueError: If `execution_token` doesn't belong to an active pipeline execution.
        """
        execution_id = current_pipeline_execution_id.get()
        current_pipeline_execution_id.reset(execution_token)

        info = self._pipelines.get(execution_id)
        if info:
            if info.execution_token != execution_token:
                raise ValueError("The `execution_token` param must be for an active pipeline")

            info.execution_token = None
            info.end_time = time.time()
            self._emit("pipeline_ended", { "execution_id": execution_id })

    def start_item(self, item: DatasetItem) -> DatasetItemExecutionInfo:
        """
        Start tracking an item for the active pipeline execution.

        Args:
            item: The item to track.

        Returns:
            DatasetItemExecutionInfo: The info for the item.

        Raises:
            ValueError: If `item` is not actively tracked or no active pipeline execution exists.
        """
        if not item.id:
            raise ValueError("`item` must have an id to be tracked by PipelineService")

        execution_id = current_pipeline_execution_id.get()
        if not execution_id:
            raise ValueError("No pipeline execution is currently active")

        info = self._get_item_info(execution_id, item)
        if not info:
            info = self._add_item_info(execution_id, item)

        info.status = "running"
        info.start_time = info.start_time or time.time()
        info.execution_token = current_item_id.set(item.id)

        self._emit("item_updated", {
            "item": info,
            "fields": ["status", "start_time", "execution_token"]
        })

        return info

    def stop_item(self, info: DatasetItemExecutionInfo, status: DatasetItemExecutionStatus) -> None:
        """
        Stop tracking an item.

        Args:
            info: The info for the item.
            status: The status of the item.

        Raises:
            ValueError: If `item` is not actively tracked.
        """
        if not info.execution_token:
            raise ValueError("`item` must be an actively tracked item")

        info.status = status
        info.end_time = time.time()

        current_item_id.reset(info.execution_token)
        info.execution_token = None

        self._emit("item_updated", {
            "item": info,
            "fields": ["status", "end_time", "execution_token"]
        })

    def update_item(self, item_id: str, values: Dict[str, Any]) -> None:
        """
        Update the info for an item.

        Args:
            item_id: The id of the item.
            values: The values to update.

        Raises:
            ValueError: If the item is not actively tracked.
        """
        info = self._find_info_by_id(item_id)
        if not info:
            raise ValueError(f"Item with ID {item_id} not found")

        changed_fields: List[str] = []
        for key, value in values.items():
            if hasattr(info, key):
                setattr(info, key, value)
                changed_fields.append(key)
            else:
                info.metadata[key] = value
                changed_fields.append(f"metadata.{key}")

        if changed_fields:
            self._emit("item_updated", { "item": info, "fields": changed_fields })

    def append_to_item_property(self, item_id: str, property: str, value: Any) -> None:
        """
        Append a value to a specific property in the info for an item.

        Args:
            item_id: The id of the item.
            property: The property to append to.
            value: The value to append.

        Raises:
            ValueError: If the item is not actively tracked.
        """
        info = self._find_info_by_id(item_id)
        if not info:
            raise ValueError(f"Item with ID {item_id} not found")

        self.update_item(item_id, { property: getattr(info, property, []) + [value] })

    def subscribe(
        self,
        event_type: PipelineServiceEventType,
        filter: Dict[str, Any],
        callback: Callable[[PipelineServiceEventType, Dict[str, Any]], None]
    ) -> None:
        """
        Subscribe to pipeline service events.

        Args:
            event_type: The type of event to subscribe to.
            filter: The filter to apply to the event, if applicable for the event type.
            callback: The callback to invoke when the event occurs.
        """
        def predicate(_event_type: PipelineServiceEventType, payload: Dict[str, Any]) -> bool:
            return self._matches(_event_type, filter or {}, payload)
        self._events.on(event_type, callback, predicate)

    def unsubscribe(
        self,
        event_type: PipelineServiceEventType,
        callback: Callable[[PipelineServiceEventType, Dict[str, Any]], None]
    ) -> None:
        """
        Unsubscribe from pipeline service events.

        Args:
            event_type: The type of event to unsubscribe from.
            callback: The callback to unsubscribe.
        """
        self._events.off(event_type, callback)

    def _find_info_by_id(self, item_id: str) -> DatasetItemExecutionInfo | None:
        """
        Find the first matching DatasetItemExecutionInfo by item_id across all executions.

        Args:
            item_id: The id of the item.

        Returns a tuple of (execution_id, info) or None if not found.
        Preserves insertion order by iterating execution dicts in insertion order
        and items dicts in their insertion order.
        """
        for _execution_id, items in self._items.items():
            if item_id in items:
                return items[item_id]
        return None

    def _get_item_info(
        self,
        execution_id: PipelineExecutionId,
        item: DatasetItem
    ) -> Optional[DatasetItemExecutionInfo]:
        return self._items.get(execution_id, {}).get(item.id)

    def _add_item_info(
        self,
        execution_id: PipelineExecutionId,
        item: DatasetItem
    ) -> DatasetItemExecutionInfo:
        items = self._items.setdefault(execution_id, {})
        info = DatasetItemExecutionInfo(id=item.id, pipeline_execution_id=execution_id, item=item)

        items[item.id] = info
        self._emit("item_added", { "item": info })

        return info

    def _emit(self, event_type: PipelineServiceEventType, payload: Dict[str, Any]) -> None:
        self._events.emit(event_type, payload)

    def _matches(
        self,
        event_type: PipelineServiceEventType,
        filter: Dict[str, Any],
        payload: Dict[str, Any]
    ) -> bool:
        if not filter:
            return True

        if event_type in ("item_added", "item_updated", "item_removed"):
            info: DatasetItemExecutionInfo = payload.get("item")

            item_id = filter.get("item_id")
            if item_id and item_id != info.id:
                return False

            fields = filter.get("fields")
            changed = set(payload.get("fields", []))
            if fields and not (set(fields) & changed):
                return False

        # No filters for pipeline events currently
        return True

pipeline_service = PipelineService()
