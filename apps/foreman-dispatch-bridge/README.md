# foreman-dispatch-bridge

A deterministic, create-only bridge that turns claimable [dispatch](https://github.com/itsmiso-ai/dispatch-workflow)
work items into ephemeral [Foreman](https://llmkube.com/docs/foreman) `Workload` CRs.

It runs as a Kubernetes CronJob (manifests live in home-ops, not here) with a
ServiceAccount scoped to **create-only** on `workloads.foreman.llmkube.dev`. It has
**no LLM calls** — pure plumbing, matching dispatch's "no judgment in scripts" discipline.

Per run it: claims one item from dispatch for a lane, applies overnight-window gating
for the `escalated` lane, maps the item to a `Workload` manifest, and creates it.
Foreman's capability-aware scheduler then dispatches the coder (Strix Halo for escalated,
nvidia for normal) and the verifier gate.

## Layout

- `bridge/` — Python package: `models`, `window`, `claim`, `workload`, `main`.
- `tests/` — pytest unit tests (run logic-level TDD; the image is boot-tested via `container_test.go`).
- `requirements.txt` — runtime deps. `requirements-dev.txt` — adds pytest.

## Dev

```bash
pip install -r requirements-dev.txt
pytest -v
```

## Status

Phase 1 (escalated/overnight lane). Design + plan:
`docs/superpowers/specs/2026-06-30-foreman-dispatch-integration-design.md` and
`docs/superpowers/plans/2026-06-30-foreman-escalated-lane-phase1.md` (in the personal docs tree).

> The dispatch claim-response shape in `tests/fixtures/dispatch_claim_sample.json` is a
> stand-in until plan Task 1 captures the real response; reconcile key names then.
