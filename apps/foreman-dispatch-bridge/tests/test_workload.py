from bridge.models import ClaimedItem
from bridge.workload import workload_name, build_workload

ITEM = ClaimedItem(repo="defilantech/LLMKube", issue_number=510,
                   intent="Fix the lint-all docs gap", lane="escalated")


def test_workload_name_is_deterministic_and_sanitized():
    assert workload_name(ITEM) == "wl-defilantech-llmkube-510"


def test_build_workload_picks_escalated_coder():
    wl = build_workload(ITEM, namespace="foreman-system")
    assert wl["spec"]["coderAgentRef"]["name"] == "coder-escalated"


def test_build_workload_picks_normal_coder():
    normal = ClaimedItem(repo="x/y", issue_number=7, intent="t", lane="normal")
    wl = build_workload(normal, namespace="foreman-system")
    assert wl["spec"]["coderAgentRef"]["name"] == "coder-normal"


def test_build_workload_structure():
    wl = build_workload(ITEM, namespace="foreman-system")
    assert wl["apiVersion"] == "foreman.llmkube.dev/v1alpha1"
    assert wl["kind"] == "Workload"
    assert wl["metadata"]["namespace"] == "foreman-system"
    assert wl["metadata"]["labels"]["created-by"] == "dispatch-bridge"
    assert wl["spec"]["repo"] == "defilantech/LLMKube"
    assert wl["spec"]["issues"] == [510]
    assert wl["spec"]["verifierAgentRef"]["name"] == "verifier-gate"
