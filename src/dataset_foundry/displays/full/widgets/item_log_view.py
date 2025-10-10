from textual.widgets import ListItem, Label
from textual.reactive import reactive

from ....core.pipeline_service import pipeline_service
from ....types.dataset_item_execution_info import DatasetItemExecutionInfo
from ....utils.collections import find_first
from ..safe_ui.list_view import SafeUiListView


class ItemLogView(SafeUiListView):
    item_id: reactive[str | None] = reactive(None)

    DEFAULT_CSS = """
    ItemLogView {
        width: 100%;
        height: 100%;
    }
    ItemLogView .log-line {
        width: 100%;
        text-wrap: wrap;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._lines: list[str] = []
        self._last_len: int = 0
        self._on_item_updated_subscribed: bool = False

    def watch_item_id(self, _old_id: str | None, new_id: str | None):
        if self._on_item_updated_subscribed:
            pipeline_service.unsubscribe("item_updated", self._on_item_updated)
            self._on_item_updated_subscribed = False

        # Reset state
        self._lines = []
        self._last_len = 0
        self.clear()

        if not new_id:
            return

        # Seed with existing lines
        info = find_first(pipeline_service.items, lambda item: item.id == new_id)
        if info and info.logs:
            self._lines = list(info.logs)
            self._last_len = len(self._lines)
            for line in self._lines:
                self._add_line(line)

        self._on_item_updated_subscribed = True
        pipeline_service.subscribe(
            "item_updated",
            {
                "item_id": new_id,
                "fields": ["logs"]
            },
            self._on_item_updated
        )

    def _on_item_updated(self, _event_type, payload) -> None:
        info: DatasetItemExecutionInfo = payload.get("item")
        if not info or info.id != self.item_id:
            return

        new_logs = list(info.logs)
        # Append only the delta to avoid re-rendering entire buffer
        if self._last_len <= len(new_logs):
            delta = new_logs[self._last_len :]
        else:
            # Logs were truncated/reset; rebuild
            self._lines = []
            self._last_len = 0
            delta = new_logs

        if not delta:
            return

        self._lines.extend(delta)
        self._last_len = len(self._lines)
        for line in delta:
            self._add_line(line)

    def _add_line(self, line: str):
        self.append_safe(ListItem(Label(line, classes="log-line", markup=False)))
