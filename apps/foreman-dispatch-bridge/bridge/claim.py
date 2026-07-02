import re
from typing import Callable, Optional
from bridge.models import ClaimedItem

# Injected transports so the client is testable without network.
# http_get(url, headers) -> parsed JSON ; http_post(url, headers, json) -> parsed JSON | None
HttpGet = Callable[[str, dict], object]
HttpPost = Callable[[str, dict, dict], object]

_RENOVATE_RE = re.compile(r"renovate", re.IGNORECASE)


def _number(item: dict):
    return item.get("number") or item.get("issueNumber")


def _lane(item: dict):
    return item.get("lane") or item.get("currentLane")


def _status(item: dict) -> Optional[str]:
    for label in item.get("labels") or []:
        name = label.get("name") if isinstance(label, dict) else label
        if isinstance(name, str) and name.startswith("status/"):
            return name
    return item.get("status")


def select_item(items: list, lane: str) -> Optional[dict]:
    """First claimable, ready, lane-matching, non-renovate queue item."""
    for item in items:
        if not isinstance(item, dict):
            continue
        if _RENOVATE_RE.search(str(item.get("title") or "")):
            continue
        if (_lane(item) or lane) != lane:
            continue
        if _status(item) != "status/ready":
            continue
        if item.get("claimable") is not True and item.get("agentMatch") is not True:
            continue
        return item
    return None


def to_claimed_item(item: dict, lane: str) -> ClaimedItem:
    return ClaimedItem(
        repo=item["repoFullName"],
        issue_number=int(_number(item)),
        intent=str(item.get("title") or ""),
        lane=_lane(item) or lane,
        issue_id=str(item.get("issueId") or item.get("id") or ""),
    )


class DispatchClient:
    """Two-step dispatch claim: GET the lane queue, select an item, POST a claim."""

    def __init__(self, base_url: str, token: str, http_get: HttpGet, http_post: HttpPost):
        self._base = base_url.rstrip("/")
        self._token = token
        self._get = http_get
        self._post = http_post

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._token}"}

    def queue(self, agent_name: str, lane: str) -> list:
        url = f"{self._base}/api/agents/{agent_name}/queue?lane={lane}&includeClaimed=true"
        data = self._get(url, self._headers())
        return data if isinstance(data, list) else []

    def claim(self, item: dict, agent_name: str) -> bool:
        payload = {
            "issueId": item.get("issueId") or item.get("id"),
            "repoFullName": item.get("repoFullName"),
            "issueNumber": int(_number(item)),
            "agentName": agent_name,
        }
        # http_post returns None on 409 (already claimed by someone else).
        return self._post(f"{self._base}/api/issues/claim", self._headers(), payload) is not None

    def claim_one(self, agent_name: str, lane: str) -> Optional[ClaimedItem]:
        item = select_item(self.queue(agent_name, lane), lane)
        if item is None:
            return None
        if not self.claim(item, agent_name):
            return None
        return to_claimed_item(item, lane)

    def set_lane(self, item: ClaimedItem, lane: str, reason: str) -> bool:
        """Record an explicit lane classification for the issue (manual override)."""
        payload = {
            "model": "bridge-escalation",
            "classification": {"lane": lane, "confidence": "high", "reason": reason},
        }
        url = f"{self._base}/api/issues/{item.issue_id}/lane"
        return self._post(url, self._headers(), payload) is not None

    def unclaim(self, item: ClaimedItem, agent_name: str) -> bool:
        """Release the bridge's claim so the issue is claimable again."""
        payload = {
            "issueId": item.issue_id,
            "repoFullName": item.repo,
            "issueNumber": item.issue_number,
            "agentName": agent_name,
        }
        return self._post(f"{self._base}/api/issues/unclaim", self._headers(), payload) is not None

    def find_issue_id(self, agent_name: str, lanes: list, repo: str, issue_number: int) -> str:
        """Recover a dispatch issue id by repo+number from the lane queues
        (includeClaimed=true, so claimed items are visible). Used to backfill
        Workloads whose issue-id annotation predates bridge 0.3.0."""
        for lane in lanes:
            for item in self.queue(agent_name, lane):
                if not isinstance(item, dict):
                    continue
                if item.get("repoFullName") == repo and int(_number(item) or 0) == issue_number:
                    return str(item.get("issueId") or item.get("id") or "")
        return ""

    def escalate(self, item: ClaimedItem, lane: str, reason: str, agent_name: str) -> bool:
        """Move a given-up issue to the escalation lane and release the claim.

        Lane first, then unclaim: if the unclaim fails the issue stays claimed
        (so nothing re-serves it into a loop) and the caller keeps the Failed
        Workload tombstone, so the next tick retries the escalation.
        """
        return self.set_lane(item, lane, reason) and self.unclaim(item, agent_name)
