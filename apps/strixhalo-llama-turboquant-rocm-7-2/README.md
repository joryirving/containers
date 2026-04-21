# StrixHalo Llama.cpp TurboQuant (ROCm 7.2)

TurboQuant-enabled llama.cpp for AMD Strix Halo via ROCm 7.2.

## Source

- TurboQuant source: [TheTom/llama-cpp-turboquant](https://github.com/TheTom/llama-cpp-turboquant) `feature/turboquant-kv-cache`
- Pinned commit: `8ba9f128822b4cef73f5555ca5fcccfbfadbcd20`

This fork explicitly supports HIP/AMD and exposes `turbo3` and `turbo4` KV cache types.

## Base Image

```
docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-7.2@sha256:c246a5557e42d1375111160f43fbaa8519d9bf7e3308a87edc76f2d740fabf7c
```

Digest-pinned. Do not use mutable tags.

## Build Args

| Arg | Default | Description |
|-----|---------|-------------|
| `TURBOQUANT_SOURCE` | `TheTom/llama-cpp-turboquant` | TurboQuant upstream source |
| `TURBOQUANT_REF` | `8ba9f128822b4cef73f5555ca5fcccfbfadbcd20` | TurboQuant commit |

## Runtime

Exposes only `llama-server`. Runs as `nobody:nobody`.

## Supported KV Cache Types

- `f32`, `f16`, `bf16`
- `q8_0`, `q4_0`, `q4_1`, `iq4_nl`, `q5_0`, `q5_1`
- `turbo3` (TurboQuant 3-bit)
- `turbo4` (TurboQuant 4-bit, recommended)

## Recommended Launch Flags

Performance-preferred (turbo4 symmetric K/V):

```bash
llama-server -m /model.gguf -ngl 99 --cache-type-k turbo4 --cache-type-v turbo4
```

Quality-safe baseline:

```bash
llama-server -m /model.gguf -ngl 99 --cache-type-k q8_0 --cache-type-v q8_0
```

## Known Limitations

- TurboQuant KV cache requires Flash Attention on ROCm. If FA is disabled, quantized V will fail.
- Only `linux/amd64` is supported (Strix Halo is amd64-only).

## Validation

```bash
# Local build
docker buildx bake image-local --progress=plain 2>&1 | tail -20

# Smoke test
docker run --rm strixhalo-llama-turboquant-rocm-7-2:rolling /usr/local/bin/llama-server --help
```
