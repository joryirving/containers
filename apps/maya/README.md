# Project Maya image

This app builds the GLM-5.3-Flash engine and its vision encoder (`maya-vision`)
from Project Maya for CUDA 13 and `sm_86` (RTX 3090). It follows the upstream
Docker recipe at the upstream release tag `v${VERSION}` plus upstream's
`tools/vision` build: the GLM5NEXT mtmd patch applied to the exact `setup.py`
`LLAMA_CPP_COMMIT`, then the `maya-vision` target. Only the `maya` engine is
built (not `maya-ds4`/`maya-mm3`).

The encoder ships at `build-vision/bin/maya-vision` with a `MAYA-BUILD.json`
stamp whose source hash is computed from the tree as the image ships it, so
upstream's setup accepts the prebuilt binary; a vision-enabled config still
downloads the encoder's mmproj/vocab files at runtime. A Renovate version bump
whose llama.cpp pin moves off the patch's anchors fails the build instead of
shipping a broken encoder.

## Upstream setup runs in this image

`maya.py --setup` works end to end here without compiling anything:

- `build/MAYA-BUILD.json` and `build-vision/MAYA-BUILD.json` carry the source
  hashes upstream's setup compares against, so steps 4 and 7 skip the build.
- The pinned llama.cpp checkout ships at `third_party/llama.cpp`, so step 3
  downloads no source.
- The venv carries the `.strata-pip.json` stamp `setup.py` writes, so step 3
  installs no packages.
- `nvcc` and `g++` are installed, so step 1's toolchain checks pass. They are
  there to satisfy the checks, not to compile: the stamps do that.

Step 8 writes the config, its log and the run script into `/opt/maya`, so that
directory is world-writable with the sticky bit: the shipped code and the
engines stay root-owned and undeletable, and anything new is written as the
image user. Model files go to `--models-dir`, which must be a writable mount.

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
