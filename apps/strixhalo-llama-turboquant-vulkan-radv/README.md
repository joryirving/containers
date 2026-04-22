# StrixHalo Llama.cpp TurboQuant (Vulkan RADV)

TurboQuant-enabled llama.cpp for AMD Strix Halo via Vulkan RADV.

## Source

- TurboQuant source: [paudley/llama.cpp](https://github.com/paudley/llama.cpp)
- Pinned ref: `b8eda0cc7033dc62ad876dc29c965844928aaf36`

This image rebuilds llama.cpp from the TurboQuant Vulkan lineage while preserving the Strix Halo Vulkan build profile (Ninja, GGML RPC, Vulkan toolchain).

## Base Image

```
docker.io/kyuz0/amd-strix-halo-toolboxes:vulkan-radv@sha256:780dccdc1ef753ea1903616b364671445ae79bac2c3975515c7ab43fe37fd4eb
```

Digest-pinned. Do not use mutable tags.

## Build Args

| Arg                 | Default                                    | Description                |
|---------------------|--------------------------------------------|----------------------------|
| `TURBOQUANT_SOURCE` | `paudley/llama.cpp`                        | TurboQuant upstream source |
| `TURBOQUANT_REF`    | `b8eda0cc7033dc62ad876dc29c965844928aaf36` | TurboQuant commit          |

## Runtime

Exposes only `llama-server`. Runs as `65534:65534`.

## Supported KV Cache Types

- `f32`, `f16`, `bf16`
- `q8_0`, `q4_0`, `q4_1`, `iq4_nl`, `q5_0`, `q5_1`
- `tbq3_0`, `tbq4_0`, `pq3_0`, `pq4_0`

## Recommended Launch Flags

```bash
llama-server -m /model.gguf -ngl 999 -fa 1 --no-mmap --device vulkan --cache-type-k tbq4_0 --cache-type-v tbq4_0
```

## Validation

```bash
# Local build
docker buildx bake image-local --progress=plain 2>&1 | tail -20

# Smoke test
docker run --rm strixhalo-llama-turboquant-vulkan-radv:rolling /usr/bin/llama-server --version
```
