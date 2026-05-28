from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from behave import given, then, when
from behave.__main__ import run_behave
from behave.configuration import Configuration

from sismic.interpreter import Interpreter

if TYPE_CHECKING:
    from collections.abc import Callable

    from behave.runner import Context

    from sismic.model import Statechart

__all__ = ["execute_bdd", "map_action", "map_assertion"]


def map_action(step_text: str, existing_step_or_steps: str | list[str]) -> None:
    """Map new "given"/"when" steps to one or many existing one(s).
    Parameters are propagated to the original step(s) as well, as expected.

    Examples:
     - map_action('I open door', 'I send event open_door')
     - map_action('Event {name} has to be sent', 'I send event {name}')
     - map_action('I do two things', ['First thing to do', 'Second thing to do'])

    :param step_text: Text of the new step, without the "given" or "when" keyword.
    :param existing_step_or_steps: existing step, without the "given" or "when" keyword.
        Could be a list of steps.

    """
    if not isinstance(existing_step_or_steps, str):
        existing_step_or_steps = "\nand ".join(existing_step_or_steps)

    @given(step_text)
    def _(context: Context, **kwargs: object) -> None:
        context.execute_steps("Given " + existing_step_or_steps.format(**kwargs))

    @when(step_text)
    def _(context: Context, **kwargs: object) -> None:
        context.execute_steps("When " + existing_step_or_steps.format(**kwargs))


def map_assertion(step_text: str, existing_step_or_steps: str | list[str]) -> None:
    """Map a new "then" step to one or many existing one(s).
    Parameters are propagated to the original step(s) as well, as expected.

    map_assertion('door is open', 'state door open is active')
    map_assertion('{x} seconds elapsed', 'I wait for {x} seconds')
    map_assertion('assert two things', ['first thing to assert', 'second thing to assert'])

    :param step_text: Text of the new step, without the "then" keyword.
    :param existing_step_or_steps: existing step, without "then" keyword. Could be a list of steps.
    """
    if not isinstance(existing_step_or_steps, str):
        existing_step_or_steps = "\nand ".join(existing_step_or_steps)

    @then(step_text)
    def _(context: Context, **kwargs: object) -> None:
        context.execute_steps("Then " + existing_step_or_steps.format(**kwargs))


def execute_bdd(
    statechart: Statechart,
    feature_filepaths: list[Path],
    *,
    step_filepaths: list[Path] | None = None,
    property_statecharts: list[Statechart] | None = None,
    interpreter_klass: Callable[[Statechart], Interpreter] = Interpreter,
    debug_on_error: bool = False,
    behave_parameters: list[str] | None = None,
) -> int:
    """Execute BDD tests for a statechart.

    :param statechart: statechart to test
    :param feature_filepaths: list of filepaths to feature files.
    :param step_filepaths: list of filepaths to step definitions.
    :param property_statecharts: list of property statecharts
    :param interpreter_klass: a callable that accepts a statechart and an optional clock
        and returns an Interpreter
    :param debug_on_error: set to True to drop to (i)pdb in case of error.
    :param behave_parameters: additional CLI parameters used by Behave
        (see http://behave.readthedocs.io/en/latest/behave.html#command-line-arguments)
    :return: exit code of behave CLI.
    """
    # Default values
    step_filepaths = step_filepaths or []
    property_statecharts = property_statecharts or []
    behave_parameters = behave_parameters or []

    # If debug_on_error, disable captured stdout, otherwise it hangs
    if debug_on_error and "--capture" not in behave_parameters:
        behave_parameters.append("--no-capture")

    # Create temporary directory to put everything inside
    with tempfile.TemporaryDirectory() as tempdir:
        # Create configuration for Behave
        config = Configuration(behave_parameters)

        # Paths to features
        config.paths = [f"{f}" for f in feature_filepaths]

        environment_path = Path(tempdir) / "environment.py"
        step_dir = Path(tempdir) / "steps"

        # Copy environment
        with environment_path.open("w") as environment:
            environment.write("from sismic.bdd.environment import *")

        # Path to environment
        config.environment_file = str(environment_path)

        # Add predefined steps
        step_dir.mkdir(parents=True, exist_ok=True)
        with (step_dir / "__steps.py").open("w") as step:
            step.write("from sismic.bdd.steps import *")

        # Copy provided steps, if any
        for step_filepath in step_filepaths:
            shutil.copy(
                step_filepath,
                step_dir / os.path.split(step_filepath)[-1],
            )

        # Path to steps
        config.steps_dir = str(step_dir)

        # Put statechart and properties in user data
        config.update_userdata(
            {
                "statechart": statechart,
                "interpreter_klass": interpreter_klass,
                "property_statecharts": property_statecharts,
                "debug_on_error": debug_on_error,
            },
        )

        # Run behave
        return run_behave(config)
