# comfyui-xpu

ComfyUI for Intel Panther Lake integrated graphics (Xe3 architecture, oneAPI
target id `ptl-h`). This image replaces the `yanwk/comfyui-boot:xpu` deployment
and is built from Intel's maintained recipe in
[intel/llm-scaler](https://github.com/intel/llm-scaler) `omni/docker/Dockerfile`
(Apache-2.0), adapted to this repo's standards: everything pinned by immutable
digest/commit, rootless runtime, AMD64 only (the OMIX base and oneAPI toolchain
have no arm64 variants), and trimmed to the node set this host actually runs.

The image is AOT-locked to `ptl-h` through the `omni_xpu_kernel` wheel
(`TORCH_XPU_ARCH_LIST` / `OMNI_XPU_DEVICE` / provider wheel `--xpu-target`).
It is not portable to BMG (`battlemage`) or other XPU targets.

## Runtime contract

- Entry `/llm/entrypoints/start_comfyui.sh`: sources the OMIX oneAPI
  environment, re-orders `LD_LIBRARY_PATH` so the Torch wheel's SYCL/UR runtime
  wins over the compiler image's (Intel's `omix_torch_runtime.sh` reorder),
  then execs `python main.py` from `/llm/ComfyUI`.
- Env knobs: `PORT` (default 8188), `COMFYUI_LISTEN` (default 0.0.0.0),
  `CLI_ARGS` (raw passthrough appended before CLI args, e.g.
  `--enable-dynamic-vram --reserve-vram 4`).
