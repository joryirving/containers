from dataclasses import dataclass


@dataclass(frozen=True)
class ClaimedItem:
    repo: str          # "owner/name"
    issue_number: int
    intent: str
    lane: str          # "normal" | "escalated"
