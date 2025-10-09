from typing import Callable, Dict, List, Optional, Tuple, TypeVar, Generic, Any

EventTypeT = TypeVar("EventTypeT")
EventPayload = Dict[str, Any]
EventCallback = Callable[[EventTypeT, EventPayload], None]
EventPredicate = Optional[Callable[[EventTypeT, EventPayload], bool]]

_SubscriberEntry = Tuple[EventPredicate, EventCallback]
_SubscriberMap = Dict[EventTypeT, List[_SubscriberEntry]]

class EventEmitter(Generic[EventTypeT]):
    """
    Lightweight synchronous event emitter with optional per-subscription predicates.

    - Subscribers register per event type.
    - Each subscriber can optionally provide a predicate that filters payloads.
    - Callbacks are invoked in registration order; exceptions are swallowed to avoid
      breaking the emitter loop.
    """

    def __init__(self) -> None:
        # event_type -> list of (predicate, callback)
        self._subscribers: _SubscriberMap[EventTypeT] = {}

    def on(
        self,
        event_type: EventTypeT,
        callback: EventCallback,
        predicate: EventPredicate = None,
    ) -> None:
        entries = self._subscribers.setdefault(event_type, [])
        entries.append((predicate, callback))

    def off(self, event_type: EventTypeT, callback: EventCallback) -> None:
        entries = self._subscribers.get(event_type, [])
        self._subscribers[event_type] = [pair for pair in entries if pair[1] is not callback]

    def emit(self, event_type: EventTypeT, payload: EventPayload) -> None:
        for predicate, callback in list(self._subscribers.get(event_type, [])):
            try:
                if predicate is None or predicate(event_type, payload):
                    callback(event_type, payload)
            except Exception:
                # Avoid bubbling exceptions from user callbacks
                # to keep the emitter robust.
                pass

