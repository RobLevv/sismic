from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from sismic.interpreter.default import Interpreter
from sismic.runner.runner import AsyncRunner

if TYPE_CHECKING:
    from collections.abc import Generator

    from sismic.model.statechart import Statechart


class MockedRunner(AsyncRunner):
    before_run = MagicMock()
    before_execute = MagicMock()
    after_execute = MagicMock()
    after_run = MagicMock()


class TestAsyncRunner:
    """Test Suite for AsyncRunner."""

    INTERVAL = 0.02

    @pytest.fixture
    def interpreter(self, simple_statechart: Statechart) -> Interpreter:
        return Interpreter(simple_statechart)

    @pytest.fixture
    def runner(self, interpreter: Interpreter) -> Generator[AsyncRunner]:
        r = AsyncRunner(interpreter, interval=0)
        yield r
        r.stop()

    @pytest.fixture
    def mocked_runner(
        self,
        interpreter: Interpreter,
    ) -> Generator[AsyncRunner]:
        r = MockedRunner(interpreter, interval=0)
        yield r
        r.stop()

    def test_not_yet_started(self, runner: AsyncRunner) -> None:
        assert runner.interpreter.configuration == []

        runner.interpreter.queue("goto s2")
        sleep(self.INTERVAL)
        assert runner.interpreter.configuration == []

        runner.start()
        sleep(self.INTERVAL)
        assert runner.interpreter.configuration == ["root", "s3"]

    def test_start(self, runner: AsyncRunner) -> None:
        runner.start()
        sleep(self.INTERVAL)
        assert runner.interpreter.configuration == ["root", "s1"]

        runner.interpreter.queue("goto s2")
        sleep(self.INTERVAL)
        assert runner.interpreter.configuration == ["root", "s3"]

    def test_restart_stopped(self, runner: AsyncRunner) -> None:
        runner.start()
        runner.stop()

        with pytest.raises(RuntimeError, match="Cannot restart"):
            runner.start()

        assert not runner.running

    def test_start_again(self, runner: AsyncRunner) -> None:
        runner.start()

        with pytest.raises(RuntimeError, match="already started"):
            runner.start()

        assert runner.running
        runner.stop()
        assert not runner.running

    def test_hooks(self, mocked_runner: MockedRunner) -> None:

        assert len(mocked_runner.before_run.call_args_list) == 0
        assert len(mocked_runner.before_execute.call_args_list) == 0
        assert len(mocked_runner.after_execute.call_args_list) == 0

        mocked_runner.start()
        sleep(self.INTERVAL)
        assert len(mocked_runner.before_run.call_args_list) == 1

        sleep(self.INTERVAL)

        assert len(mocked_runner.before_execute.call_args_list) > 0
        assert len(mocked_runner.after_execute.call_args_list) > 0

        assert len(mocked_runner.after_run.call_args_list) == 0
        mocked_runner.stop()
        sleep(self.INTERVAL)
        assert len(mocked_runner.after_run.call_args_list) == 1

    def test_final(self, runner: AsyncRunner) -> None:
        runner.start()
        runner.interpreter.queue("goto s2")
        runner.interpreter.queue("goto final")
        sleep(self.INTERVAL)
        sleep(self.INTERVAL)
        assert runner.interpreter.final
        assert not runner.running
        sleep(self.INTERVAL)  # Wait for the thread to finish
        assert not runner._thread.is_alive()

    def test_pause(self, runner: AsyncRunner) -> None:
        runner.start()
        assert not runner.paused

        sleep(self.INTERVAL)
        runner.pause()
        assert runner.paused
        assert runner.running
        assert runner.interpreter.configuration == ["root", "s1"]

        runner.interpreter.queue("goto s2")
        sleep(self.INTERVAL)
        assert runner.interpreter.configuration == ["root", "s1"]

        runner.unpause()
        assert not runner.paused
        assert runner.running
        sleep(self.INTERVAL)
        assert runner.interpreter.configuration == ["root", "s3"]

    def test_state(self, runner: AsyncRunner) -> None:
        assert not runner.running
        assert not runner.paused
        runner.start()
        assert runner.running
        assert not runner.paused
        runner.pause()
        assert runner.running
        assert runner.paused
        runner.unpause()
        assert runner.running
        assert not runner.paused
        runner.stop()
        assert not runner.running
        assert not runner.paused

    def test_join_stopped(self, runner: AsyncRunner) -> None:
        runner.start()
        runner.stop()
        runner.wait()
