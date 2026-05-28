from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sismic.exceptions import PropertyStatechartError
from sismic.model import Event, MetaEvent

if TYPE_CHECKING:
    from collections.abc import Callable

    from sismic.interpreter import Interpreter

__all__ = ["InternalEventListener", "PropertyStatechartListener"]


class InternalEventListener:
    """Listener that filters and propagates internal events as external events."""

    def __init__(self, func: Callable[[Event], Any]) -> None:
        self._callable = func

    def __call__(self, event: MetaEvent) -> None:
        if event.name == "event sent" and isinstance(event.event, Event):
            self._callable(Event(event.event.name, **event.event.data))


class PropertyStatechartListener:
    """Listener that propagates meta-events to given property statechart, executes
    the property statechart, and checks it.
    """

    def __init__(self, interpreter: Interpreter) -> None:
        self._interpreter = interpreter

    def __call__(self, event: MetaEvent) -> None:
        self._interpreter.queue(event)
        self._interpreter.execute()
        if self._interpreter.final:
            raise PropertyStatechartError(self._interpreter)
