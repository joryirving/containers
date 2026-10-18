---
name: container-image-review
description: Review container Dockerfiles, image pinning, rootless execution, runtime filesystem behavior, multi-architecture builds, entrypoints, and Go/test changes in joryirving/containers.
---

# Container image review

This repository builds a rootless, semantically versioned, multi-architecture collection of container images. Images live under apps/, shared includes and test helpers live in include/ and testhelpers/, and docker-bake.hcl defines build targets. The Go module uses Go 1.25.1 and testcontainers-go for integration tests.

## Container requirements

- Containers run as nobody:nogroup (UID/GID 65534) by default. A root user requires a concrete capability justification, and the image must switch back to the unprivileged user before its entrypoint runs.
- Runtime base images are pinned to immutable sha256 digests. Do not accept mutable latest tags. Pin build tools and third-party binaries too, and verify checksums when the upstream publishes them.
- Keep one primary process per container. Do not add process supervisors; send logs to stdout/stderr unless a mounted volume is explicitly part of the contract.
- Images support linux/amd64 and linux/arm64. Architecture-specific behavior should use TARGETARCH and be exercised by the build pipeline.
- Runtime must work with a read-only root filesystem where applicable. Persistent state belongs in mounted volumes; use a temporary filesystem for required scratch space rather than writing state into image layers.
- Never bake credentials into Dockerfiles, defaults, entrypoints, or test helpers. Runtime configuration carries secrets; build-time values must not become hardcoded defaults.

## Dockerfile and supply-chain checks

- Flag unjustified root execution, unguarded remote scripts, untrusted download sources, missing package-manager cache cleanup, missing architecture handling, unpinned versions, broad version defaults that hide drift, and runtime writes to the image filesystem.
- Prefer explicit COPY ownership, minimal entrypoints, and a narrow capability set. CAP_SYS_ADMIN needs a concrete justification. Avoid binding services to all interfaces unless the workload requires it.
- Check shell scripts with the repository's shell linting tools and keep base-image/build-tool versions visible to Renovate through the established version-comment convention.
- Do not treat an image as digest-pinned merely because a tag looks versioned. Verify the actual reference syntax.

## Go and tests

- Keep the standard Go layout, a clean go.mod, and justified indirect dependency changes. Integration tests use testcontainers-go; test helpers must not contain credentials.
- Validate the relevant image build and tests, including both supported architectures where the workflow permits. Do not claim multi-architecture verification if only one architecture ran.

## Review outcomes

Approve rootless, digest-pinned, single-purpose images with explicit architecture support and clean build targets. Request changes for missing digests, unjustified root, mutable latest defaults, unsafe download/install patterns, missing architecture support, runtime writes to the image layer, or credential exposure.

Skip review-only findings for documentation-only changes, generated files that are correctly regenerated, CI workflow-only edits handled by the separate workflow review, and bot updates that only change established version comments or container versions without other code changes.

Commit messages and PR titles follow conventional prefixes. Breaking changes must be called out explicitly, and PR descriptions should explain why a change is needed rather than only listing files.
