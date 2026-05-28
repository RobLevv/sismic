import unittest
from pathlib import Path

from sismic.interpreter import Interpreter
from sismic.io import import_from_yaml


class MicrowaveTests(unittest.TestCase):
    def setUp(self) -> None:
        with Path("microwave.yaml").open() as f:
            sc = import_from_yaml(f)

        self.oven = Interpreter(sc)
        self.oven.execute_once()

    def test_no_heating_when_door_is_not_closed(self) -> None:
        self.oven.queue("door_opened", "item_placed", "timer_inc")
        self.oven.execute()

        self.oven.queue("cooking_start")

        for step in iter(self.oven.execute_once, None):
            for event in step.sent_events:
                assert event.name != "heating_on"

        assert "cooking_mode" not in self.oven.configuration

    def test_increase_timer(self) -> None:
        self.oven.queue("door_opened", "item_placed", "door_closed")

        events = 10 * ["timer_inc"]
        self.oven.queue(*events)
        self.oven.execute()

        assert self.oven.context["timer"] == 10
