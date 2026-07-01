import os
from typing import Callable, Optional
from bridge.models import ClaimedItem
from bridge.workload import build_workload, gate_profile_for

ClaimOne = Callable[[str, str], Optional[ClaimedItem]]  # (agent_name, lane) -> item | None


def run_once(
    lanes: list,
    agent_name: str,
    claim_one: ClaimOne,
    create_workload: Callable[[dict], None],
    namespace: str,
    gate_profiles: Optional[dict] = None,
) -> list:
    """Claim one ready issue per lane and materialize a Workload for each. Returns per-lane outcomes.

    gate_profiles maps "owner/repo" -> a Foreman GateProfile dict; the matching
    profile (or the "*" wildcard) is stamped on each Workload so non-Go repos
    run their own language gate. None/empty leaves gateProfile off (Go default).
    """
    gate_profiles = gate_profiles or {}
    results = []
    for lane in lanes:
        item = claim_one(agent_name, lane)
        if item is None:
            results.append(f"{lane}:empty")
            continue
        manifest = build_workload(item, namespace, gate_profile_for(item.repo, gate_profiles))
        create_workload(manifest)
        results.append(f"{lane}:created:{manifest['metadata']['name']}")
    return results


def _real_main() -> None:  # pragma: no cover - thin wiring, exercised in the cluster
    import requests
    from kubernetes import client, config
    from bridge.claim import DispatchClient
    from bridge.workload import parse_gate_profiles

    base_url = os.environ.get("DISPATCH_URL", "http://dispatch.llm:3000")
    token = os.environ["DISPATCH_AGENT_TOKEN"]
    agent_name = os.environ.get("DISPATCH_AGENT_NAME", "foreman/coder")
    lanes = [l.strip() for l in os.environ.get("DISPATCH_LANES", "local,cloud,frontier").split(",") if l.strip()]
    namespace = os.environ.get("FOREMAN_NAMESPACE", "llm")
    gate_profiles = parse_gate_profiles(os.environ.get("GATEPROFILE_MAP"))

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

    for line in run_once(lanes, agent_name, dispatch.claim_one, create_workload, namespace, gate_profiles):
        print(line)


if __name__ == "__main__":
    _real_main()
