from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal
from contextvars import Token

from ..core.dataset_item import DatasetItem
from .pipeline_execution_info import PipelineExecutionId

DatasetItemExecutionStatus = Literal["created", "running", "success", "failure", "error"]


@dataclass
class DatasetItemExecutionInfo:
    id: str
    pipeline_execution_id: PipelineExecutionId
    item: DatasetItem
    status: DatasetItemExecutionStatus = "created"
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: float | None = None
    end_time: float | None = None
    execution_token: Token | None = None
    logs: List[str] = field(default_factory=list)
