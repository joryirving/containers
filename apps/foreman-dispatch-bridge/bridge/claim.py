from typing import Callable, Optional
from bridge.models import ClaimedItem

# http_post(url, headers, params) -> parsed JSON dict
HttpPost = Callable[[str, dict, dict], dict]


def parse_claim_response(payload: dict) -> Optional[ClaimedItem]:
    if not payload:
        return None
    issue = payload.get("issue")
    if not issue:
        return None
    return ClaimedItem(
        repo=issue["repo"],
        issue_number=int(issue["number"]),
        intent=issue["title"],
        lane=payload.get("lane", "normal"),
    )


class DispatchClient:
    def __init__(self, base_url: str, token: str, agent_name: str, http_post: HttpPost):
        self._base = base_url.rstrip("/")
        self._token = token
        self._agent = agent_name
        self._post = http_post

    def claim_one(self, lane: str) -> Optional[ClaimedItem]:
        url = f"{self._base}/api/issues/claim"
        headers = {"Authorization": f"Bearer {self._token}"}
        params = {"agent": self._agent, "lane": lane}
        return parse_claim_response(self._post(url, headers, params))
