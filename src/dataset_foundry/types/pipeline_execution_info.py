from contextvars import Token
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.pipeline import Pipeline
    from ..core.dataset import Dataset
    from ..core.context import Context

type PipelineExecutionId = str


@dataclass
class PipelineExecutionInfo:
    execution_id: PipelineExecutionId
    execution_token: Token
    pipeline: 'Pipeline'
    dataset: 'Dataset'
    context: 'Context'
    start_time: float
    end_time: float | None = None
