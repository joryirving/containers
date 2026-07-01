from bridge.models import ClaimedItem
from bridge.workload import workload_name, build_workload

ITEM = ClaimedItem(repo="joryirving/home-ops", issue_number=42,
                   intent="Fix the flaky reconcile test", lane="local")


def test_workload_name_is_deterministic_and_sanitized():
    assert workload_name(ITEM) == "wl-joryirving-home-ops-42"


def test_build_workload_uses_single_coder_gate_reviewer():
    wl = build_workload(ITEM, namespace="llm")
    assert wl["spec"]["coderAgentRef"]["name"] == "coder"
    assert wl["spec"]["verifierAgentRef"]["name"] == "gate"
    assert wl["spec"]["reviewerAgentRefs"] == [{"name": "reviewer"}]


def test_build_workload_structure():
    wl = build_workload(ITEM, namespace="llm")
    assert wl["apiVersion"] == "foreman.llmkube.dev/v1alpha1"
    assert wl["kind"] == "Workload"
    assert wl["metadata"]["namespace"] == "llm"
    assert wl["metadata"]["labels"] == {"created-by": "dispatch-bridge", "lane": "local"}
    assert wl["spec"]["repo"] == "joryirving/home-ops"
    assert wl["spec"]["issues"] == [42]
    assert wl["spec"]["intent"] == "Fix the flaky reconcile test"
