from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sismic.model import MacroStep, Transition

if TYPE_CHECKING:
    from collections.abc import Mapping

    from sismic.interpreter import Interpreter

MacroSteps = MacroStep | list[MacroStep]


def state_is_entered(steps: MacroSteps, name: str) -> bool:
    """Holds if state was entered during given steps.

    :param steps: a macrostep or list of macrosteps
    :param name: name of a state
    :return: given state was entered
    """
    if isinstance(steps, MacroStep):
        return name in steps.entered_states
    return any(name in step.entered_states for step in steps)


def state_is_exited(steps: MacroSteps, name: str) -> bool:
    """Holds if state was exited during given steps.

    :param steps: a macrostep or list of macrosteps
    :param name: name of a state
    :return: given state was exited
    """
    if isinstance(steps, MacroStep):
        return name in steps.exited_states
    return any(name in step.exited_states for step in steps)


def event_is_fired(
    steps: MacroSteps,
    name: str | None,
    parameters: Mapping[str, Any] | None = None,
) -> bool:
    """Holds if an event was fired during given steps.

    If name is None, this function looks for any event.
    If parameters are provided, their values are compared with the respective
    attribute of the event. Not *all* parameters have to be provided, as only
    the ones that are provided are actually compared.

    :param steps: a macrostep or list of macrosteps
    :param name: name of an event
    :param parameters: additional parameters
    :return: event was fired
    """
    steps = steps if isinstance(steps, list) else [steps]
    parameters = parameters or {}

    for step in steps:
        for event in step.sent_events:
            if name is None or event.name == name:
                matching_parameters = True
                for key, value in parameters.items():
                    if getattr(event, key, None) != value:
                        matching_parameters = False
                        break
                if matching_parameters:
                    return True
    return False


def event_is_consumed(
    steps: MacroSteps,
    name: str | None,
    parameters: Mapping[str, Any] | None = None,
) -> bool:
    """Holds if an event was consumed during given steps.

    If name is None, this function looks for any event.
    If parameters are provided, their values are compared with the respective
    attribute of the event. Not *all* parameters have to be provided, as only
    the ones that are provided are actually compared.

    :param steps: a macrostep or list of macrosteps
    :param name: name of an event
    :param parameters: additional parameters
    :return: event was consumed
    """
    steps = steps if isinstance(steps, list) else [steps]
    parameters = parameters or {}

    for step in steps:
        if step.event is None:
            continue

        if name is None or step.event.name == name:
            matching_parameters = True
            for key, value in parameters.items():
                if getattr(step.event, key, None) != value:
                    matching_parameters = False
                    break
            if matching_parameters:
                return True
    return False


def transition_is_processed(steps: MacroSteps, transition: Transition | None = None) -> bool:
    """Holds if a transition was processed during given steps.

    If no transition is provided, this function looks for any transition.

    :param steps: a macrostep or list of macrosteps
    :param transition: a transition
    :return: transition was processed
    """
    steps = steps if isinstance(steps, list) else [steps]

    if transition is None:
        return any(len(step.transitions) > 0 for step in steps)
    return any(transition in step.transitions for step in steps)


def expression_holds(interpreter: Interpreter, expression: str) -> bool:
    """Holds if given expression holds.

    :param interpreter: current interpreter
    :param expression: expression to evaluate
    :return: expression holds
    """
    return interpreter._evaluator._evaluate_code(expression)
