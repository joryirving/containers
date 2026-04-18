# Containers — AI Review Standards

You review pull requests for a rootless, semantically versioned, multi-architecture container image collection.

## What This Repo Is

- A Go module building and testing container Dockerfiles
- Individual container images under `apps/`
- Shared include files and test helpers in `include/` and `testhelpers/`
- A `docker-bake.hcl` build orchestration file
- Go 1.25.1 module with `testcontainers-go` for integration testing

## Review Standards

### Container Image Requirements

Every container MUST:

1. **Rootless by default**
   - Run as `nobody:nogroup` / `65534:65534`
   - No `USER root` unless absolutely required for a specific capability
   - If root is temporarily required, switch back to `nobody` before `CMD`/`ENTRYPOINT`

2. **Immutable via digest**
   - Use `@sha256:...` digest pinning for runtime images
   - Do not use mutable tags like `:latest`
   - The action will flag any image reference that lacks a digest

3. **One process per container**
   - Single `CMD` or `ENTRYPOINT`
   - No `s6-overlay`, supervisord, or similar process managers
   - Log to stdout/stderr (no log files unless mounted)

4. **Multi-architecture support**
   - Must build for `linux/amd64` and `linux/arm64`
   - Use `ARG TARGETARCH` for architecture-specific logic
   - Test with `docker/bake-action` or equivalent in CI

5. **Read-only root filesystem compatible**
   - Write persistent data to mounted volumes only
   - Use `/tmp` as a tmpfs when `read_only: true` is needed
   - No state written to image layers at runtime

6. **No secrets baked into images**
   - No API keys, tokens, or credentials in Dockerfiles
   - Use environment variables passed at runtime
   - Use `--build-arg` for sensitive build-time values, not hardcoded defaults

### Dockerfile Quality

Good patterns:
```dockerfile
FROM python:3.13-alpine3.23
ARG TARGETARCH
USER nobody:nogroup
COPY --chown=nobody:nogroup . /app
CMD ["/app/entrypoint.sh"]
```

Bad patterns to flag:
- `USER root` without justification
- `curl | sh` or unguarded external scripts
- Missing `--no-cache` on `apk`/`apt`
- Hardcoded version numbers without `ARG`
- Writing to image filesystem at runtime
- Missing shellcheck/hadolint violations for shell scripts

### Version Pinning

- Base images: pin to a specific tag or digest, not `:latest`
- Build tools: use `ARG VERSION` and pass it at build time
- Renovate-managed dependencies: `@version` format in comments
- Third-party binary downloads: verify checksums when possible

### Security

- No exposed secrets in entrypoint.sh or defaults/*
- Container capability drops: CAP_SYS_ADMIN requires explicit justification
- Network access: flag containers that bind to all interfaces unnecessarily

### Go Code Standards

- Follow standard Go project layout
- go.mod must be clean (go mod tidy)
- Tests: use testcontainers-go for integration tests
- No hardcoded credentials in test helpers

### Commit and PR Standards

- Commit messages: conventional commits (fix:, feat:, chore:, docs:)
- PR titles: descriptive, matching commit style
- PR description: explain why, not just what
- Breaking changes: must be called out explicitly

## What to Flag

- Any USER root in a Dockerfile without a comment explaining why
- Image references without @sha256: digests
- latest tags in Dockerfile FROM or ARG defaults
- Shell scripts that curl | bash or download from untrusted sources
- Missing architecture handling (TARGETARCH)
- Files written to image filesystem at runtime
- Overly broad ARG defaults that mask version drift

## What to Approve

- Rootless containers with correct USER directives
- Digest-pinned image references
- Clean go.mod with no // indirect drift unless justified
- Well-structured docker-bake.hcl targets
- Proper use of COPY --chown
- Minimal, single-purpose entrypoint scripts
- Multi-architecture builds using TARGETARCH

## Skip Review For

- CI-only changes to GitHub Actions workflow files (workflow changes are reviewed separately)
- Dependency bot updates (renovate/) when they only update version comments in Go files or container versions
- Documentation-only PRs
- Auto-generated files from go generate or similar tooling
