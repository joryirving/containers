import os
from dataclasses import replace
from datetime import datetime, time
from typing import Callable, Optional
from bridge.models import ClaimedItem
from bridge.window import NightWindow, should_dispatch
from bridge.workload import build_workload


def run_once(
    lane: str,
    claim_one: Callable[[str], Optional[ClaimedItem]],
    create_workload: Callable[[dict], None],
    now: datetime,
    window: NightWindow,
    namespace: str,
) -> str:
    if not should_dispatch(lane, now, window):
        return "skipped-window"
    item = claim_one(lane)
    if item is None:
        return "empty-queue"
    # The lane we claimed from is authoritative for routing; the dispatch response's
    # lane is advisory and may be absent (defaults to "normal" in parse_claim_response).
    # Reconcile so an omitted/mismatched response lane can't silently route an
    # escalated claim to the normal coder.
    item = replace(item, lane=lane)
    manifest = build_workload(item, namespace)
    create_workload(manifest)
    return f"created:{manifest['metadata']['name']}"


def _real_main() -> None:  # pragma: no cover - thin wiring, exercised in cluster runbook
    import requests
    from kubernetes import client, config
    from bridge.claim import DispatchClient

    lane = os.environ["BRIDGE_LANE"]
    namespace = os.environ.get("FOREMAN_NAMESPACE", "foreman-system")
    window = NightWindow(
        start=time.fromisoformat(os.environ.get("WINDOW_START", "22:00")),
        end=time.fromisoformat(os.environ.get("WINDOW_END", "06:00")),
    )

    def http_post(url, headers, params):
        r = requests.post(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    dispatch = DispatchClient(
        base_url=os.environ["DISPATCH_URL"],
        token=os.environ["DISPATCH_AGENT_TOKEN"],
        agent_name=os.environ["DISPATCH_AGENT_NAME"],
        http_post=http_post,
    )

    config.load_incluster_config()
    api = client.CustomObjectsApi()

    def create_workload(manifest: dict) -> None:
        try:
            api.create_namespaced_custom_object(
                group="foreman.llmkube.dev", version="v1alpha1",
                namespace=namespace, plural="workloads", body=manifest,
            )
        except client.exceptions.ApiException as e:
            if e.status != 409:  # 409 = already exists -> idempotent no-op
                raise

    result = run_once(lane, dispatch.claim_one, create_workload, datetime.now(), window, namespace)
    print(result)


if __name__ == "__main__":
    _real_main()
