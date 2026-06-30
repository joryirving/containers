from bridge.models import ClaimedItem

AGENT_BY_LANE = {"normal": "coder-normal", "escalated": "coder-escalated"}
VERIFIER_AGENT = "verifier-gate"


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
            "coderAgentRef": {"name": AGENT_BY_LANE[item.lane]},
            "verifierAgentRef": {"name": VERIFIER_AGENT},
        },
    }
