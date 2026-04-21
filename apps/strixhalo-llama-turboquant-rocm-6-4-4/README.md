# StrixHalo Llama.cpp TurboQuant (ROCm 6.4.4)

TurboQuant-enabled llama.cpp for AMD Strix Halo via ROCm 6.4.4.

## Source

- TurboQuant source: [TheTom/llama-cpp-turboquant](https://github.com/TheTom/llama-cpp-turboquant)
- Pinned ref: `8ba9f128822b4cef73f5555ca5fcccfbfadbcd20`

This image uses the HIP-capable TurboQuant lineage and targets `turbo4` KV cache mode.

## Base Image

```
docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-6.4.4@sha256:957974b729f458ab34f33104e795216a79b347803aff18247355c5a1d61efe43
```

Digest-pinned. Do not use mutable tags.

## Build Profile

Preserved Strix Halo ROCm settings:

- `AMDGPU_TARGETS=gfx1151`
- `LLAMA_HIP_UMA=ON`
- `GGML_CUDA_ENABLE_UNIFIED_MEMORY=ON`

## Build Args

| Arg | Default | Description |
|-----|---------|-------------|
| `TURBOQUANT_SOURCE` | `TheTom/llama-cpp-turboquant` | TurboQuant upstream source |
| `TURBOQUANT_REF` | `8ba9f128822b4cef73f5555ca5fcccfbfadbcd20` | TurboQuant commit |

## Runtime

Exposes only `llama-server`. Runs as `65534:65534`.

## Supported KV Cache Types

- Standard: `f32`, `f16`, `bf16`, `q8_0`, `q4_0`, `q4_1`, `iq4_nl`, `q5_0`, `q5_1`
- TurboQuant: `turbo3`, `turbo4`

## Required ROCm Runtime Target

```bash
llama-server -m /model.gguf -ngl 999 -fa 1 --no-mmap --cache-type-k turbo4 --cache-type-v turbo4
```

## Validation

Build verifies `turbo4` is compiled in via `strings build/bin/llama-server | grep turbo4`.
