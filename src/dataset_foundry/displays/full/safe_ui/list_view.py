from textual.widgets import ListView, ListItem

from .mixin import SafeUiMixin


class SafeUiListView(SafeUiMixin, ListView):
    """ListView that provides a safe append API for cross-task updates."""

    def append_safe(self, item: ListItem) -> None:
        self.safe_ui_call(lambda: super(SafeUiListView, self).append(item))
