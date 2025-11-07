from textual.widgets import ListItem, Label
from textual.app import ComposeResult

from ....types.dataset_item_execution_info import DatasetItemExecutionInfo


STATUS_EMOJI = {
    "created": "◾",
    "running": "⏳",
    "success": "✅",
    "failure": "❌",
    "error": "💥",
}

class ItemTab(ListItem):
    """A tab representing an item with a status emoji and a label."""

    DEFAULT_CSS = """
    ItemTab {
        layout: horizontal;
        padding-right: 1;
    }
    ItemTab .title {
        text-wrap: wrap;
    }
    """

    def __init__(self, info: DatasetItemExecutionInfo, **kwargs):
        text = str(info.id) if info.id is not None else "_"
        super().__init__(name=text, **kwargs)
        self._info = info
        self._label_id = f"label_{text}"

    def compose(self) -> ComposeResult:
        yield Label(self._get_label_text(self._info), id=self._label_id, classes="title")

    def update_from_info(self, info: DatasetItemExecutionInfo) -> None:
        self._info = info
        label: Label = self.query_one(f"#{self._label_id}")
        label.update(self._get_label_text(info))
        self.refresh()

    def _get_label_text(self, info: DatasetItemExecutionInfo) -> str:
        data = info.item.data
        status = data.get("display_status") or info.status
        emoji = data.get("display_emoji") or STATUS_EMOJI.get(status, STATUS_EMOJI["created"])
        return f"{emoji}\N{NO-BREAK SPACE}{info.id}"

# -------------------------------------------------------------------------------------------------
# HACK: Workaround for Textual converting non-breaking spaces to spaces [fastfedora 30.Sep.25]
# -------------------------------------------------------------------------------------------------
import re
from rich.text import Text

_re_whitespace = re.compile("[^\\S\N{NO-BREAK SPACE}]+$")

def monkeypatch_rich_word_wrapping_bug() -> None:
    # Workaround for https://github.com/Textualize/rich/issues/3545
    import rich._wrap
    import rich.text
    rich._wrap.re_word = re.compile("\\s*[\\S\N{NO-BREAK SPACE}]+\\s*")
    rich.text._re_whitespace = _re_whitespace

    def rstrip(self: Text) -> None:
        self.plain = _re_whitespace.sub('', self.plain)
    Text.rstrip = rstrip  # type: ignore[method-assign]

monkeypatch_rich_word_wrapping_bug()
# -------------------------------------------------------------------------------------------------
