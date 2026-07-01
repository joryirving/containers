from dataclasses import dataclass


@dataclass(frozen=True)
class ClaimedItem:
    repo: str          # "owner/name"
    issue_number: int
    intent: str
    lane: str          # dispatch worker lane, e.g. "local" | "cloud" | "frontier"
    issue_id: str = ""  # dispatch DB id; needed to unclaim (release) the issue