- Writable mounts for UID 65534: the models PVC at `/models/host` (mapped into
  ComfyUI's folder registry via `/llm/configs/comfyui_host_models.yaml`), plus
  `/data/input`, `/data/output`, `/data/user`.
- The container needs the iGPU render node (`/dev/dri/renderD*`) and a user
  with access to the render group; without a device ComfyUI starts but falls
  back to CPU.
- Provenance lives in `/llm/manifests/` (`omni-runtime-constraints.txt` is also
  an active `PIP_CONSTRAINT`), provider wheel sha256s, the pip freeze snapshot,
  and the patched oneDNN identity. Intel's `omni/tools/` validation scripts
  ship at `/llm/tools/` for on-device acceptance.

## Pinned ingredients

All git revisions were verified on 2026-11-25 with `git ls-remote` (ref
present) or, for non-ref commits, a `git fetch --depth 1` of the exact SHA.
PyPI versions were verified against the registry; torch wheels against
`download.pytorch.org/whl/xpu`. The base digest was verified against the
Docker Hub tag manifest listing for `intel/omix:0.4.1-devel-ubuntu24.04`
(the amd64 image digest).

| Ingredient                                                 | Source                                 | Pin                                                                                                           | Verified                                                              |
| ---------------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| OMIX base                                                  | Docker Hub `intel/omix`                | `0.4.1-devel-ubuntu24.04` @ `sha256:6f8c8893…389a`                                                            | yes                                                                   |
| llm-scaler (kernel, adapter node, patches, configs, tools) | `intel/llm-scaler`                     | `2f032c556f5df4348bd1012e07270889cb65d9ae` (main HEAD at adoption)                                            | yes                                                                   |
| oneDNN source build                                        | `uxlfoundation/oneDNN`                 | `03c022d3ffdcee958cfacbe720048e725fdf644c` + bf16-int4 patch `sha256:0a7afff4…daeb`                           | yes                                                                   |
| CUTLASS-SYCL headers                                       | `intel/sycl-tla`                       | `2fc09973bfdf15755090fcb0e3b6ad236408a992`                                                                    | yes                                                                   |
| ComfyUI                                                    | `Comfy-Org/ComfyUI`                    | `v0.45.0` release tag, renovate-managed via `VERSION` (v0.45.0 == commit `989d93d0…`, same commit Intel pins) | yes                                                                   |
| torch / torchvision / torchaudio                           | `download.pytorch.org/whl/xpu`         | `2.14.0+xpu` / `0.29.0+xpu` / `2.11.0+xpu`                                                                    | yes                                                                   |
| comfyui-frontend-package                                   | PyPI                                   | `1.58.5`                                                                                                      | yes                                                                   |
| comfyui-workflow-templates                                 | PyPI                                   | `0.11.105`                                                                                                    | yes                                                                   |
| comfyui-manager                                            | PyPI                                   | `4.2.2`                                                                                                       | yes                                                                   |
| comfy-kitchen / comfy-aimdo (official wheels)              | PyPI                                   | `0.2.41` / `0.6.0`                                                                                            | yes                                                                   |
| comfy-kitchen-xpu provider                                 | `xiangyuT/comfy-kitchen-xpu`           | `f27f58782c51b6ab314b4cc0f6e65c8a6bafa277` (0.2.41)                                                           | yes                                                                   |
| comfy-aimdo-xpu provider                                   | `xiangyuT/comfy-aimdo-xpu`             | `3bc6afbcb92e10a2d4737e79d170190ed787bf89` (0.6.0)                                                            | yes                                                                   |
| ComfyUI-GGUF-XPU                                           | `xiangyuT/ComfyUI-GGUF-XPU`            | `39671fe73117ba97de7011e7e06e32599dcda06d`                                                                    | yes                                                                   |
| ComfyUI-VideoHelperSuite                                   | `Kosinkadink/ComfyUI-VideoHelperSuite` | `775ae691ecbab6a6d09a2c186f95d130cf8a10d3` (main HEAD)                                                        | yes                                                                   |
| ComfyUI-KJNodes                                            | `kijai/ComfyUI-KJNodes`                | `187868f53a7d9df007dbfe85891dab41453f7933` (main HEAD)                                                        | yes                                                                   |
| comfyui_controlnet_aux                                     | `Fannovel16/comfyui_controlnet_aux`    | `e8b689a513c3e6b63edc44066560ca5919c0576e` (upstream pin) + Intel's depth-anything-v2 XPU patch               | yes, and `git apply --check` of Intel's patch passes at this revision |
| ComfyUI_essentials                                         | `cubiq/ComfyUI_essentials`             | `9d9f4bedfc9f0321c19faf71855e228c93bd0dc9` (main HEAD)                                                        | yes                                                                   |

Renovate tracks the image `VERSION` (ComfyUI release) through the annotation in
`docker-bake.hcl`. Bumping it is not a one-line change: the clone fetches the
`v${COMFYUI_VERSION}` tag, so `COMFYUI_VERSION`, the manager/frontend/templates
pins, a `grep` of the shipped version, and a rebuild on the target host all
have to move together.

## Differences from Intel's image

- `XPU_TARGET=ptl-h` instead of `bmg`; the kernel and both provider wheels are
  built for Panther Lake.
- llm-scaler is cloned at a pinned commit instead of COPY'd from a local
  checkout — this repo builds standalone.
- Dropped custom nodes: ComfyUI-nunchaku-XPU and comfy-mono-decode-XPU (not
  used for image generation on this host), ComfyUI-Easy-Use and
  ComfyUI-CacheDiT (not part of the deployment's workflows).
- Dropped the AIMDO native-owner diagnostic build
  (`AIMDO_XPU_BUILD_NATIVE_OWNER_DIAGNOSTIC` stays at its default `0`) and,
  with it, the allocator-preload bootstrap in Intel's `start_comfyui.sh`.
- Entrypoint is ours: it keeps Intel's `omix_torch_runtime.sh` LD reorder and
  replaces the rest of `start_comfyui.sh` with env-driven `PORT`/`CLI_ARGS`;
  the no_proxy default, `--reserve-vram` budget, and DynamicVRAM flag policy
  are intentionally not baked in (pass them via `CLI_ARGS`).
- Runs as `nobody` (65534) with `PYTHONDONTWRITEBYTECODE=1` instead of root
  (repo standard); all runtime writes go to mounted directories.
- Upstream nodes sit at current main HEADs rather than Intel's older pins;
  Intel's controlnet_aux patch was verified to apply cleanly at the chosen
  revision.
- `vim` dropped from the OS layer. `OMNIXPU_INTERPOLATE_FIX=0` and
  `OMNIXPU_H3_TE_INT8_CR=1` keep Intel's runtime values.
- Dropped Intel's `OMNI_*` provenance environment block (it exists for Intel's
  CI plumbing); the same identities ship as labels and `/llm/manifests/`.

## Validation

- Every pin above was independently verified before being written into the
  Dockerfile (methods in the table intro). No unverified pins.
- `gofmt` and `go vet` pass on `apps/comfyui-xpu`.
- **Build validation runs in CI**: the image is linux/amd64 with a oneAPI
  toolchain and cannot be built on the macOS/arm64 dev host. Builds are long
  (oneDNN + kernel compile). The Go test suite runs only GPU-free packaging
  assertions (image user, manifests, provider wheel isolation, pinned
  metadata, ptl-h AOT lock). Kernel/XPU device acceptance cannot run in CI
  and must be done on the Panther Lake host — use
  `/llm/tools/validate_comfyui_image.py` from Intel for that.
- **GPU device access**: the image user (65534) reaches `/dev/dri` only
  because the current deployment runs the pod privileged (root's implicit
  `CAP_DAC_OVERRIDE`). A non-privileged deployment must add
  `--group-add <host render gid>` (and `--device=/dev/dri`); the base image
  ships no `render` group, so a numeric gid is required.
- **Manager writes**: `/opt/venv` and `/llm/ComfyUI/custom_nodes` are chowned
  to the runtime user so ComfyUI-Manager's install-missing-nodes flow works;
  treat runtime pip installs as part of the image's supported behavior.

## Attribution

Build recipe adapted from [intel/llm-scaler](https://github.com/intel/llm-scaler)
(`omni/docker/Dockerfile` and the `omni/` tree), Apache-2.0, and from
[xiangyuT/comfy-kitchen-xpu](https://github.com/xiangyuT/comfy-kitchen-xpu)
provider packaging (commit-pinned above). ComfyUI itself is GPL-3.0-or-later.
This file set carries their copyright notices' intent forward: keep upstream
patch/label identities intact when modifying the build.
