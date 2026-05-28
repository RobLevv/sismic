from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .evaluator import Evaluator

if TYPE_CHECKING:
    from sismic.interpreter import Interpreter


if TYPE_CHECKING:
    from collections.abc import Mapping

    from sismic.model import Event

__all__ = ["DummyEvaluator"]


class DummyEvaluator(Evaluator):
    """A dummy evaluator that does nothing and evaluates every condition to True."""

    def __init__(
        self,
        interpreter: Interpreter,
        *,
        initial_context: Mapping[str, Any] | None = None,
    ) -> None:
        pass

    @property
    def context(self) -> Mapping[str, Any]:
        return {}

    def _evaluate_code(self, code: str, *, additional_context: Mapping | None = None) -> bool:  # noqa: ARG002
        return True

    def _execute_code(self, code: str, *, additional_context: Mapping | None = None) -> list[Event]:  # noqa: ARG002
        return []
