# foreman-dispatch-bridge

A deterministic, create-only bridge that turns claimable [dispatch](https://github.com/itsmiso-ai/dispatch-workflow)
work items into ephemeral [Foreman](https://llmkube.com/docs/foreman) `Workload` CRs.

It runs as a Kubernetes CronJob (manifests live in home-ops, not here) with a
ServiceAccount scoped to **create-only** on `workloads.foreman.llmkube.dev`. It has
**no LLM calls** — pure plumbing, matching dispatch's "no judgment in scripts" discipline.

Per run it walks the dispatch lanes (`local`, `cloud`, `frontier`), and for each:
`GET`s the lane queue, selects a ready + claimable non-renovate item, `POST`s a claim,
and maps the claimed issue to a `Workload` that references the `coder`, `gate`, and
`reviewer` Agents. Foreman then runs coder (nvidia) → gate (deterministic) → reviewer
(Ornith on the Strix Halo).

## Layout

- `bridge/` — Python package: `models`, `claim`, `workload`, `main`.
- `tests/` — pytest unit tests (run logic-level TDD; the image is boot-tested via `container_test.go`).
- `requirements.txt` — runtime deps. `requirements-dev.txt` — adds pytest.

## Dev

```bash
pip install -r requirements-dev.txt
pytest -v
```

## Config (env)

- `DISPATCH_URL` (default `http://dispatch.llm:3000`), `DISPATCH_AGENT_TOKEN`
- `DISPATCH_AGENT_NAME` (default `foreman/coder`), `DISPATCH_LANES` (default `local,cloud,frontier`)
- `FOREMAN_NAMESPACE` (default `llm`)

## Status

MVP: single coder, all lanes, no window gating. The claim protocol matches
`itsmiso-ai/dispatch-workflow` (`GET /api/agents/{agent}/queue?lane=…` → select →
`POST /api/issues/claim`). Longer term this logic may move into a dispatch plugin.
