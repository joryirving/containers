# Containers

This repository builds and tests rootless, semantically versioned, multi-architecture container images. Individual images live under `apps/`; shared includes and test helpers live in `include/` and `testhelpers/`; `docker-bake.hcl` defines build targets. The Go module uses Go 1.25.1 and testcontainers-go for integration tests.

## Review standards

The detailed image, Dockerfile, supply-chain, security, Go, and review-outcome checklist lives in [.agents/skills/container-image-review/SKILL.md](.agents/skills/container-image-review/SKILL.md). Load it for image, build, entrypoint, runtime, dependency, or release changes.

## Validation

Keep go.mod tidy, run the relevant Go tests and container builds, and verify both linux/amd64 and linux/arm64 when image behavior changes. Report any validation that could not be run rather than implying it passed.
