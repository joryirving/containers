from datetime import datetime, time
from bridge.models import ClaimedItem
from bridge.window import NightWindow
from bridge.main import run_once

WIN = NightWindow(start=time(22, 0), end=time(6, 0))
NIGHT = datetime(2026, 6, 30, 23, 0)
DAY = datetime(2026, 6, 30, 12, 0)


def test_skips_when_escalated_outside_window():
    created = []
    res = run_once("escalated", claim_one=lambda l: (_ for _ in ()).throw(AssertionError("should not claim")),
                   create_workload=created.append, now=DAY, window=WIN, namespace="foreman-system")
    assert res == "skipped-window"
    assert created == []


def test_empty_queue_creates_nothing():
    created = []
    res = run_once("escalated", claim_one=lambda l: None,
                   create_workload=created.append, now=NIGHT, window=WIN, namespace="foreman-system")
    assert res == "empty-queue"
    assert created == []


def test_creates_workload_when_item_present_in_window():
    created = []
    item = ClaimedItem(repo="a/b", issue_number=3, intent="fix", lane="escalated")
    res = run_once("escalated", claim_one=lambda l: item,
                   create_workload=created.append, now=NIGHT, window=WIN, namespace="foreman-system")
    assert res == "created:wl-a-b-3"
    assert created[0]["spec"]["coderAgentRef"]["name"] == "coder-escalated"
