from __future__ import annotations

import abc
from time import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sismic.interpreter import Interpreter


class Clock(abc.ABC):
    """Abstract implementation of a clock, as used by an interpreter.

    The purpose of a clock instance is to provide a way for the interpreter
    to get the current time during the execution of a statechart.
    """

    @abc.abstractproperty
    def time(self) -> float:
        """Current time"""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.time}]"


class SimulatedClock(Clock):
    """A simulated clock, starting from 0, that can be manually or automatically
    incremented.

    Manual incrementation can be done by setting a new value to the time attribute.
    Automatic incrementation occurs when start() is called, until stop() is called.
    In that case, clock speed can be adjusted with the speed attribute.
    A value strictly greater than 1 increases clock speed while a value strictly
    lower than 1 slows down the clock.
    """

    def __init__(self) -> None:
        self._base: float = time()
        self._time: float = 0
        self._play: bool = False
        self._speed: float = 1

    @property
    def _elapsed(self) -> float:
        return (time() - self._base) * self._speed if self._play else 0

    def start(self) -> None:
        """Clock will be automatically updated both based on real time and
        its speed attribute.
        """
        if not self._play:
            self._base = time()
            self._play = True

    def stop(self) -> None:
        """Clock won't be automatically updated."""
        if self._play:
            self._time += self._elapsed
            self._play = False

    @property
    def speed(self) -> float:
        """Speed of the current clock. Only affects time if start() is called."""
        return self._speed

    @speed.setter
    def speed(self, speed: float) -> None:
        self._time += self._elapsed
        self._base = time()
        self._speed = speed

    @property
    def time(self) -> float:
        """Time value of this clock."""
        return self._time + self._elapsed

    @time.setter
    def time(self, new_time: float) -> None:
        """Set the time of this clock.

        :param new_time: new time
        """
        if new_time < self._time:
            raise ValueError(
                f"Time must be monotonic, cannot change time from {self._time} to {new_time}",
            )

        self._time = new_time
        self._base = time()

    def __str__(self) -> str:
        return f"{self._time:.2f}"

    def __repr__(self) -> str:
        return "{}[{:.2f},x{},{}]".format(
            self.__class__.__name__,
            self.time,
            self._speed,
            ">" if self._play else "=",
        )


class UtcClock(Clock):
    """A clock that simulates a wall clock in UTC.

    The returned time value is based on Python time.time() function.
    """

    @property
    def time(self) -> float:
        return time()


class SynchronizedClock(Clock):
    """A clock that is synchronized with a given interpreter.

    The synchronization is based on the interpreter's internal time value, not
    on its clock. As a consequence, the time value of a SynchronizedClock only
    changes when the underlying interpreter is executed.

    :param interpreter: an interpreter instance
    """

    def __init__(self, interpreter: Interpreter) -> None:
        self._interpreter = interpreter

    @property
    def time(self) -> float:
        return self._interpreter.time
