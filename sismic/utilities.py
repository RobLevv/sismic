"""Group-by util."""

from collections import defaultdict
from collections.abc import Callable, Iterable
from typing import TypeVar

from sismic.model import Transition

T = TypeVar("T", bound=str | int)


def sorted_groupby(
    iterable: Iterable[Transition],
    key: Callable[[Transition], T],
    *,
    reverse: bool = False,
) -> list[tuple[T, list[Transition]]]:
    """Return pairs (label, group) grouped and sorted by label = key(item)."""
    groups: dict[T, list[Transition]] = defaultdict(list[Transition])
    for value in iterable:
        groups[key(value)].append(value)

    return sorted(groups.items(), key=lambda x: x[0], reverse=reverse)
