import logging

from textual.widgets import ListView

from ....core.pipeline_service import pipeline_service
from ....types.dataset_item_execution_info import DatasetItemExecutionInfo

from .item_tab import ItemTab


logger = logging.getLogger(__name__)


class ItemTabs(ListView):
    def on_mount(self):
        for info in pipeline_service.items:
            self._add_tab(info)

        pipeline_service.subscribe("item_added", {}, self._on_item_added)
        pipeline_service.subscribe("item_updated", {"fields": ["status"]}, self._on_item_updated)

        self._maybe_select_first_tab()

    def _on_item_added(self, _event_type, payload):
        info: DatasetItemExecutionInfo = payload.get("item")
        if info:
            self._add_tab(info)
            self._maybe_select_first_tab()

    def _on_item_updated(self, _event_type, payload):
        info: DatasetItemExecutionInfo = payload.get("item")
        if info:
            tab: ItemTab = self.query_one(f"#item_{info.id}")
            tab.update_from_info(info)

    def _add_tab(self, info: DatasetItemExecutionInfo):
        tab = ItemTab(info, id=f"item_{info.id}")
        self.append(tab)

    def _maybe_select_first_tab(self):
        """Select first tab if no other tab is selected and one is available"""
        if self.index is None and len(self.children) > 0:
            self.index = 0
            self.action_select_cursor()
