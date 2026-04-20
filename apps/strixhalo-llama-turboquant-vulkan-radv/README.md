# StrixHalo Llama.cpp TurboQuant (Vulkan RADV)

TurboQuant-enabled llama.cpp for AMD Strix Halo via Vulkan RADV.

## Source

- TurboQuant source: [paudley/llama.cpp](https://github.com/paudley/llama.cpp) `tq-surgical`

### Chosen Over Alternatives

| Rejected | Reason |
|----------|--------|
| unixsysdev/llama-turboquant | ROCm-focused, minimal Vulkan-specific changes |
| TheTom/llama-cpp-turboquant | ~308 commits, too broad for minimal surgical patch approach |
| paudley/tq-surgical as primary | Best Vulkan focus: 34 commits, surgical TurboQuant/Vulkan integration |

## Base Image

```
docker.io/kyuz0/amd-strix-halo-toolboxes:vulkan-radv@sha256:e8d01f28649b8f18733b64a7769d7f0d78ebc6cde46825a253a96fab550ed034
```

Digest-pinned. Do not use mutable tags.

## Build Args

| Arg | Default | Description |
|-----|---------|-------------|
| `TURBOQUANT_SOURCE` | `paudley/llama.cpp` | TurboQuant upstream source |
| `TURBOQUANT_REF` | `tq-surgical` | TurboQuant branch/ref |

## Runtime

Exposes only `llama-server`. Runs as `nobody:nogroup` (65534:65534).

## Supported KV Cache Types

- `f32`, `f16`, `bf16`
- `q8_0`, `q4_0`, `q4_1`, `iq4_nl`, `q5_0`, `q5_1`
- `tq3_0`, `tq4_0` (TurboQuant 3-bit and 4-bit)

## Recommended Launch Flags

For symmetric K/V (performance-preferred):

```bash
llama-server -m /model.gguf -ngl 99 --device vulkan --cache-type-k tq3_0 --cache-type-v tq3_0
```

For quality-safe baseline:

```bash
llama-server -m /model.gguf -ngl 99 --device vulkan --cache-type-k q8_0 --cache-type-v q8_0
```

## Known Limitations

- Flash Attention for TurboQuant types requires K and V types to match. Mixed K/V types fall back to non-FA path.
- TurboQuant KV cache on Vulkan may have different performance characteristics than ROCm.
- Only `linux/amd64` is supported (Strix Halo is amd64-only).

## Validation

```bash
# Local build
docker buildx bake image-local --progress=plain 2>&1 | tail -20

# Smoke test
docker run --rm strixhalo-llama-turboquant-vulkan-radv:rolling /usr/local/bin/llama-server --help
```
