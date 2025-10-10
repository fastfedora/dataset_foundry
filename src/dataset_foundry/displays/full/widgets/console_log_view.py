from textual.widgets import ListItem, Label

from ....displays.core.console_service import console_service
from ..safe_ui.list_view import SafeUiListView


class ConsoleLogView(SafeUiListView):
    """Scrollable console output subscribing to ConsoleService."""

    def on_mount(self):
        # Seed with existing lines
        for line in console_service.lines:
            self._add_line(line)

        console_service.subscribe(self._on_line)

    def on_unmount(self):
        console_service.unsubscribe(self._on_line)

    def _on_line(self, _event_type: str, payload: dict):
        line = payload.get("line", "")
        self._add_line(line)

    def _add_line(self, line: str):
        self.append_safe(ListItem(Label(str(line), markup=False)))
