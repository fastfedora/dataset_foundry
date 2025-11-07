import logging

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import ListView, Tab, Tabs

from ...core.pipeline_service import pipeline_service
from ...displays.core.console_service import console_service
from .widgets.console_log_view import ConsoleLogView
from .widgets.item_log_view import ItemLogView
from .widgets.item_tabs import ItemTabs

logger = logging.getLogger(__name__)


class FullDisplayApp(App):
    CSS = """
    Screen { layout: vertical; }

    #pane_pipeline { layout: horizontal; }
    #pane_console { layout: horizontal; }

    #item_tabs {
        width: 20%;
        min-width: 20%;
        max-width: 20%;
        height: 100%;
    }
    #item_tabs ListItem { width: 100%; }
    #item_tabs Label { width: 100%; text-wrap: wrap; }

    ItemLogView { width: 80%; }
    """

    def __init__(self):
        super().__init__()
        self.app.begin_capture_print(self, stdout=True, stderr=True)
        self.log_view = ItemLogView()
        self.console_view = ConsoleLogView()

    def on_print(self, event: events.Print) -> None:
        console_service.append(str(event.text))

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Tabs(
                Tab("Pipeline", id="tab_pipeline"),
                Tab("Console", id="tab_console"),
                id="top_tabs"
            )
            with Horizontal(id="pane_pipeline"):
                yield ItemTabs(id="item_tabs")
                yield self.log_view
            with Horizontal(id="pane_console"):
                yield self.console_view

    def on_mount(self) -> None:
        if len(pipeline_service.pipelines) > 0:
            self._select_tab('tab_pipeline')
        else:
            self._select_tab('tab_console')
            # Hide pipeline tab until a pipeline starts
            self.query_one('#tab_pipeline').display = False

        pipeline_service.subscribe("pipeline_started", {}, self._on_pipeline_started)

    def on_list_view_selected(self, event: ListView.Selected):
        # Only handle selections from the item tabs list
        source_list = event.list_view
        if getattr(source_list, 'id', None) != 'item_tabs':
            return

        # Use the ListItem's name to store the item_id
        item_id = event.item.name
        self.log_view.item_id = item_id

    def _on_pipeline_started(self, _event_type, _payload):
        """Show Pipeline tab when a pipeline starts"""
        self._select_tab('tab_pipeline')

    def on_tabs_tab_activated(self, event: Tabs.TabActivated):
        # HACK: The `TabActivated` event appears to be being send when tabs are added into the DOM
        #       even if they are not actually active. Checking the `-active` class ensures we only
        #       switch to the tab if it is actually active. [fastfedora 10.Oct.25]
        if "-active" in event.tab.classes:
            self._switch_tab(event.tab.id)

    def _select_tab(self, tab_id: str) -> None:
        top_tabs = self.query_one('#top_tabs')
        top_tabs.active = tab_id
        self._switch_tab(tab_id)

    def _switch_tab(self, tab_id: str) -> None:
        pipeline_pane = self.query_one('#pane_pipeline')
        console_pane = self.query_one('#pane_console')

        if tab_id == 'tab_pipeline':
            # Ensure the Pipeline tab itself is visible when selected, since it starts hidden
            pipeline_tab = self.query_one('#tab_pipeline')
            pipeline_tab.display = True

            # Switch to the pipeline tab pane
            pipeline_pane.display = True
            console_pane.display = False
        elif tab_id == 'tab_console':
            pipeline_pane.display = False
            console_pane.display = True
