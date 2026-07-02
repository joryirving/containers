import json
from typing import Optional

from bridge.models import ClaimedItem

# Default coder when a lane has no explicit mapping; Ornith reviews, deterministic gate verifies.
CODER_AGENT = "coder"
VERIFIER_AGENT = "gate"
REVIEWER_AGENTS = ["reviewer"]

# Fallback key in a lane->coder-agent map: its agent applies to any lane that
# has no entry of its own.
LANE_CODER_WILDCARD = "*"

# Fallback key in a gate-profile map: its profile applies to any repo that has
# no entry of its own.
GATE_PROFILE_WILDCARD = "*"

# Annotation keys the bridge stamps on each Workload so the failed-workload
# retry loop can read attempt count + the dispatch identity needed to unclaim.
ATTEMPT_ANNOTATION = "foreman.llmkube.dev/attempt"
ISSUE_ID_ANNOTATION = "foreman.llmkube.dev/issue-id"
AGENT_NAME_ANNOTATION = "foreman.llmkube.dev/agent-name"


def parse_gate_profiles(raw: Optional[str]) -> dict:
    """Parse the GATEPROFILE_MAP env var (JSON object: repo -> GateProfile).

    Empty or absent -> {}, so every Workload omits gateProfile and Foreman
    falls back to its Go gate (unchanged behavior). Each value is passed
    through verbatim as Workload.spec.gateProfile, so the full CRD shape is
    expressible from config:

        {
          "misospace/dispatch": {"language": "node",
                                 "commands": {"test": "corepack pnpm i && corepack pnpm test"}},
          "misospace/miso-gallery": {"language": "python",
                                     "commands": {"test": "pip install -q -e . && pytest -q"}},
          "*": {"language": "generic"}
        }

    A bare {"language": "node"} uses the preset's stock image (node:22), which
    ships no eslint/prettier/test deps -- set commands (install-in-command) or
    a pre-baked image for repos with real toolchains.
    """
    raw = (raw or "").strip()
    if not raw:
        return {}
    return json.loads(raw)


def gate_profile_for(repo: str, gate_profiles: dict) -> Optional[dict]:
    """Resolve a repo's gate profile: exact match, then the "*" wildcard, else None."""
    if not gate_profiles:
        return None
    return gate_profiles.get(repo) or gate_profiles.get(GATE_PROFILE_WILDCARD)


def parse_lane_coder_agents(raw: Optional[str]) -> dict:
    """Parse the LANE_CODER_AGENTS env var (JSON object: lane -> coder Agent name).

    Empty or absent -> {}, so every lane routes to the default coder Agent
    (unchanged behavior). Example wiring the escalation tier to a cloud-proxy
    coder:

        {"*": "coder", "frontier": "coder-frontier"}
    """
    raw = (raw or "").strip()
    if not raw:
        return {}
    return json.loads(raw)


def coder_agent_for(lane: str, lane_coder_agents: dict) -> str:
    """Resolve a lane's coder Agent: exact match, then "*", else the default coder."""
    if not lane_coder_agents:
        return CODER_AGENT
    return lane_coder_agents.get(lane) or lane_coder_agents.get(LANE_CODER_WILDCARD) or CODER_AGENT


def workload_name(item: ClaimedItem) -> str:
    owner_repo = item.repo.replace("/", "-").lower()
    return f"wl-{owner_repo}-{item.issue_number}"


def build_workload(
    item: ClaimedItem,
    namespace: str,
    gate_profile: Optional[dict] = None,
    agent_name: str = "",
    attempt: int = 1,
    coder_agent: str = CODER_AGENT,
) -> dict:
    spec = {
        "intent": item.intent,
        "repo": item.repo,
        "issues": [item.issue_number],
        "coderAgentRef": {"name": coder_agent},
        "verifierAgentRef": {"name": VERIFIER_AGENT},
        "reviewerAgentRefs": [{"name": name} for name in REVIEWER_AGENTS],
    }
    if gate_profile:
        # Passed through verbatim. Foreman >= 0.8.23 copies Workload.spec.gateProfile
        # onto every decomposed AgenticTask (the coder self-gate + verify Job), so a
        # non-Go repo runs its own language gate instead of the Go default.
        spec["gateProfile"] = gate_profile
    return {
        "apiVersion": "foreman.llmkube.dev/v1alpha1",
        "kind": "Workload",
        "metadata": {
            "name": workload_name(item),
            "namespace": namespace,
            "labels": {"created-by": "dispatch-bridge", "lane": item.lane},
            # attempt drives the retry cap; issue-id + agent-name let the retry
            # loop unclaim the dispatch issue when retries are exhausted.
            "annotations": {
                ATTEMPT_ANNOTATION: str(attempt),
                ISSUE_ID_ANNOTATION: item.issue_id,
                AGENT_NAME_ANNOTATION: agent_name,
            },
        },
        "spec": spec,
    }
