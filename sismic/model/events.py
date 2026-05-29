from typing import Generic, TypeVar

T = TypeVar("T", bound="str|float|Event|None")


class Event(Generic[T]):
    """An event with a name and (optionally) some data passed as named parameters.

    The list of parameters can be obtained using *dir(event)*. Notice that
    *name* and *data* are reserved names. If a *delay* parameter is provided,
    then this event will be considered as a delayed event (and won't be
    executed until given delay has elapsed).

    When two events are compared, they are considered equal if their names
    and their data are equal.

    :param name: name of the event.
    :param data: additional data passed as named parameters.
    """

    __slots__ = ["data", "name"]

    def __init__(self, name: str, **additional_parameters: T) -> None:
        self.name = name
        self.data = additional_parameters

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Event):
            return self.name == other.name and self.data == other.data
        return NotImplemented

    def __getattr__(self, attr: str) -> T:
        try:
            return self.data[attr]
        except KeyError as err:
            raise AttributeError(name=attr, obj=self) from err

    def __getstate__(self) -> tuple[str, dict[str, T]]:
        # For pickle and implicitly for multiprocessing
        return self.name, self.data

    def __setstate__(self, state: tuple[str, dict[str, T]]) -> None:
        # For pickle and implicitly for multiprocessing
        self.name, self.data = state

    def __hash__(self) -> int:
        return hash(self.name)

    def __dir__(self) -> list[str]:
        return ["name", *list(self.data.keys())]

    def __repr__(self) -> str:
        if self.data:
            return (
                f"{self.__class__.__name__}"
                f"({self.name}, {', '.join(f'{k}={v!r}' for k, v in self.data.items())})"
            )
        return f"{self.__class__.__name__}({self.name!r})"


class InternalEvent(Event):
    """Subclass of Event that represents an internal event."""


class MetaEvent(Event):
    """Subclass of Event that represents a MetaEvent, as used in property statecharts."""
