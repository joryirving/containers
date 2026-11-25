#!/usr/bin/env bash
# Keep the OMIX oneAPI environment initialization, then restore the venv's
# Torch-matched SYCL/UR runtime ahead of the OMIX 2026.1 build toolchain, the
# same reorder intel/llm-scaler's omix_torch_runtime.sh performs: without it
# the inherited OMIX environment mixes libsycl from the Torch wheel with
# libur_loader from the compiler image. AIMDO's native allocator bootstrap and
# the provider preflight from upstream start_comfyui.sh are dropped: the
# AIMDO native-owner diagnostic is not built into this image, and the
# ComfyUI-OmniXPU prestartup handles provider discovery itself.
set -eo pipefail

source /opt/intel/oneapi/setvars.sh --force

shopt -s nullglob
torch_library_directories=(
    "${VIRTUAL_ENV}"/lib/python*/site-packages/torch/lib
)
shopt -u nullglob

if [[ ${#torch_library_directories[@]} -ne 1 ]]; then
    echo "expected one Torch library directory under ${VIRTUAL_ENV}" >&2
    exit 1
fi

export LD_LIBRARY_PATH="${VIRTUAL_ENV}/lib:${torch_library_directories[0]}:${LD_LIBRARY_PATH:-}"

cd /llm/ComfyUI
exec python main.py \
    --listen "${COMFYUI_LISTEN:-0.0.0.0}" \
    --port "${PORT:-8188}" \
    --extra-model-paths-config /llm/configs/comfyui_host_models.yaml \
    --input-directory /data/input \
    --output-directory /data/output \
    --user-directory /data/user \
    --enable-manager \
    ${CLI_ARGS:-} "$@"
