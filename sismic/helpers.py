from __future__ import annotations

from collections import Counter
from functools import wraps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .interpreter import Interpreter
    from .model import MacroStep

__all__ = ["coverage_from_trace", "log_trace"]


def log_trace(interpreter: Interpreter) -> list[MacroStep]:
    """Return a list that will be populated by each value returned by the *execute_once* method
    of given interpreter.

    :param interpreter: an *Interpreter* instance
    :return: a list of *MacroStep*
    """
    func = interpreter.execute_once
    trace = []

    @wraps(func)
    def new_func() -> MacroStep | None:
        step = func()
        if step:
            trace.append(step)
        return step

    interpreter.execute_once = new_func
    return trace


def coverage_from_trace(trace: list[MacroStep]) -> Mapping[str, Counter]:
    """Given a list of macro steps considered as the trace of a statechart execution.
    return *Counter* objects that counts the states that were entered,
    the states that were exited and the transitions that were processed.

    :param trace: A list of macro steps
    :return: A dict whose keys are "entered states", "exited states" and "processed transitions"
    and whose values are Counter object.
    """
    entered_states = []
    exited_states = []
    processed_transitions = []

    for macrostep in trace:
        for microstep in macrostep.steps:
            entered_states.extend(microstep.entered_states)
            exited_states.extend(microstep.exited_states)
            if microstep.transition:
                processed_transitions.append(microstep.transition)

    return {
        "entered states": Counter(entered_states),
        "exited states": Counter(exited_states),
        "processed transitions": Counter(processed_transitions),
    }
