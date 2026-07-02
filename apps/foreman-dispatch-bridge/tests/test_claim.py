import json
from pathlib import Path
from bridge.models import ClaimedItem
from bridge.claim import select_item, to_claimed_item, DispatchClient

SAMPLE = json.loads(Path("tests/fixtures/dispatch_claim_sample.json").read_text())


def test_select_item_picks_first_ready_claimable_non_renovate():
    item = select_item(SAMPLE, "local")
    # #42 is ready+claimable; #7 is renovate; #99 is backlog.
    assert item["number"] == 42


def test_select_item_skips_renovate_and_non_ready():
    only_bad = [i for i in SAMPLE if i["number"] in (7, 99)]
    assert select_item(only_bad, "local") is None


def test_select_item_respects_lane():
    assert select_item(SAMPLE, "frontier") is None


def test_to_claimed_item_maps_dispatch_fields():
    item = to_claimed_item(SAMPLE[0], "local")
    assert item == ClaimedItem(
        repo="joryirving/home-ops", issue_number=42,
        intent="Fix the flaky reconcile test", lane="local",
        issue_id="iss_abc123",
    )


def test_claim_one_queue_then_claim():
    captured = {}

    def fake_get(url, headers):
        captured["get_url"] = url
        return SAMPLE

    def fake_post(url, headers, payload):
        captured["claim_payload"] = payload
        return {"ok": True}

    client = DispatchClient("http://d/", "tok", http_get=fake_get, http_post=fake_post)
    item = client.claim_one("foreman/coder", "local")
    assert item == ClaimedItem(
        repo="joryirving/home-ops", issue_number=42,
        intent="Fix the flaky reconcile test", lane="local",
        issue_id="iss_abc123",
    )
    assert captured["get_url"] == "http://d/api/agents/foreman/coder/queue?lane=local&includeClaimed=true"
    assert captured["claim_payload"] == {
        "issueId": "iss_abc123", "repoFullName": "joryirving/home-ops",
        "issueNumber": 42, "agentName": "foreman/coder",
    }


def test_claim_one_returns_none_on_409_conflict():
    client = DispatchClient("http://d", "tok",
                            http_get=lambda u, h: SAMPLE,
                            http_post=lambda u, h, p: None)  # None == 409 already claimed
    assert client.claim_one("foreman/coder", "local") is None


def test_claim_one_empty_queue():
    client = DispatchClient("http://d", "tok",
                            http_get=lambda u, h: [],
                            http_post=lambda u, h, p: {"ok": True})
    assert client.claim_one("foreman/coder", "local") is None


def _client_recording_posts(responses=None):
    from bridge.claim import DispatchClient
    posts = []
    resp = list(responses or [])

    def http_post(url, headers, payload):
        posts.append((url, payload))
        return resp.pop(0) if resp else {}

    return DispatchClient("http://d", "tok", lambda u, h: [], http_post), posts


def test_set_lane_posts_manual_classification():
    from bridge.models import ClaimedItem
    c, posts = _client_recording_posts()
    item = ClaimedItem(repo="a/b", issue_number=7, intent="t", lane="local", issue_id="id-7")
    assert c.set_lane(item, "frontier", "3 failed attempts") is True
    url, payload = posts[0]
    assert url == "http://d/api/issues/id-7/lane"
    assert payload["model"] == "bridge-escalation"
    assert payload["classification"] == {"lane": "frontier", "confidence": "high",
                                         "reason": "3 failed attempts"}


def test_unclaim_posts_release():
    from bridge.models import ClaimedItem
    c, posts = _client_recording_posts()
    item = ClaimedItem(repo="a/b", issue_number=7, intent="t", lane="local", issue_id="id-7")
    assert c.unclaim(item, "foreman-coder") is True
    url, payload = posts[0]
    assert url == "http://d/api/issues/unclaim"
    assert payload == {"issueId": "id-7", "repoFullName": "a/b", "issueNumber": 7,
                       "agentName": "foreman-coder"}


def test_escalate_stops_after_failed_lane_move():
    from bridge.models import ClaimedItem
    # First POST (lane) -> None (failure); unclaim must NOT run.
    c, posts = _client_recording_posts(responses=[None])
    item = ClaimedItem(repo="a/b", issue_number=7, intent="t", lane="local", issue_id="id-7")
    assert c.escalate(item, "frontier", "r", "foreman-coder") is False
    assert len(posts) == 1


def test_escalate_lane_then_unclaim():
    from bridge.models import ClaimedItem
    c, posts = _client_recording_posts(responses=[{}, {}])
    item = ClaimedItem(repo="a/b", issue_number=7, intent="t", lane="local", issue_id="id-7")
    assert c.escalate(item, "frontier", "r", "foreman-coder") is True
    assert [u for u, _ in posts] == ["http://d/api/issues/id-7/lane", "http://d/api/issues/unclaim"]
