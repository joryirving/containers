# Project Maya image

This app builds the GLM-5.3-Flash engine from Project Maya for CUDA 13 and
`sm_86` (RTX 3090). It follows the upstream Docker recipe at a pinned Maya
commit and builds only the `maya` engine needed for this test.

The standard containers release and pull-request workflows build this app for
`linux/amd64` only. The image does not contain model weights. Mount Maya's
generated Maya-S24 pack and configuration at runtime; see Project Maya's
`docs/DOCKER.md` and `docs/MODELS.md`.

The app is intentionally experiment-scoped. Do not change the source commit or
CUDA base digest without rebuilding and validating the image on the target
runtime.
