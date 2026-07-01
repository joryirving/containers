from bridge.models import ClaimedItem
from bridge.workload import (
    workload_name,
    build_workload,
    parse_gate_profiles,
    gate_profile_for,
)

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


def test_build_workload_omits_gate_profile_by_default():
    # No profile -> no gateProfile key, so Foreman keeps its Go default.
    assert "gateProfile" not in build_workload(ITEM, namespace="llm")["spec"]


def test_build_workload_passes_gate_profile_through_verbatim():
    profile = {"language": "node", "commands": {"test": "corepack pnpm i && corepack pnpm test"}}
    wl = build_workload(ITEM, namespace="llm", gate_profile=profile)
    assert wl["spec"]["gateProfile"] == profile


def test_parse_gate_profiles_empty_is_empty_dict():
    assert parse_gate_profiles(None) == {}
    assert parse_gate_profiles("") == {}
    assert parse_gate_profiles("   ") == {}


def test_parse_gate_profiles_parses_json_map():
    raw = '{"misospace/dispatch": {"language": "node"}, "*": {"language": "generic"}}'
    assert parse_gate_profiles(raw) == {
        "misospace/dispatch": {"language": "node"},
        "*": {"language": "generic"},
    }


def test_gate_profile_for_prefers_exact_match_then_wildcard():
    profiles = {"misospace/dispatch": {"language": "node"}, "*": {"language": "generic"}}
    assert gate_profile_for("misospace/dispatch", profiles) == {"language": "node"}
    # Unmatched repo falls back to the wildcard.
    assert gate_profile_for("misospace/miso-chat", profiles) == {"language": "generic"}


def test_gate_profile_for_returns_none_when_no_match_and_no_wildcard():
    assert gate_profile_for("misospace/miso-chat", {"misospace/dispatch": {"language": "node"}}) is None
    assert gate_profile_for("a/b", {}) is None
