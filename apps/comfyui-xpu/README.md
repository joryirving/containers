# comfyui-xpu

ComfyUI for Intel Panther Lake iGPUs (Xe3, `ptl-h`), built on Intel's omni XPU
stack. Replaces the `yanwk/comfyui-boot:xpu` deployment on the `layla` worker.

## Why this image exists

The upstream images are unusable here:

- `yanwk/comfyui-boot:xpu` ships bleeding-edge Python 3.14 / torch 2.15 with
  ComfyUI's Intel-XPU fast paths disabled — quantized models fall back to a
  per-step full dequantization (measured ~1.8 s/step of pure overhead on a 7B
  int8 model), and attention runs on a ~2.3 TF/s math fallback instead of a
  flash kernel.
- `intel/llm-scaler-omni` publishes kernels compiled for Battlemage (`bmg`)
  and a frozen ComfyUI 0.31 stack.
- `igerry/comfyui-b70-xpu` is a good reference but is also `bmg`-locked.

This image builds Intel's current `omni/docker/Dockerfile` recipe (Apache-2.0)
with `XPU_TARGET=ptl-h`, giving native INT8/ConvRot GEMM kernels, fused
rotate+quantize, AdaLN/RMSNorm+RoPE fusions, and the CUTE attention route for
upstream ComfyUI 0.45.

## Ingredients

| Component                                                | Source                                       | Pin                                                    |
| -------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------------ |
| Base (oneAPI 2026.1, GPU runtime)                        | `intel/omix`                                 | `0.4.1-devel-ubuntu24.04@sha256:6f8c8893…`             |
| PyTorch                                                  | download.pytorch.org/whl/xpu                 | `2.14.0+xpu` (vision `0.29.0+xpu`, audio `2.11.0+xpu`) |
| oneDNN                                                   | uxlfoundation/oneDNN + Intel bf16-int4 patch | `03c022d3…` (patch sha256 `0a7afff4…`)                 |
| CUTLASS-SYCL headers                                     | intel/sycl-tla                               | `2fc09973…`                                            |
| omni_xpu_kernel + ComfyUI-OmniXPU node                   | intel/llm-scaler                             | `2f032c55…` (main)                                     |
| ComfyUI                                                  | comfyanonymous/ComfyUI                       | `v0.45.0` release tag (renovate-managed `VERSION`)     |
| comfy-kitchen / XPU runtime provider                     | Comfy-Org + xiangyuT/comfy-kitchen-xpu       | `0.2.41` / `f27f5878…`                                 |
| comfy-aimdo / XPU runtime provider                       | Comfy-Org + xiangyuT/comfy-aimdo-xpu         | `0.6.0` / `3bc6afbc…`                                  |
| ComfyUI-GGUF-XPU                                         | xiangyuT                                     | `39671fe7…`                                            |
| VideoHelperSuite / KJNodes / essentials / controlnet_aux | upstream                                     | commits pinned in the Dockerfile                       |

The kernel wheel is CPython-, torch-ABI-, and AOT-target-locked: a `ptl-h`
wheel must never be reused on BMG, or built from BMG artifacts.

## Deviations from Intel's recipe

- llm-scaler is cloned at a pinned commit instead of COPY'd from the build
  context (we build outside the llm-scaler checkout).
- Trimmed custom nodes: no nunchaku, no mono-decode, no Easy-Use, no CacheDiT
  (none are used by this deployment's image-generation workflows).
- AIMDO native-owner allocator diagnostic is not built (opt-in upstream
  diagnostic; DynamicVRAM weight staging remains available without it).
- Entrypoint is a minimal `python main.py` launcher that reproduces upstream's
  OMIX/Torch runtime library-ordering fix; the AIMDO provider bootstrap and
  preflight from upstream `start_comfyui.sh` are dropped.
- ComfyUI is fetched by the renovate-managed `v${VERSION}` release tag (with a
  shipped-version assert) instead of a frozen commit, so dependency updates and
  the published tag can never drift apart.
- Models are bound at runtime through `--extra-model-paths-config
  configs/comfyui_host_models.yaml` (PVC mounted at `/models/host`); `input/`,
  `output/`, and `user/` are redirected to `/data/{input,output,user}` so no
  runtime writes land in the image layer.

## Runtime

```sh
docker run --device=/dev/dri --privileged \
  -e PORT=8188 -e CLI_ARGS="--use-pytorch-cross-attention" \
  ghcr.io/joryirving/comfyui-xpu:0.45.0
```

`--privileged` matches the current deployment's device access model (hostIPC +
privileged pod on Talos; no DRA claim). The image runs as root: the pod is
privileged by design, the RBD PVC is root-owned, and switching to a non-root
user is a deployment-side change (fsGroup), not an image-side one. `OMNIXPU_H3_TE_INT8_CR` stays `0`
(the MiniMax-H3 text-projection quantization policy is not relevant here);
ComfyUI-OmniXPU's INT8 eligibility repair for `int8_tensorwise` models is on
by default, which is the point of the image.

## Validation

- amd64 build: pending CI (`linux/amd64` only — the oneAPI toolchain and the
  omix base ship no arm64 variants; local builds are impossible on an arm64
  macOS host).
- `container_test.go` pins the packaging contract without a GPU (kernel-wheel
  target identity, provider sidecar purity, manifest constraints, entrypoint
  wiring, onednn source-build identity). Device acceptance (kernel load, CUTE
  attention call, INT8 routing counters) happens on the target host after
  deployment, following intel/llm-scaler's `validate_comfyui_image.sh` flow.
- Every commit pin was verified to exist via `git ls-remote` / registry
  manifest lookup at authoring time.

## Attribution

Dockerfile adapted from [intel/llm-scaler](https://github.com/intel/llm-scaler)
`omni/docker/Dockerfile` (Apache-2.0), which builds on
[xiangyuT/comfy-kitchen-xpu](https://github.com/xiangyuT/comfy-kitchen-xpu)
and [intel/sycl-tla](https://github.com/intel/sycl-tla).
