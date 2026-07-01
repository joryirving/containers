from bridge.models import ClaimedItem

# Single coder for the MVP (all lanes route to it); Ornith reviews, deterministic gate verifies.
CODER_AGENT = "coder"
VERIFIER_AGENT = "gate"
REVIEWER_AGENTS = ["reviewer"]


def workload_name(item: ClaimedItem) -> str:
    owner_repo = item.repo.replace("/", "-").lower()
    return f"wl-{owner_repo}-{item.issue_number}"


def build_workload(item: ClaimedItem, namespace: str) -> dict:
    return {
        "apiVersion": "foreman.llmkube.dev/v1alpha1",
        "kind": "Workload",
        "metadata": {
            "name": workload_name(item),
            "namespace": namespace,
            "labels": {"created-by": "dispatch-bridge", "lane": item.lane},
        },
        "spec": {
            "intent": item.intent,
            "repo": item.repo,
            "issues": [item.issue_number],
            "coderAgentRef": {"name": CODER_AGENT},
            "verifierAgentRef": {"name": VERIFIER_AGENT},
            "reviewerAgentRefs": [{"name": name} for name in REVIEWER_AGENTS],
        },
    }
