from dataclasses import dataclass
from datetime import datetime, time


@dataclass(frozen=True)
class NightWindow:
    start: time  # local, inclusive
    end: time    # local, exclusive; if end <= start the window wraps past midnight

    def contains(self, now: datetime) -> bool:
        t = now.time()
        if self.start <= self.end:
            return self.start <= t < self.end
        return t >= self.start or t < self.end


def should_dispatch(lane: str, now: datetime, window: NightWindow) -> bool:
    if lane == "escalated":
        return window.contains(now)
    return True
