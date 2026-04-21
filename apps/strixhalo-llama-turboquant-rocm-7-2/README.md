# StrixHalo Llama.cpp TurboQuant (ROCm 7.2)

TurboQuant-enabled llama.cpp for AMD Strix Halo via ROCm 7.2.

## Source

- TurboQuant source: [TheTom/llama-cpp-turboquant](https://github.com/TheTom/llama-cpp-turboquant)
- Pinned ref: `8ba9f128822b4cef73f5555ca5fcccfbfadbcd20`

This image uses the HIP-capable TurboQuant lineage and targets `turbo4` KV cache mode.

## Base Image

```
docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-7.2@sha256:c246a5557e42d1375111160f43fbaa8519d9bf7e3308a87edc76f2d740fabf7c
```

Digest-pinned. Do not use mutable tags.

## Build Profile

Preserved Strix Halo ROCm settings:

- `AMDGPU_TARGETS=gfx1151`
- `LLAMA_HIP_UMA=ON`
- `GGML_CUDA_ENABLE_UNIFIED_MEMORY=ON`
- ROCm 7 unroll workaround: `-mllvm --amdgpu-unroll-threshold-local=600`

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
