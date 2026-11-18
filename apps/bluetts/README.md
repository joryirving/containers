# bluetts

[BlueTTS v3](https://github.com/maxmelichov/BlueTTS) — open-source, MIT-licensed
TTS (44.1 kHz, ONNX Runtime, CPU) serving an OpenAI-compatible speech API
(`/v1/audio/speech`, mp3/wav/pcm/flac/opus/aac), built to replace kokoro in the
homelab (evaluated faster/natural by ear; see home-ops `llm/bluetts` HelmRelease).

This image is English-only: the Hebrew and Yiddish G2P frontends are excluded.
It ships a single zero-shot cloned voice (`mia`, in `voices-custom/mia.json`)
instead of the 15 stock BlueV3 voices, with render parameters tuned by ear and
delivered as env:

| Env               | Default  | Meaning                               |
| ----------------- | -------- | ------------------------------------- |
| `BLUE_STEPS`      | `16`     | Flow-matching Euler steps (default 8) |
| `BLUE_CFG`        | `4.0`    | Classifier-free guidance scale        |
| `BLUE_PACE_BLEND` | `0.5`    | Duration smoothing toward fixed pace  |
| `BLUE_PACE_REF`   | `0.0625` | Seconds-per-token pace reference      |

The upstream `examples/openai_server.py` is patched (see `openai_server.patch`)
to honor those env vars; upstream hardcodes the 8-step/CFG 4.0 defaults.

`VERSION` pins the BlueTTS commit the voice JSON was exported against; the ONNX
bundle is fetched at `BLUEV3_REVISION` from huggingface.co/notmax123/BlueV3-onnx
with per-file sha256 (LFS oid) verification. Voice JSONs only load against the
bundle they were exported from, so both pins must move together.
