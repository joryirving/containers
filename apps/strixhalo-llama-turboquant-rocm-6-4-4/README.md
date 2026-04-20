# StrixHalo Llama.cpp TurboQuant (ROCm 6.4.4)

TurboQuant-enabled llama.cpp for AMD Strix Halo via ROCm 6.4.4.

## Source

- TurboQuant source: [unixsysdev/llama-turboquant](https://github.com/unixsysdev/llama-turboquant) `main`
- Reference: [TheTom/llama-cpp-turboquant](https://github.com/TheTom/llama-cpp-turboquant) `feature/turboquant-kv-cache`

### Chosen Over Alternatives

| Rejected | Reason |
|----------|--------|
| paudley/llama.cpp `tq-surgical` | Vulkan-focused, not ROCm-specific |
| TheTom as primary | ~160 commits, too broad for minimal patch approach |
| unixsysdev as primary | Smallest viable ROCm TurboQuant delta: only 2 commits adding TQ3_0 type + docs |

## Base Image

```
docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-6.4.4@sha256:957974b729f458ab34f33104e795216a79b347803aff18247355c5a1d61efe43
```

Digest-pinned. Do not use mutable tags.

## Build Args

| Arg | Default | Description |
|-----|---------|-------------|
| `TURBOQUANT_SOURCE` | `unixsysdev/llama-turboquant` | TurboQuant upstream source |
| `TURBOQUANT_REF` | `main` | TurboQuant branch/ref |

## Runtime

Exposes only `llama-server`. Runs as `nobody:nogroup` (65534:65534).

## Supported KV Cache Types

- `f32`, `f16`, `bf16`
- `q8_0`, `q4_0`, `q4_1`, `iq4_nl`, `q5_0`, `q5_1`
- `tq3_0` (TurboQuant 3-bit)

## Recommended Launch Flags

For symmetric K/V (performance-preferred):

```bash
llama-server -m /model.gguf -ngl 99 --cache-type-k tq3_0 --cache-type-v tq3_0
```

For quality-safe baseline:

```bash
llama-server -m /model.gguf -ngl 99 --cache-type-k q8_0 --cache-type-v q8_0
```

## Known Limitations

- TurboQuant KV cache requires Flash Attention on ROCm. If FA is disabled, quantized V will fail.
- Mixed asymmetric K/V TurboQuant on ROCm: requires explicit validation on target workload before production use.
- Only `linux/amd64` is supported (Strix Halo is amd64-only).

## Validation

```bash
# Local build
docker buildx bake image-local --progress=plain 2>&1 | tail -20

# Smoke test
docker run --rm strixhalo-llama-turboquant-rocm-6-4-4:rolling /usr/local/bin/llama-server --help
```
