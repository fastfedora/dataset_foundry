from contextvars import ContextVar


current_pipeline_execution_id: ContextVar[str] = ContextVar("pipeline_execution_id")
current_item_id: ContextVar[str] = ContextVar("item_id")
