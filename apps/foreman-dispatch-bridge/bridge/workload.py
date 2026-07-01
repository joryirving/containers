import json
from typing import Optional

from bridge.models import ClaimedItem

# Single coder for the MVP (all lanes route to it); Ornith reviews, deterministic gate verifies.
CODER_AGENT = "coder"
VERIFIER_AGENT = "gate"
REVIEWER_AGENTS = ["reviewer"]

# Fallback key in a gate-profile map: its profile applies to any repo that has
# no entry of its own.
GATE_PROFILE_WILDCARD = "*"


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


def workload_name(item: ClaimedItem) -> str:
    owner_repo = item.repo.replace("/", "-").lower()
    return f"wl-{owner_repo}-{item.issue_number}"


def build_workload(item: ClaimedItem, namespace: str, gate_profile: Optional[dict] = None) -> dict:
    spec = {
        "intent": item.intent,
        "repo": item.repo,
        "issues": [item.issue_number],
        "coderAgentRef": {"name": CODER_AGENT},
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
        },
        "spec": spec,
    }
