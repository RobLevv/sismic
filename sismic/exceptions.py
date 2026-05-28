from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sismic.interpreter import Interpreter
    from sismic.model import MacroStep, MicroStep, StateMixin


class SismicError(Exception):
    pass


class StatechartError(SismicError):
    """Base error for anything that is related to a statechart."""


class CodeEvaluationError(SismicError):
    """Base error for anything related to the evaluation of the code contained in a statechart."""


class ExecutionError(SismicError):
    """Base error for anything related to the execution of a statechart."""


class ConflictingTransitionsError(ExecutionError):
    """When multiple conflicting (parallel) transitions can be processed at the same time."""


class NonDeterminismError(ExecutionError):
    """In case of non-determinism."""


class PropertyStatechartError(SismicError):
    """Raised when a property statechart reaches a final state.

    :param property_statechart: the property statechart that reaches a final state
    """

    def __init__(self, property_statechart: Interpreter) -> None:
        super().__init__()
        self._property = property_statechart

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}\nProperty is not satisfied,"
            f" {self._property} has reached a final state"
        )


class ContractError(SismicError):
    """Base exception for situations in which a contract is not satisfied.
    All the parameters are optional, and are exposed to ease debug.

    :param configuration: list of active states
    :param step: a *MicroStep* or *MacroStep* instance.
    :param obj: the object that is concerned by the assertion
    :param assertion: the assertion that failed
    :param context: the context in which the condition failed
    """

    __slots__ = ["_assertion", "_configuration", "_context", "_obj", "_step"]

    def __init__(
        self,
        configuration: list[StateMixin] | None = None,
        step: MicroStep | MacroStep | None = None,
        obj: object = None,
        assertion: object = None,
        context: dict[object, object] | None = None,
    ) -> None:
        super().__init__(self)
        self._configuration = configuration
        self._step = step
        self._obj = obj
        self._assertion = assertion
        self._context = context

    @property
    def configuration(self) -> list[StateMixin] | None:
        return self._configuration

    @property
    def step(self) -> MicroStep | MacroStep | None:
        return self._step

    @property
    def obj(self) -> object:
        return self._obj

    @property
    def condition(self) -> object:
        return self._assertion

    @property
    def context(self) -> object:
        return self._context

    def __str__(self) -> str:
        message = [f"{self.__class__.__name__}"]
        if self._obj:
            message.append(f"Object: {self._obj}")
        if self._assertion:
            message.append(f"Assertion: {self._assertion}")
        if self._configuration:
            message.append(f"Configuration: {self._configuration}")
        if self._step:
            message.append(f"Step: {self._step}")
        if self._context:
            message.append("Context:")
            for key, value in sorted(self._context.items(), key=lambda t: t[0]):
                message.append(f" - {key} = {value}")

        return "\n".join(message)


class PreconditionError(ContractError):
    """A precondition is not satisfied."""


class PostconditionError(ContractError):
    """A postcondition is not satisfied."""


class InvariantError(ContractError):
    """An invariant is not satisfied."""
