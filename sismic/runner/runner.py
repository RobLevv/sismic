from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sismic.interpreter import Interpreter
    from sismic.model import MacroStep


class AsyncRunner:
    """An asynchronous runner that repeatedly execute given interpreter.

    The runner tries to call its `execute` method every `interval` seconds, assuming
    that a call to that method takes less time than `interval`.
    If not, subsequent call is queued and will occur as soon as possible with
    no delay. The runner stops as soon as the underlying interpreter reaches
    a final configuration.

    The execution must be started with the `start` method, and can be (definitively)
    stopped with the `stop` method. An execution can be temporarily suspended
    using the `pause` and `unpause` methods. A call to `wait` blocks until
    the statechart reaches a final configuration.

    The current state of a runner can be obtained using its `running` and
    `paused` properties.

    While this runner can be used "as is", it is designed to be subclassed and
    as such, proposes several hooks to control the execution and additional
    behaviours:

     - before_run: called (only once!) when the runner is started. By default, does nothing.
     - after_run: called (only once!) when the interpreter reaches a final configuration.
       configuration of the underlying interpreter is reached. By default, does nothing.
     - execute: called at each step of the run. By default, calls the `execute_once`
       method of the underlying interpreter and returns a *list* of macro steps.
     - before_execute: called right before the call to `execute()`. By default, does nothing.
     - after_execute: called right after the call to `execute()` with the returned value
       of `execute()`. By default, does nothing.

    By default, this runner calls the interpreter's `execute_once` method only once per cycle
    (meaning at least one macro step is processed during each cycle). If `execute_all` is
    set to True, then `execute_once` is repeatedly called until no macro step can be
    processed in the current cycle.

    :param interpreter: interpreter instance to run.
    :param interval: interval between two calls to `execute`
    :param execute_all: Repeatedly call interpreter's `execute_once` method at each step.
    """

    def __init__(
        self,
        interpreter: Interpreter,
        interval: float = 0.1,
        *,
        execute_all: bool = False,
    ) -> None:
        """Initialize an AsyncRunner.

        :param interpreter: interpreter to be executed by the runner
        :param interval: interval between two calls to `execute`, defaults to 0.1
        :param execute_all: `execute_once` the interpeter for all steps, defaults to False
        """
        self._unpaused = threading.Event()
        self._stop = threading.Event()

        self.interpreter = interpreter
        self.interval = interval
        self._execute_all = execute_all
        self._thread = threading.Thread(target=self._run)

    @property
    def running(self) -> bool:
        """Holds if execution is currently running (even if it's paused)."""
        return self._thread.is_alive()

    @property
    def paused(self) -> bool:
        """Holds if execution is running but paused."""
        return self.running and not self._unpaused.is_set()

    def start(self) -> None:
        """Start the execution."""
        if self._stop.is_set():
            raise RuntimeError("Cannot restart a stopped runner.")
        if self._thread.is_alive():
            raise RuntimeError("Runner is already started")
        self._unpaused.set()
        self._thread.start()

    def stop(self) -> None:
        """Stop the execution."""
        self._stop.set()
        self._unpaused.set()
        self.wait()

    def pause(self) -> None:
        """Pause the execution."""
        self._unpaused.clear()

    def unpause(self) -> None:
        """Unpause the execution."""
        self._unpaused.set()

    def wait(self) -> None:
        """Wait for the execution to finish."""
        if self._thread.is_alive():
            self._thread.join()

    def execute(self) -> list[MacroStep]:
        """Called each time the interpreter has to be executed."""
        steps = []
        step = self.interpreter.execute_once()

        while step:
            steps.append(step)
            step = self.interpreter.execute_once()

            if not self._execute_all:
                break

        return steps

    def before_execute(self) -> None:
        """Called before each call to `execute()`."""

    def after_execute(self, steps: list[MacroStep]) -> None:
        """Called after each call to self.execute().
        Receives the return value of self.execute().

        :param steps: List of macrosteps returned by self.execute()
        """

    def before_run(self) -> None:
        """Called before running the execution."""

    def after_run(self) -> None:
        """Called after a final configuration is reached."""

    def _run(self) -> None:
        self.before_run()
        self._unpaused.wait()

        while not self.interpreter.final and not self._stop.is_set():
            starttime = time.time()
            self.before_execute()
            r = self.execute()
            self.after_execute(r)

            elapsed = time.time() - starttime
            time.sleep(max(0, self.interval - elapsed))
            self._unpaused.wait()

        # Ensure that self._stop is set if self.interpreter.final holds
        self._stop.set()

        self.after_run()

    def __del__(self) -> None:
        """Cleanly stop all threading executions."""
        self.stop()
