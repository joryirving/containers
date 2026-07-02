from dataclasses import replace
from typing import Callable, Optional

from bridge.models import ClaimedItem
from bridge.workload import (
    build_workload,
    coder_agent_for,
    gate_profile_for,
    ATTEMPT_ANNOTATION,
    ISSUE_ID_ANNOTATION,
)

# How many total coder attempts before the bridge stops retrying a Workload and
# leaves it as a Failed tombstone for human triage. Override via env.
DEFAULT_MAX_ATTEMPTS = 3

ListFailed = Callable[[], list]         # () -> list of Failed Workload manifests (dicts)
DeleteWorkload = Callable[[str], None]  # (name) -> None; blocks until the object is gone
Escalate = Callable[[ClaimedItem], bool]  # (item) -> True when re-laned + unclaimed
LookupIssueId = Callable[[ClaimedItem], str]   # (item) -> dispatch issue id, "" if not found
FeedbackFor = Callable[[str], str]             # (workload name) -> retry feedback text, "" if none


# Bounds the feedback block injected into a retry's coder prompt.
FEEDBACK_MAX_CHARS = 2000


def feedback_from_tasks(tasks: list) -> str:
    """Distill a failed Workload's task results into a retry prompt block.

    Sources, in order of usefulness: a reviewer NO-GO's structured findings
    (missing_tests / scope_creep / *_details), then reviewer summaries, then
    coder failure errors. Returns "" when there is nothing actionable, so the
    caller falls back to a plain (issues-path) retry.
    """
    notes = []
    for t in tasks or []:
        spec = t.get("spec") or {}
        st = t.get("status") or {}
        ex = (st.get("result") or {}).get("extra") or {}
        kind = spec.get("kind")
        if kind == "review" and st.get("verdict") == "NO-GO":
            me = ex.get("modelExtra") or {}
            findings = me.get("findings") or {}
            flags = sorted(k for k, v in findings.items() if v is True and not k.endswith("_details"))
            details = [f"{k}: {v}" for k, v in sorted(findings.items()) if isinstance(v, str) and v]
            summary = ex.get("modelSummary") or ""
            parts = []
            if flags:
                parts.append("findings: " + ", ".join(flags))
            parts.extend(details)
            if summary:
                parts.append(summary)
            if parts:
                notes.append("Reviewer rejected the previous attempt (NO-GO). " + "; ".join(parts))
        elif kind == "issue-fix" and st.get("verdict") in ("NO-GO", "INCOMPLETE"):
            err = ex.get("error") or ""
            if err:
                notes.append(f"Previous coder attempt failed: {err}")
    if not notes:
        return ""
    text = (
        "A previous automated attempt at this issue was rejected. "
        "Address this feedback in your fix:\n- " + "\n- ".join(notes)
    )
    return text[:FEEDBACK_MAX_CHARS]


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
    escalate: Optional[Escalate] = None,
    escalation_lane: str = "",
    lane_coder_agents: Optional[dict] = None,
    lookup_issue_id: Optional[LookupIssueId] = None,
    feedback_for: Optional[FeedbackFor] = None,
) -> list:
    """Retry Failed bridge Workloads, bounded by max_attempts.

    For each Failed Workload:
      - attempt < max_attempts: delete it and recreate a fresh one at attempt+1,
        so it re-runs with the current config (gateProfile, agent refs). The name
        is deterministic, so delete-then-recreate reuses the same name/branch;
        delete_workload must block until the old object is gone.
      - attempt >= max_attempts, not yet in the escalation lane, and an escalate
        hook is wired: move the issue to the escalation lane + release the claim,
        then delete the Workload. The next tick claims it from the escalation
        lane and builds a fresh Workload with that lane's coder Agent. If the
        escalate call fails, keep the tombstone so the next tick retries it.
      - attempt >= max_attempts otherwise (already escalated, or no hook): leave
        it as a Failed tombstone (no action). The issue stays claimed so the
        groomer won't re-serve it into a loop; a human triages from the
        lingering Workload.

    Returns per-Workload outcome strings.
    """
    lane_coder_agents = lane_coder_agents or {}
    results = []
    for wl in list_failed():
        name = ((wl.get("metadata") or {}).get("name")) or "?"
        attempt = attempt_of(wl)
        if attempt >= max_attempts:
            item = item_from_workload(wl)
            if not item.issue_id and lookup_issue_id:
                # Workloads created before the issue-id annotation (bridge <0.3.0)
                # carry "" forever through retries; recover the id from the
                # dispatch queue so they can still escalate.
                item = replace(item, issue_id=lookup_issue_id(item) or "")
            can_escalate = (
                escalate is not None
                and escalation_lane
                and item.lane != escalation_lane
                and item.issue_id
            )
            if can_escalate and escalate(item):
                delete_workload(name)
                results.append(f"{name}:escalated:{item.lane or '?'}->{escalation_lane}")
            else:
                results.append(f"{name}:giveup:{attempt}/{max_attempts}")
            continue
        item = item_from_workload(wl)
        # Collect the previous attempt's review findings / failure BEFORE the
        # delete (the tasks go with the Workload). A retry that knows why it
        # was rejected beats a blind identical re-run.
        feedback = feedback_for(name) if feedback_for else ""
        delete_workload(name)
        manifest = build_workload(
            item,
            namespace,
            gate_profile_for(item.repo, gate_profiles),
            agent_name,
            attempt + 1,
            coder_agent_for(item.lane, lane_coder_agents),
            feedback=feedback,
        )
        create_workload(manifest)
        results.append(f"{name}:retry:{attempt + 1}/{max_attempts}")
    return results
