from bridge.retry import attempt_of, item_from_workload, reconcile_failures


def _failed_wl(name, repo="misospace/dispatch", issue=7, attempt=None, lane="local", issue_id="id-7"):
    ann = {"foreman.llmkube.dev/issue-id": issue_id}
    if attempt is not None:
        ann["foreman.llmkube.dev/attempt"] = str(attempt)
    return {
        "metadata": {"name": name, "labels": {"created-by": "dispatch-bridge", "lane": lane}, "annotations": ann},
        "spec": {"intent": "fix it", "repo": repo, "issues": [issue]},
        "status": {"phase": "Failed"},
    }


def test_attempt_of_defaults_and_parses():
    assert attempt_of(_failed_wl("w")) == 1                    # no annotation -> 1
    assert attempt_of(_failed_wl("w", attempt=2)) == 2
    assert attempt_of({"metadata": {"annotations": {"foreman.llmkube.dev/attempt": "junk"}}}) == 1
    assert attempt_of({}) == 1


def test_item_from_workload_reconstructs_fields():
    item = item_from_workload(_failed_wl("w", repo="a/b", issue=42, lane="cloud", issue_id="xyz"))
    assert item.repo == "a/b"
    assert item.issue_number == 42
    assert item.intent == "fix it"
    assert item.lane == "cloud"
    assert item.issue_id == "xyz"


class _Recorder:
    def __init__(self, failed):
        self.failed = failed
        self.deleted = []
        self.created = []

    def list_failed(self):
        return self.failed

    def delete(self, name):
        self.deleted.append(name)

    def create(self, manifest):
        self.created.append(manifest)


def test_reconcile_retries_below_max_deletes_and_recreates_at_next_attempt():
    r = _Recorder([_failed_wl("wl-misospace-dispatch-7", attempt=1)])
    profiles = {"*": {"language": "generic"}}
    out = reconcile_failures("foreman-coder", r.list_failed, r.create, r.delete,
                             namespace="llm", gate_profiles=profiles, max_attempts=3)
    assert out == ["wl-misospace-dispatch-7:retry:2/3"]
    assert r.deleted == ["wl-misospace-dispatch-7"]
    assert len(r.created) == 1
    m = r.created[0]
    # recreated with attempt+1, the current gateProfile, and the same name/branch
    assert m["metadata"]["annotations"]["foreman.llmkube.dev/attempt"] == "2"
    assert m["metadata"]["name"] == "wl-misospace-dispatch-7"
    assert m["spec"]["gateProfile"] == {"language": "generic"}


def test_reconcile_gives_up_at_max_without_touching_the_workload():
    r = _Recorder([_failed_wl("wl-misospace-dispatch-7", attempt=3)])
    out = reconcile_failures("foreman-coder", r.list_failed, r.create, r.delete,
                             namespace="llm", gate_profiles={}, max_attempts=3)
    assert out == ["wl-misospace-dispatch-7:giveup:3/3"]
    assert r.deleted == []   # left as a tombstone
    assert r.created == []


def test_reconcile_first_attempt_annotation_absent_counts_as_one():
    r = _Recorder([_failed_wl("wl-a-b-1", attempt=None)])
    out = reconcile_failures("foreman-coder", r.list_failed, r.create, r.delete,
                             namespace="llm", gate_profiles={}, max_attempts=3)
    assert out == ["wl-a-b-1:retry:2/3"]
    assert r.created[0]["metadata"]["annotations"]["foreman.llmkube.dev/attempt"] == "2"


def test_reconcile_empty_is_noop():
    r = _Recorder([])
    assert reconcile_failures("foreman-coder", r.list_failed, r.create, r.delete,
                              namespace="llm", gate_profiles={}, max_attempts=3) == []


def test_reconcile_escalates_at_max_when_hook_wired():
    r = _Recorder([_failed_wl("wl-a-b-7", attempt=3, lane="local", issue_id="id-7")])
    escalated = []

    def escalate(item):
        escalated.append(item)
        return True

    out = reconcile_failures("foreman-coder", r.list_failed, r.create, r.delete,
                             "llm", {}, max_attempts=3,
                             escalate=escalate, escalation_lane="frontier")
    assert out == ["wl-a-b-7:escalated:local->frontier"]
    assert [i.issue_id for i in escalated] == ["id-7"]
    assert r.deleted == ["wl-a-b-7"]   # tombstone removed after successful escalation
    assert r.created == []             # the next tick's claim builds the frontier Workload


def test_reconcile_keeps_tombstone_when_escalate_fails():
    r = _Recorder([_failed_wl("wl-a-b-7", attempt=3)])
    out = reconcile_failures("foreman-coder", r.list_failed, r.create, r.delete,
                             "llm", {}, max_attempts=3,
                             escalate=lambda item: False, escalation_lane="frontier")
    assert out == ["wl-a-b-7:giveup:3/3"]
    assert r.deleted == []             # keep the tombstone; next tick retries escalation


def test_reconcile_never_escalates_out_of_the_escalation_lane():
    r = _Recorder([_failed_wl("wl-a-b-7", attempt=3, lane="frontier")])
    out = reconcile_failures("foreman-coder", r.list_failed, r.create, r.delete,
                             "llm", {}, max_attempts=3,
                             escalate=lambda item: True, escalation_lane="frontier")
    assert out == ["wl-a-b-7:giveup:3/3"]
    assert r.deleted == []


def test_reconcile_requires_issue_id_to_escalate():
    r = _Recorder([_failed_wl("wl-a-b-7", attempt=3, issue_id="")])
    out = reconcile_failures("foreman-coder", r.list_failed, r.create, r.delete,
                             "llm", {}, max_attempts=3,
                             escalate=lambda item: True, escalation_lane="frontier")
    assert out == ["wl-a-b-7:giveup:3/3"]


def test_reconcile_retry_uses_lane_coder_agent():
    r = _Recorder([_failed_wl("wl-a-b-7", attempt=1, lane="frontier")])
    reconcile_failures("foreman-coder", r.list_failed, r.create, r.delete,
                       "llm", {}, max_attempts=3,
                       lane_coder_agents={"*": "coder", "frontier": "coder-frontier"})
    assert r.created[0]["spec"]["coderAgentRef"] == {"name": "coder-frontier"}
