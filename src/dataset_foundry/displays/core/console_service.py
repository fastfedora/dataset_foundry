from typing import Callable, List, Literal
from ...core.event_emitter import EventEmitter

ConsoleServiceEventType = Literal["line"]


class ConsoleService:
    """
    Service for capturing global logs and allowing subscribers to listen to them.
    """

    def __init__(self):
        self._lines: List[str] = []
        self._events = EventEmitter[ConsoleServiceEventType]()

    @property
    def lines(self) -> List[str]:
        return list(self._lines)

    def append(self, line: str) -> None:
        self._lines.append(line)
        self._emit(line)

    def subscribe(self, callback: Callable[[ConsoleServiceEventType, dict], None]) -> None:
        self._events.on("line", callback)

    def unsubscribe(self, callback: Callable[[ConsoleServiceEventType, dict], None]) -> None:
        self._events.off("line", callback)

    def _emit(self, line: str) -> None:
        self._events.emit("line", {"line": line})

console_service = ConsoleService()
