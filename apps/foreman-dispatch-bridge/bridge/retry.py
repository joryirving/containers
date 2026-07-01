from typing import Callable

from bridge.models import ClaimedItem
from bridge.workload import (
    build_workload,
    gate_profile_for,
    ATTEMPT_ANNOTATION,
    ISSUE_ID_ANNOTATION,
)

# How many total coder attempts before the bridge stops retrying a Workload and
# leaves it as a Failed tombstone for human triage. Override via env.
DEFAULT_MAX_ATTEMPTS = 3

ListFailed = Callable[[], list]         # () -> list of Failed Workload manifests (dicts)
DeleteWorkload = Callable[[str], None]  # (name) -> None; blocks until the object is gone


def attempt_of(wl: dict) -> int:
    """Read the attempt counter off a Workload; absent/garbage -> 1."""
    ann = (wl.get("metadata") or {}).get("annotations") or {}
    try:
        return max(1, int(ann.get(ATTEMPT_ANNOTATION, "1")))
    except (TypeError, ValueError):
        return 1


def item_from_workload(wl: dict) -> ClaimedItem:
    """Reconstruct the ClaimedItem from a Workload so build_workload can re-render
    it (with the CURRENT gateProfile/config) on retry."""
    meta = wl.get("metadata") or {}
    spec = wl.get("spec") or {}
    labels = meta.get("labels") or {}
    ann = meta.get("annotations") or {}
    issues = spec.get("issues") or [0]
    return ClaimedItem(
        repo=str(spec.get("repo") or ""),
        issue_number=int(issues[0]),
        intent=str(spec.get("intent") or ""),
        lane=str(labels.get("lane") or ""),
        issue_id=str(ann.get(ISSUE_ID_ANNOTATION) or ""),
    )


def reconcile_failures(
    agent_name: str,
    list_failed: ListFailed,
    create_workload: Callable[[dict], None],
    delete_workload: DeleteWorkload,
    namespace: str,
    gate_profiles: dict,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> list:
    """Retry Failed bridge Workloads, bounded by max_attempts.

    For each Failed Workload:
      - attempt < max_attempts: delete it and recreate a fresh one at attempt+1,
        so it re-runs with the current config (gateProfile, agent refs). The name
        is deterministic, so delete-then-recreate reuses the same name/branch;
        delete_workload must block until the old object is gone.
      - attempt >= max_attempts: leave it as a Failed tombstone (no action). The
        issue stays claimed so the groomer won't re-serve it into a loop; a human
        triages from the lingering Workload.

    Returns per-Workload outcome strings.
    """
    results = []
    for wl in list_failed():
        name = ((wl.get("metadata") or {}).get("name")) or "?"
        attempt = attempt_of(wl)
        if attempt >= max_attempts:
            results.append(f"{name}:giveup:{attempt}/{max_attempts}")
            continue
        item = item_from_workload(wl)
        delete_workload(name)
        manifest = build_workload(
            item,
            namespace,
            gate_profile_for(item.repo, gate_profiles),
            agent_name,
            attempt + 1,
        )
        create_workload(manifest)
        results.append(f"{name}:retry:{attempt + 1}/{max_attempts}")
    return results
