# Containers

This repository builds and tests rootless, semantically versioned, multi-architecture container images. Individual images live under `apps/`; shared includes and test helpers live in `include/` and `testhelpers/`; `docker-bake.hcl` defines build targets. The Go module uses Go 1.25.1 and testcontainers-go for integration tests.

## Review standards

The detailed image, Dockerfile, supply-chain, security, Go, and review-outcome checklist lives in [.agents/skills/container-image-review/SKILL.md](.agents/skills/container-image-review/SKILL.md). Load it for image, build, entrypoint, runtime, dependency, or release changes.

## Validation

Keep go.mod tidy, run the relevant Go tests and container builds, and verify both linux/amd64 and linux/arm64 when image behavior changes. Report any validation that could not be run rather than implying it passed.

## Source comments

- Prefer clear names and straightforward code over explanatory comments. Omit comments that merely narrate what the code does.
- Keep each inline implementation comment to one concise line by default. Explain the non-obvious why, not the what; do not evade the limit with an overlong line or consecutive one-line comments.
- Use multiple lines only when needed for a complex algorithm, non-obvious invariant, security constraint, compatibility requirement, or external protocol behavior. Preserve public API documentation, required docstrings, license headers, and machine-readable directives.
- Keep issue history, PR review discussions, prior implementation narratives, and agent reasoning out of source comments; put durable explanations in appropriate documentation.
- While editing code, remove redundant comments and shorten verbose comments in the affected area. Preserve meaningful warnings, invariants, and directives; do not expand the diff into unrelated cleanup.
- Before opening or updating a PR, inspect added and modified source comments and remove or shorten unnecessary prose. Review comment quality semantically, not by mechanically counting lines.
