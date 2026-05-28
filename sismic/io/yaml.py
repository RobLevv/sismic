from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING, TextIO

import schema
from ruamel import yaml
from schema import Optional, Or, Schema, Use

from .datadict import export_to_dict, import_from_dict

if TYPE_CHECKING:
    from sismic.model import Statechart


class SCHEMA:
    contract = Schema({Or("before", "after", "always"): Use(str)})

    transition = Schema(
        {
            Optional("target"): Use(str),
            Optional("event"): Use(str),
            Optional("guard"): Use(str),
            Optional("action"): Use(str),
            Optional("contract"): [contract],
            Optional("priority"): Or(Use(int), "high", "low"),
        },
    )
    state = {}  # noqa: RUF012
    state.update(
        {
            "name": Use(str),
            Optional("type"): Or("final", "shallow history", "deep history"),
            Optional("on entry"): Use(str),
            Optional("on exit"): Use(str),
            Optional("transitions"): [transition],
            Optional("contract"): [contract],
            Optional("initial"): Use(str),
            Optional("parallel states"): [state],
            Optional("states"): [state],
            Optional("memory"): Use(str),
        },
    )

    statechart = Schema(
        {
            "statechart": {
                "name": Use(str),
                Optional("description"): Use(str),
                Optional("preamble"): Use(str),
                "root state": state,
            },
        },
    )


def import_from_yaml(
    text: TextIO | str | None = None,
    filepath: Path | None = None,
    *,
    ignore_schema: bool = False,
    ignore_validation: bool = False,
) -> Statechart:
    """Import a statechart from a YAML representation (first argument) or a YAML file (filepath
    argument).

    Unless specified, the structure contained in the YAML is validated against a predefined
    schema (see *sismic.io.SCHEMA*), and the resulting statechart is validated using its
    *validate()* method.

    :param text: A YAML text. If not provided, filepath argument has to be provided.
    :param filepath: A path to a YAML file.
    :param ignore_schema: set to *True* to disable yaml validation.
    :param ignore_validation: set to *True* to disable statechart validation.
    :return: a *Statechart* instance
    """
    if not text and not filepath:
        raise TypeError(
            "A YAML must be provided, either using first argument or filepath argument.",
        )
    if text and filepath:
        raise TypeError("Either provide first argument or filepath argument, not both.")
    if filepath:
        with Path(filepath).open() as f:
            text = f.read()

    yml = yaml.YAML(typ="safe", pure=True)
    data = yml.load(text)

    if not ignore_schema:
        data = schema.Schema(SCHEMA.statechart).validate(data)

    sc = import_from_dict(data)

    if not ignore_validation:
        sc.validate()
    return sc


def export_to_yaml(statechart: Statechart, filepath: str | None = None) -> str:
    """Export given *Statechart* instance to YAML. Its YAML representation is returned by
    this function. Automatically save the output to filepath, if provided.

    :param statechart: statechart to export
    :param filepath: save output to given filepath, if provided
    :return: A textual YAML representation
    """
    output = StringIO()

    yml = yaml.YAML(typ="safe", pure=True)
    yml.dump(export_to_dict(statechart), output)

    if filepath:
        with Path(filepath).open("w") as f:
            f.write(output.getvalue())

    return output.getvalue()
