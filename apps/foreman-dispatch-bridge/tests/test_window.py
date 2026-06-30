from datetime import datetime, time
from bridge.window import NightWindow, should_dispatch

WIN = NightWindow(start=time(22, 0), end=time(6, 0))  # 22:00–06:00 local, wraps midnight


def test_escalated_inside_window_dispatches():
    assert should_dispatch("escalated", datetime(2026, 6, 30, 23, 30), WIN) is True


def test_escalated_after_midnight_inside_window():
    assert should_dispatch("escalated", datetime(2026, 6, 30, 2, 0), WIN) is True


def test_escalated_outside_window_blocked():
    assert should_dispatch("escalated", datetime(2026, 6, 30, 12, 0), WIN) is False


def test_normal_always_dispatches_regardless_of_window():
    assert should_dispatch("normal", datetime(2026, 6, 30, 12, 0), WIN) is True
