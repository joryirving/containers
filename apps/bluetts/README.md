# bluetts

[BlueTTS v3](https://github.com/maxmelichov/BlueTTS) — open-source, MIT-licensed
TTS (44.1 kHz, ONNX Runtime, CPU) serving an OpenAI-compatible speech API
(`/v1/audio/speech`, mp3/wav/pcm/flac/opus/aac), built to replace kokoro in the
homelab (evaluated faster/natural by ear; see home-ops `llm/bluetts` HelmRelease).

This image is English-only: the Hebrew and Yiddish G2P frontends are excluded.
Upstream's English G2P (`polyg2p`) publishes linux x86_64 and macOS wheels only —
there is no linux/arm64 wheel, so arm64 images build but cannot synthesize
English. It ships a single zero-shot cloned voice (`mia`, in `voices-custom/mia.json`)
instead of the 15 stock BlueV3 voices, with render parameters tuned by ear and
delivered as env:

| Env                   | Default  | Meaning                                                                                                                                                                                                   |
| --------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `BLUE_STEPS`          | `16`     | Flow-matching Euler steps (default 8)                                                                                                                                                                     |
| `BLUE_CFG`            | `4.0`    | Classifier-free guidance scale                                                                                                                                                                            |
| `BLUE_PACE_BLEND`     | `0.5`    | Duration smoothing toward fixed pace                                                                                                                                                                      |
| `BLUE_PACE_REF`       | `0.0625` | Seconds-per-token pace reference                                                                                                                                                                          |
| `BLUE_PROVIDERS`      | unset    | Comma-separated ONNX Runtime providers. `WebGpuExecutionProvider` is for WebGPU diagnostics, `OpenVINOExecutionProvider` for Intel GPU/NPU inference. Both provider plugins ship in the amd64 image only. |
| `BLUE_OV_DEVICE`      | `GPU`    | OpenVINO device when selected: `CPU`, `GPU`, `NPU`, `AUTO`.                                                                                                                                               |
| `BLUE_WEBGPU_ADAPTER` | `0`      | Dawn Vulkan adapter index. Only `0` is accepted for the Intel B390.                                                                                                                                       |

The upstream `examples/openai_server.py` is patched (see `openai_server.patch`)
to honor those env vars; upstream hardcodes the 8-step/CFG 4.0 defaults. The
OpenVINO execution provider defaults `device_type` to CPU, so `src/blue_onnx/__init__.py`
is patched (see `openvino.patch`) to pass `BLUE_OV_DEVICE` as provider options —
without it, selecting `OpenVINOExecutionProvider` would silently stay on CPU.
The amd64 image installs the WebGPU and OpenVINO provider plugins. Both
plugins are amd64-only; the arm64 image ships neither and runs on CPU. The
OpenVINO plugin includes its runtime and matches upstream's
`[openvino]` extra. The English-only image does not use the Yiddish frontend
that requires ONNX Runtime 1.27 or later. WebGPU 0.6.0 requires ONNX Runtime
1.24.4 or later and a Vulkan loader. The pinned llama.cpp base image supplies
the loader and Intel ANV userspace. WebGPU mode requires one Intel B390
adapter and rejects software adapters. ONNX Runtime can assign
individual operations to CPU. WebGPU mode disables session-run recovery fallback.
Check operator placement before deployment to exclude CPU-only graphs and
substantial neural computation on CPU. Set `BLUE_PROVIDERS=WebGpuExecutionProvider`
for diagnostics only.
Check the physical device on the target host before you treat a run as
hardware-backed.

`VERSION` is held at the upstream release the voice was tuned against
(manual bumps only — renovate deliberately does not track it); the ONNX
bundle is fetched at `BLUEV3_REVISION` from huggingface.co/notmax123/BlueV3-onnx
with per-file sha256 (LFS oid) verification. Voice JSONs only load against the
bundle they were exported from, so the bundle pin must move together with any
voice regeneration.
