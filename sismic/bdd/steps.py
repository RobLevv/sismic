from __future__ import annotations

from ast import AST, literal_eval
from typing import TYPE_CHECKING, cast

from behave import given, then, when

from sismic import testing

if TYPE_CHECKING:
    from behave.model import Feature
    from behave.runner import Context


@given("I do nothing")
@when("I do nothing")
def do_nothing(context: Context) -> None:
    pass


@given('I reproduce "{scenario}"')
def reproduce_scenario(context: Context, scenario: str, *, keyword: str = "Given") -> None:
    current_feature = cast("Feature", context.feature)
    for included_scenario in current_feature.scenarios:
        if included_scenario.name == scenario:
            for step in included_scenario.steps:
                if step.step_type in ["given", "when"]:
                    context.execute_steps(f"{keyword} {step.name}")
            return
    raise ValueError(f"Unknown scenario {scenario}.")


@when('I reproduce "{scenario}"')
def _reproduce_scenario(context: Context, scenario: str) -> None:
    return reproduce_scenario(context, scenario, keyword="When")


@given('I repeat "{step}" {repeat:d} times')
def repeat_step(context: Context, step: int, repeat: int, *, keyword: str = "Given") -> None:
    for _ in range(repeat):
        context.execute_steps(f"{keyword} {step}")


@when('I repeat "{step}" {repeat:d} times')
def _repeat_step(context: Context, step: int, repeat: int) -> None:
    return repeat_step(context, step, repeat, keyword="When")


@given("I send event {name}")
@given("I send event {name} with {parameter}={value}")
@when("I send event {name}")
@when("I send event {name} with {parameter}={value}")
def send_event(
    context: Context,
    name: str,
    parameter: str | None = None,
    value: str | None = None,
) -> None:
    parameters = {}
    if context.table:
        for row in context.table:
            parameters[row["parameter"].strip()] = literal_eval(row["value"].strip())

    if parameter and value:
        parameters[parameter.strip()] = literal_eval(value.strip())

    context.interpreter.queue(name, **parameters)


@given("I wait {seconds:g} seconds")
@given("I wait {seconds:g} second")
@when("I wait {seconds:g} seconds")
@when("I wait {seconds:g} second")
def wait(context: Context, seconds: float) -> None:
    context.interpreter.clock.time += seconds


@then("state {name} is entered")
def state_is_entered(context: Context, name: str) -> None:
    # Check that state exists
    context.interpreter.statechart.state_for(name)

    test = testing.state_is_entered(context.monitored_trace, name)
    assert test, f"State {name} is not entered"


@then("state {name} is not entered")
def state_is_not_entered(context: Context, name: str) -> None:
    # Check that state exists
    context.interpreter.statechart.state_for(name)

    test = not testing.state_is_entered(context.monitored_trace, name)
    assert test, f"State {name} is entered"


@then("state {name} is exited")
def state_is_exited(context: Context, name: str) -> None:
    # Check that state exists
    context.interpreter.statechart.state_for(name)

    test = testing.state_is_exited(context.monitored_trace, name)
    assert test, f"State {name} is not exited"


@then("state {name} is not exited")
def state_is_not_exited(context: Context, name: str) -> None:
    # Check that state exists
    context.interpreter.statechart.state_for(name)

    test = not testing.state_is_exited(context.monitored_trace, name)
    assert test, f"State {name} is exited"


@then("state {name} is active")
def state_is_active(context: Context, name: str) -> None:
    # Check that state exists
    context.interpreter.statechart.state_for(name)

    assert name in context.interpreter.configuration, f"State {name} is not active"


@then("state {name} is not active")
def state_is_not_active(context: Context, name: str) -> None:
    # Check that state exists
    context.interpreter.statechart.state_for(name)

    assert name not in context.interpreter.configuration, f"State {name} is active"


@then("event {name} is fired")
@then("event {name} is fired with {parameter}={value}")
def event_is_fired(
    context: Context,
    name: str,
    parameter: str | None = None,
    value: str | None = None,
) -> None:
    parameters = {}

    for row in context.table or []:
        parameters[row["parameter"].strip()] = literal_eval(row["value"].strip())

    if parameter and value:
        parameters[parameter.strip()] = literal_eval(value.strip())

    test = testing.event_is_fired(context.monitored_trace, name, parameters)

    if len(parameters) == 0:
        assert test, f"Event {name} is not fired"
    else:
        assert test, f"Event {name} is not fired with parameters {parameters}"


@then("event {name} is not fired")
def event_is_not_fired(context: Context, name: str) -> None:
    test = not testing.event_is_fired(context.monitored_trace, name)
    assert test, f"Event {name} is fired"


@then("no event is fired")
def no_event_is_fired(context: Context) -> None:
    for macrostep in context.monitored_trace:
        assert len(macrostep.sent_events) == 0, "Events {} fired".format(
            ", ".join([e.name for e in macrostep.sent_events]),
        )


@then("variable {variable} equals {value}")
def variable_equals(context: Context, variable: str, value: AST | str) -> None:
    assert variable in context.interpreter.context, f"Variable {variable} is not defined"

    current_value = context.interpreter.context[variable]
    expected_value = literal_eval(value)
    assert current_value == expected_value, (
        f"Variable {variable} equals {current_value}, not {expected_value}"
    )


@then("variable {variable} does not equal {value}")
def variable_does_not_equal(context: Context, variable: str, value: AST | str) -> None:
    assert variable in context.interpreter.context, f"Variable {variable} is not defined"

    current_value = context.interpreter.context[variable]
    expected_value = literal_eval(value)
    assert current_value != expected_value, f"Variable {variable} equals {current_value}"


@then("expression {expression} holds")
def expression_holds(context: Context, expression: str) -> None:
    assert testing.expression_holds(context.interpreter, expression), (
        f"Expression {expression} does not holds"
    )


@then("expression {expression} does not hold")
def expression_does_not_hold(context: Context, expression: str) -> None:
    assert not testing.expression_holds(context.interpreter, expression), (
        f"Expression {expression} holds"
    )


@then("statechart is in a final configuration")
def final_configuration(context: Context) -> None:
    assert context.interpreter.final, "Statechart is not in a final configuration: {}".format(
        ", ".join(context.interpreter.configuration),
    )


@then("statechart is not in a final configuration")
def not_final_configuration(context: Context) -> None:
    assert not context.interpreter.final, "Statechart is in a final configuration: {}".format(
        ", ".join(context.interpreter.configuration),
    )
