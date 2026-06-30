import json
from pathlib import Path
from bridge.models import ClaimedItem
from bridge.claim import parse_claim_response, DispatchClient


def test_parse_empty_queue_returns_none():
    assert parse_claim_response({}) is None
    assert parse_claim_response({"issue": None}) is None


def test_parse_real_sample_yields_claimeditem():
    sample = json.loads(Path("tests/fixtures/dispatch_claim_sample.json").read_text())
    item = parse_claim_response(sample)
    assert isinstance(item, ClaimedItem)
    assert "/" in item.repo
    assert item.issue_number > 0
    assert item.lane in ("normal", "escalated")


def test_client_claim_one_uses_injected_transport():
    captured = {}
    def fake_post(url, headers, params):
        captured["url"] = url
        captured["params"] = params
        return {"issue": {"repo": "a/b", "number": 3, "title": "fix"}, "lane": "escalated"}
    client = DispatchClient("http://d", "tok", "saffron-escalated", http_post=fake_post)
    item = client.claim_one("escalated")
    assert item == ClaimedItem(repo="a/b", issue_number=3, intent="fix", lane="escalated")
    assert captured["params"]["lane"] == "escalated"
