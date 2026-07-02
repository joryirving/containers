import os
import time
from typing import Callable, Optional
from bridge.models import ClaimedItem
from bridge.workload import (
    build_workload,
    coder_agent_for,
    gate_profile_for,
    parse_gate_profiles,
    parse_lane_coder_agents,
)
from bridge.retry import reconcile_failures, feedback_from_tasks, DEFAULT_MAX_ATTEMPTS

ClaimOne = Callable[[str, str], Optional[ClaimedItem]]  # (agent_name, lane) -> item | None


def run_once(
    lanes: list,
    agent_name: str,
    claim_one: ClaimOne,
    create_workload: Callable[[dict], None],
    namespace: str,
    gate_profiles: Optional[dict] = None,
    lane_coder_agents: Optional[dict] = None,
) -> list:
    """Claim one ready issue per lane and materialize a Workload for each. Returns per-lane outcomes.

    gate_profiles maps "owner/repo" -> a Foreman GateProfile dict; the matching
    profile (or the "*" wildcard) is stamped on each Workload so non-Go repos
    run their own language gate. None/empty leaves gateProfile off (Go default).

    lane_coder_agents maps a lane -> a coder Agent name (with "*" wildcard), so
    an escalation lane can route to a stronger (e.g. cloud-proxy) coder.
    None/empty routes every lane to the default coder.
    """
    gate_profiles = gate_profiles or {}
    lane_coder_agents = lane_coder_agents or {}
    results = []
    for lane in lanes:
        item = claim_one(agent_name, lane)
        if item is None:
            results.append(f"{lane}:empty")
            continue
        manifest = build_workload(
            item,
            namespace,
            gate_profile_for(item.repo, gate_profiles),
            agent_name,
            coder_agent=coder_agent_for(item.lane, lane_coder_agents),
        )
        create_workload(manifest)
        results.append(f"{lane}:created:{manifest['metadata']['name']}")
    return results


def _real_main() -> None:  # pragma: no cover - thin wiring, exercised in the cluster
    import requests
    from kubernetes import client, config
    from bridge.claim import DispatchClient

    base_url = os.environ.get("DISPATCH_URL", "http://dispatch.llm:3000")
    token = os.environ["DISPATCH_AGENT_TOKEN"]
    agent_name = os.environ.get("DISPATCH_AGENT_NAME", "foreman/coder")
    lanes = [l.strip() for l in os.environ.get("DISPATCH_LANES", "local,cloud,frontier").split(",") if l.strip()]
    namespace = os.environ.get("FOREMAN_NAMESPACE", "llm")
    gate_profiles = parse_gate_profiles(os.environ.get("GATEPROFILE_MAP"))
    max_attempts = int(os.environ.get("RETRY_MAX_ATTEMPTS", str(DEFAULT_MAX_ATTEMPTS)))
    # Lane -> coder Agent map, e.g. '{"*": "coder", "frontier": "coder-frontier"}'.
    lane_coder_agents = parse_lane_coder_agents(os.environ.get("LANE_CODER_AGENTS"))
    # When set, exhausted Workloads outside this lane escalate into it (re-lane +
    # unclaim) instead of tombstoning. Empty disables escalation.
    escalation_lane = os.environ.get("ESCALATION_LANE", "").strip()

    def http_get(url, headers):
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()

    def http_post(url, headers, payload):
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code == 409:  # already claimed by another agent
            return None
        r.raise_for_status()
        return r.json()

    dispatch = DispatchClient(base_url, token, http_get, http_post)

    config.load_incluster_config()
    api = client.CustomObjectsApi()

    def create_workload(manifest: dict) -> None:
        try:
            api.create_namespaced_custom_object(
                group="foreman.llmkube.dev", version="v1alpha1",
                namespace=namespace, plural="workloads", body=manifest,
            )
        except client.exceptions.ApiException as e:
            if e.status != 409:  # 409 = Workload already exists -> idempotent no-op
                raise

    def list_failed_workloads() -> list:
        resp = api.list_namespaced_custom_object(
            group="foreman.llmkube.dev", version="v1alpha1",
            namespace=namespace, plural="workloads",
            label_selector="created-by=dispatch-bridge",
        )
        return [
            wl for wl in resp.get("items", [])
            if (wl.get("status") or {}).get("phase") == "Failed"
        ]

    def delete_workload(name: str) -> None:
        # Foreground delete + poll: the retry recreates the same name, so the old
        # object (and its owned AgenticTasks) must be fully gone first.
        try:
            api.delete_namespaced_custom_object(
                group="foreman.llmkube.dev", version="v1alpha1",
                namespace=namespace, plural="workloads", name=name,
                body=client.V1DeleteOptions(propagation_policy="Foreground"),
            )
        except client.exceptions.ApiException as e:
            if e.status == 404:  # already gone
                return
            raise
        for _ in range(60):  # up to ~60s for cascade to complete
            try:
                api.get_namespaced_custom_object(
                    group="foreman.llmkube.dev", version="v1alpha1",
                    namespace=namespace, plural="workloads", name=name,
                )
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    return
                raise
            time.sleep(1)
        raise TimeoutError(f"workload {name} still terminating after 60s")

    def list_workload_tasks(workload_name: str) -> list:
        resp = api.list_namespaced_custom_object(
            group="foreman.llmkube.dev", version="v1alpha1",
            namespace=namespace, plural="agentictasks",
            label_selector=f"foreman.llmkube.dev/workload={workload_name}",
        )
        return resp.get("items", [])

    def feedback_for(workload_name: str) -> str:
        try:
            return feedback_from_tasks(list_workload_tasks(workload_name))
        except Exception as e:  # feedback is best-effort; never block a retry on it
            print(f"{workload_name}:feedback-lookup-failed:{e}")
            return ""

    def lookup_issue_id(item: ClaimedItem) -> str:
        try:
            return dispatch.find_issue_id(agent_name, lanes, item.repo, item.issue_number)
        except Exception as e:  # best-effort; missing id just means no escalation
            print(f"{item.repo}#{item.issue_number}:issue-id-lookup-failed:{e}")
            return ""

    def escalate(item: ClaimedItem) -> bool:
        reason = (
            f"bridge escalation: {max_attempts} failed attempts in lane "
            f"'{item.lane or '?'}' for {item.repo}#{item.issue_number}"
        )
        return dispatch.escalate(item, escalation_lane, reason, agent_name)

    # Retry failed workloads first (so a re-run this tick uses the current config),
    # then claim new work.
    for line in reconcile_failures(
        agent_name, list_failed_workloads, create_workload, delete_workload,
        namespace, gate_profiles, max_attempts,
        escalate=escalate if escalation_lane else None,
        escalation_lane=escalation_lane,
        lane_coder_agents=lane_coder_agents,
        lookup_issue_id=lookup_issue_id,
        feedback_for=feedback_for,
    ):
        print(line)

    for line in run_once(
        lanes, agent_name, dispatch.claim_one, create_workload, namespace,
        gate_profiles, lane_coder_agents,
    ):
        print(line)


if __name__ == "__main__":
    _real_main()
