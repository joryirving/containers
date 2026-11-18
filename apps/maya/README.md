# Project Maya image

This app builds the GLM-5.3-Flash engine from Project Maya for CUDA 13 and
`sm_86` (RTX 3090). It follows the upstream Docker recipe at the upstream
release tag `v${VERSION}` and builds only the `maya` engine needed for this
test.

The standard containers release and pull-request workflows build this app for
`linux/amd64` only. The image does not contain model weights. Mount Maya's
generated Maya-S24 pack and configuration at runtime; see Project Maya's
`docs/DOCKER.md` and `docs/MODELS.md`.

The image runs as UID and GID `65534`. Give that user write access to any
runtime data mounts. Maya needs an unlimited memlock limit for pinned model
memory; set the container's `memlock` ulimit instead of running it as root.

The app is intentionally experiment-scoped. Do not change the source version or
CUDA base digest without rebuilding and validating the image on the target
runtime.
