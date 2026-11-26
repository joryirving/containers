# syntax=docker/dockerfile:1
# ComfyUI for Intel Panther Lake iGPUs (Xe3, target ptl-h), built on Intel's
# omni XPU stack. The stage layout and the oneDNN/kernel/provider recipes are
# adapted from intel/llm-scaler omni/docker/Dockerfile @ 2f032c556f5df4348bd1012e07270889cb65d9ae
# (Apache-2.0); llm-scaler is fetched at that pinned commit instead of COPY'd
# from the build context, and the image is trimmed to the nodes this deployment
# runs (no nunchaku, no mono-decode, no Easy-Use/CacheDiT). AMD64 only: the
# oneAPI toolchain and the omix base ship no arm64 variants.

# ComfyUI image for Intel Panther Lake iGPUs (Xe3, XPU_TARGET=ptl-h).
# Adapted from intel/llm-scaler omni/docker/Dockerfile (Apache-2.0), which
# builds on xiangyuT/comfy-kitchen-xpu and intel/sycl-tla (Apache-2.0).
# Upstream: https://github.com/intel/llm-scaler

ARG BASE_IMAGE=intel/omix:0.4.1-devel-ubuntu24.04@sha256:6f8c8893cc89ff441e3604a3d785d78bdbe79726550e88d5cf8eab769444389a
ARG PYTHON_VERSION=3.12
ARG TORCH_VERSION=2.14.0+xpu
ARG TORCHVISION_VERSION=0.29.0+xpu
ARG TORCHAUDIO_VERSION=2.11.0+xpu
ARG ONEDNN_VERSION=2026.0.0
ARG ONEDNN_SOURCE_REPOSITORY=https://github.com/uxlfoundation/oneDNN.git
ARG ONEDNN_SOURCE_COMMIT=03c022d3ffdcee958cfacbe720048e725fdf644c
ARG ONEDNN_PATCH_SHA256=0a7afff4134f115b4bc53f46301ca3d62b1c11dc02e32c64635c469769fcdaeb
# ptl-h: Panther Lake Xe3 iGPU. The kernel wheel is AOT-compiled for this
# target and must not be reused on, or built from, BMG artifacts.
ARG XPU_TARGET=ptl-h
ARG MAX_JOBS=8
ARG VERSION=0.45.0
ARG IMAGE_TAG=${VERSION}

ARG SYCL_TLA_REPOSITORY=https://github.com/intel/sycl-tla.git
ARG SYCL_TLA_COMMIT=2fc09973bfdf15755090fcb0e3b6ad236408a992
ARG LLM_SCALER_REPOSITORY=https://github.com/intel/llm-scaler.git
# Intel's maintained recipe source; the omni/ tree (kernel, adapter node,
# patches, configs, tools) and the ComfyUI/kitchen/aimdo pins below are read
# from this revision. Bump only together with a rebuild on the target host.
ARG LLM_SCALER_COMMIT=2f032c556f5df4348bd1012e07270889cb65d9ae
ARG COMFYUI_REPOSITORY=https://github.com/Comfy-Org/ComfyUI.git
ARG COMFYUI_VERSION=0.45.0
ARG COMFYUI_FRONTEND_VERSION=1.58.5
ARG COMFYUI_WORKFLOW_TEMPLATES_VERSION=0.11.105
ARG COMFYUI_MANAGER_VERSION=4.2.2
ARG COMFY_KITCHEN_REPOSITORY=https://github.com/xiangyuT/comfy-kitchen-xpu.git
ARG COMFY_KITCHEN_COMMIT=f27f58782c51b6ab314b4cc0f6e65c8a6bafa277
ARG COMFY_KITCHEN_VERSION=0.2.41
ARG COMFY_KITCHEN_PROVIDER_VERSION=0.2.41
ARG COMFY_AIMDO_REPOSITORY=https://github.com/xiangyuT/comfy-aimdo-xpu.git
ARG COMFY_AIMDO_COMMIT=3bc6afbcb92e10a2d4737e79d170190ed787bf89
ARG COMFY_AIMDO_VERSION=0.6.0
ARG COMFY_AIMDO_PROVIDER_VERSION=0.6.0
ARG COMFY_GGUF_REPOSITORY=https://github.com/xiangyuT/ComfyUI-GGUF-XPU.git
ARG COMFY_GGUF_COMMIT=39671fe73117ba97de7011e7e06e32599dcda06d
# Upstream nodes at their current main heads (Intel pins older revisions); the
# controlnet_aux XPU patch was verified to apply to the revision below.
ARG COMFY_VHS_COMMIT=775ae691ecbab6a6d09a2c186f95d130cf8a10d3
ARG COMFY_KJNODES_COMMIT=187868f53a7d9df007dbfe85891dab41453f7933
ARG COMFY_CONTROLNET_AUX_COMMIT=e8b689a513c3e6b63edc44066560ca5919c0576e
ARG COMFY_ESSENTIALS_COMMIT=9d9f4bedfc9f0321c19faf71855e228c93bd0dc9

# ======== Stable OS/toolchain base ========
# Keep device, image-version, Kitchen, and local-source arguments out of this
# stage. Changes to those inputs must not invalidate apt or Python setup.
FROM ${BASE_IMAGE} AS os-base

ARG PYTHON_VERSION

ENV DEBIAN_FRONTEND=noninteractive

SHELL ["bash", "-c"]

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update -y && \
    apt-get install -y --no-install-recommends --fix-missing \
        ca-certificates curl ffmpeg git patch \
        python${PYTHON_VERSION}-dev python${PYTHON_VERSION}-venv python3-pip \
        build-essential ninja-build cmake pkg-config \
        libsndfile1 libsm6 libxext6 libgl1 \
        lsb-release numactl wget linux-libc-dev \
        libopengl0 libglx0 libxrender1 libxfixes3 libx11-dev \
        libxi6 libxxf86vm1 libxcursor1 libxrandr2 libxinerama1 \
        libxkbcommon0

# ======== llm-scaler source ========
# omni_xpu_kernel, the ComfyUI-OmniXPU adapter node, patches, configs, and
# validation tools all live in llm-scaler. Clone once, pinned, and copy
# per-need into later stages so a kernel edit never invalidates the ComfyUI
# dependency tree. Intel's Dockerfile COPY's these from its own checkout;
# this repo builds standalone, so the checkout is fetched at a pinned commit.
FROM os-base AS llm-scaler

ARG LLM_SCALER_REPOSITORY
ARG LLM_SCALER_COMMIT

RUN set -euo pipefail && \
    git clone --filter=blob:none --no-checkout \
        "${LLM_SCALER_REPOSITORY}" /llm-scaler && \
    git -C /llm-scaler fetch --depth 1 origin "${LLM_SCALER_COMMIT}" && \
    git -C /llm-scaler checkout --detach FETCH_HEAD && \
    test "$(git -C /llm-scaler rev-parse HEAD)" = "${LLM_SCALER_COMMIT}" && \
    test -d /llm-scaler/omni/omni_xpu_kernel && \
    test -d /llm-scaler/omni/ComfyUI-OmniXPU

# ======== Stable Python/Torch base ========
# This stage is shared by the ComfyUI dependency, Kitchen, and kernel branches.
# It changes only when the base Python/Torch/oneDNN environment changes.
FROM os-base AS python-base

ARG PYTHON_VERSION
ARG TORCH_VERSION
ARG TORCHVISION_VERSION
ARG TORCHAUDIO_VERSION
ARG ONEDNN_VERSION
ARG ONEDNN_SOURCE_REPOSITORY
ARG ONEDNN_SOURCE_COMMIT
ARG ONEDNN_PATCH_SHA256
ARG MAX_JOBS

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:/opt/intel/oneapi/compiler/latest/bin:${PATH}" \
    PIP_EXTRA_INDEX_URL="https://download.pytorch.org/whl/xpu" \
    PIP_DISABLE_PIP_VERSION_CHECK=1

ENV LD_LIBRARY_PATH="/opt/venv/lib:/opt/venv/lib/python${PYTHON_VERSION}/site-packages/torch/lib:/opt/intel/oneapi/compiler/latest/lib:/opt/intel/oneapi/dnnl/latest/lib:/opt/intel/oneapi/mkl/latest/lib:/opt/intel/oneapi/tbb/latest/lib:/opt/intel/oneapi/mpi/latest/lib"

RUN python${PYTHON_VERSION} -m venv ${VIRTUAL_ENV} && \
    pip install --upgrade pip setuptools wheel

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install \
        torch==${TORCH_VERSION} \
        torchvision==${TORCHVISION_VERSION} \
        torchaudio==${TORCHAUDIO_VERSION} \
        --index-url https://download.pytorch.org/whl/xpu && \
    pip install \
        pytest \
        onednn==${ONEDNN_VERSION} \
        onednn-devel==${ONEDNN_VERSION} && \
    pip check

COPY --from=llm-scaler /llm-scaler/omni/patches/onednn-v3.11.2-enable-bf16-int4-dequantization.patch \
    /llm/patches/onednn-v3.11.2-enable-bf16-int4-dequantization.patch

# oneDNN 3.11 disabled its optimized BF16 INT4 dequantization path in
# 0d99c32b03614d6943b993974f91d419e3c3a0f6. That changes the observable
# BF16 materialization contract used by Kitchen SVDQuant. Build the exact
# 3.11.2 release with the reviewed two-site restoration instead of downgrading
# the runtime or weakening exact correctness. Keep the Python distribution
# version pinned above and record source, patch, and installed-DSO identities.
RUN set -euo pipefail && \
    echo "${ONEDNN_PATCH_SHA256}  /llm/patches/onednn-v3.11.2-enable-bf16-int4-dequantization.patch" \
        | sha256sum --check - && \
    git clone --filter=blob:none --no-checkout \
        "${ONEDNN_SOURCE_REPOSITORY}" /tmp/onednn-source && \
    git -C /tmp/onednn-source fetch --depth 1 origin \
        "${ONEDNN_SOURCE_COMMIT}" && \
    git -C /tmp/onednn-source checkout --detach FETCH_HEAD && \
    test "$(git -C /tmp/onednn-source rev-parse HEAD)" \
        = "${ONEDNN_SOURCE_COMMIT}" && \
    git -C /tmp/onednn-source apply --check \
        /llm/patches/onednn-v3.11.2-enable-bf16-int4-dequantization.patch && \
    git -C /tmp/onednn-source apply \
        /llm/patches/onednn-v3.11.2-enable-bf16-int4-dequantization.patch && \
    git -C /tmp/onednn-source diff --check && \
    set +u && \
    source /opt/intel/oneapi/setvars.sh --force && \
    set -u && \
    cmake -S /tmp/onednn-source -B /tmp/onednn-build -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX="${VIRTUAL_ENV}" \
        -DCMAKE_C_COMPILER=/opt/intel/oneapi/compiler/2026.1/bin/icx \
        -DCMAKE_CXX_COMPILER=/opt/intel/oneapi/compiler/2026.1/bin/icpx \
        -DDNNL_BUILD_DOC=OFF \
        -DDNNL_BUILD_EXAMPLES=OFF \
        -DDNNL_BUILD_TESTS=OFF \
        -DDNNL_CPU_RUNTIME=NONE \
        -DDNNL_GPU_RUNTIME=SYCL \
        -DDNNL_GPU_VENDOR=INTEL \
        -DONEDNN_BUILD_GRAPH=OFF && \
    cmake --build /tmp/onednn-build --parallel "${MAX_JOBS}" && \
    cmake --install /tmp/onednn-build && \
    test "$(readlink -f "${VIRTUAL_ENV}/lib/libdnnl.so.3")" \
        = "${VIRTUAL_ENV}/lib/libdnnl.so.3.11" && \
    mkdir -p /llm/manifests && \
    library_sha256="$(sha256sum "${VIRTUAL_ENV}/lib/libdnnl.so.3.11" \
        | awk '{print $1}')" && \
    printf '%s\n' \
        "schema_version=1" \
        "package_version=${ONEDNN_VERSION}" \
        "source_repository=${ONEDNN_SOURCE_REPOSITORY}" \
        "source_revision=${ONEDNN_SOURCE_COMMIT}" \
        "patch_sha256=${ONEDNN_PATCH_SHA256}" \
        "library_path=${VIRTUAL_ENV}/lib/libdnnl.so.3.11" \
        "library_sha256=${library_sha256}" \
        > /llm/manifests/onednn-runtime.env && \
    rm -rf /tmp/onednn-source /tmp/onednn-build && \
    pip check

RUN mkdir -p /llm /wheels /llm/patches

# ======== Pinned native headers ========
# Header acquisition is independent of both local native projects. A kernel
# source change reuses this stage; a Kitchen change never reaches it.
FROM python-base AS sycl-tla

ARG SYCL_TLA_REPOSITORY
ARG SYCL_TLA_COMMIT

RUN cd /llm && \
    git clone --filter=blob:none --no-checkout \
        "${SYCL_TLA_REPOSITORY}" sycl-tla && \
    git -C sycl-tla fetch --depth 1 origin "${SYCL_TLA_COMMIT}" && \
    git -C sycl-tla checkout --detach FETCH_HEAD

# ======== Stable ComfyUI dependency tree ========
FROM python-base AS comfyui-deps

ARG COMFYUI_REPOSITORY
ARG COMFYUI_VERSION
ARG COMFYUI_FRONTEND_VERSION
ARG COMFYUI_WORKFLOW_TEMPLATES_VERSION
ARG COMFYUI_MANAGER_VERSION
ARG COMFY_KITCHEN_VERSION
ARG COMFY_AIMDO_VERSION
ARG COMFY_GGUF_REPOSITORY
ARG COMFY_GGUF_COMMIT
ARG COMFY_VHS_COMMIT
ARG COMFY_KJNODES_COMMIT
ARG COMFY_CONTROLNET_AUX_COMMIT
ARG COMFY_ESSENTIALS_COMMIT

# ComfyUI core and its Python dependencies are target-independent and stay
# ahead of the native-source branches for Docker cache reuse.
RUN --mount=type=cache,target=/root/.cache/pip \
    cd /llm && \
    git clone --filter=blob:none --branch "v${COMFYUI_VERSION}" --depth 1 \
        "${COMFYUI_REPOSITORY}" ComfyUI && \
    grep -q "\"${COMFYUI_VERSION}\"" /llm/ComfyUI/comfyui_version.py && \
    grep -Ev \
        '^(torch|torchvision|torchaudio)([[:space:]<>=!~].*)?$|^(comfyui-frontend-package|comfyui-workflow-templates|comfy-kitchen|comfy-aimdo)==' \
        /llm/ComfyUI/requirements.txt \
        > /tmp/comfyui-requirements.txt && \
    grep -qx \
        "comfyui_manager==${COMFYUI_MANAGER_VERSION}" \
        /llm/ComfyUI/manager_requirements.txt && \
    pip install \
        -r /tmp/comfyui-requirements.txt \
        "comfyui-frontend-package==${COMFYUI_FRONTEND_VERSION}" \
        "comfyui-workflow-templates==${COMFYUI_WORKFLOW_TEMPLATES_VERSION}" \
        "comfyui-manager==${COMFYUI_MANAGER_VERSION}" \
        "comfy-kitchen==${COMFY_KITCHEN_VERSION}" \
        "comfy-aimdo==${COMFY_AIMDO_VERSION}" && \
    pip check

# ComfyUI integrates Node Manager through the versioned Python package
# above. Do not also clone the legacy ComfyUI-Manager custom node: loading both
# creates two manager boundaries and makes missing-node behavior dependent on
# startup flags rather than the pinned package contract. Kitchen and AIMDO are
# removed from upstream requirements only so their accepted official versions
# can be installed explicitly above. The XPU implementations are installed as
# separately named providers and never overwrite these official packages.

# Pin every default custom node to an exact revision. These stable remote-
# source layers stay ahead of the frequently edited native sources, and the
# patched controlnet_aux node goes last so editing its patch invalidates
# nothing above it.

RUN --mount=type=cache,target=/root/.cache/pip \
    cd /llm/ComfyUI/custom_nodes && \
    git clone --filter=blob:none --no-checkout \
        https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git \
        comfyui-videohelpersuite && \
    git -C comfyui-videohelpersuite fetch --depth 1 origin \
        "${COMFY_VHS_COMMIT}" && \
    git -C comfyui-videohelpersuite checkout --detach FETCH_HEAD && \
    pip install -r comfyui-videohelpersuite/requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    cd /llm/ComfyUI/custom_nodes && \
    git clone --filter=blob:none --no-checkout \
        https://github.com/kijai/ComfyUI-KJNodes.git && \
    git -C ComfyUI-KJNodes fetch --depth 1 origin \
        "${COMFY_KJNODES_COMMIT}" && \
    git -C ComfyUI-KJNodes checkout --detach FETCH_HEAD && \
    pip install -r ComfyUI-KJNodes/requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    cd /llm/ComfyUI/custom_nodes && \
    git clone --filter=blob:none --no-checkout \
        https://github.com/cubiq/ComfyUI_essentials.git && \
    git -C ComfyUI_essentials fetch --depth 1 origin \
        "${COMFY_ESSENTIALS_COMMIT}" && \
    git -C ComfyUI_essentials checkout --detach FETCH_HEAD && \
    pip install -r ComfyUI_essentials/requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    cd /llm/ComfyUI/custom_nodes && \
    git clone --filter=blob:none --no-checkout \
        "${COMFY_GGUF_REPOSITORY}" ComfyUI-GGUF-XPU && \
    git -C ComfyUI-GGUF-XPU fetch --depth 1 origin \
        "${COMFY_GGUF_COMMIT}" && \
    git -C ComfyUI-GGUF-XPU checkout --detach FETCH_HEAD && \
    pip install -r ComfyUI-GGUF-XPU/requirements.txt

# Intel's XPU patch: depth-anything-v2 hardcodes DEVICE='cuda' or 'cpu'; the
# model would sit on the XPU device while dpt runs on CPU without it.
COPY --from=llm-scaler /llm-scaler/omni/patches/comfyui_controlnet_aux_depth_anything_v2_xpu.patch \
    /llm/patches/comfyui_controlnet_aux_depth_anything_v2_xpu.patch
RUN --mount=type=cache,target=/root/.cache/pip \
    cd /llm/ComfyUI/custom_nodes && \
    git clone --filter=blob:none --no-checkout \
        https://github.com/Fannovel16/comfyui_controlnet_aux.git && \
    git -C comfyui_controlnet_aux fetch --depth 1 origin \
        "${COMFY_CONTROLNET_AUX_COMMIT}" && \
    git -C comfyui_controlnet_aux checkout --detach FETCH_HEAD && \
    git -C comfyui_controlnet_aux apply --check \
        /llm/patches/comfyui_controlnet_aux_depth_anything_v2_xpu.patch && \
    git -C comfyui_controlnet_aux apply \
        /llm/patches/comfyui_controlnet_aux_depth_anything_v2_xpu.patch && \
    pip install -r comfyui_controlnet_aux/requirements.txt

# ======== Kitchen wheel branch ========
# Kitchen and the Omni kernel deliberately branch from separate cached parents.
# Updating either source/commit builds only that wheel, then reruns the cheap
# final installation/verification layer.
FROM python-base AS kitchen-wheel

ARG COMFY_KITCHEN_REPOSITORY
ARG COMFY_KITCHEN_COMMIT
ARG COMFY_KITCHEN_PROVIDER_VERSION
ARG TORCH_VERSION
ARG XPU_TARGET

RUN cd /llm && \
    git clone --filter=blob:none --no-checkout \
        "${COMFY_KITCHEN_REPOSITORY}" comfy-kitchen-xpu && \
    git -C comfy-kitchen-xpu fetch --depth 1 origin \
        "${COMFY_KITCHEN_COMMIT}" && \
    git -C comfy-kitchen-xpu checkout --detach FETCH_HEAD

RUN --mount=type=cache,target=/root/.cache/pip \
    cd /llm/comfy-kitchen-xpu && \
    mkdir -p /wheels/kitchen-source /wheels/kitchen-provider && \
    pip wheel . --wheel-dir /wheels/kitchen-source \
        --no-deps --no-build-isolation && \
    source_wheels=(/wheels/kitchen-source/comfy_kitchen-${COMFY_KITCHEN_PROVIDER_VERSION}-*.whl) && \
    test "${#source_wheels[@]}" -eq 1 && \
    python packaging/xpu_runtime_provider/build_wheel.py \
        --source-wheel "${source_wheels[0]}" \
        --output-dir /wheels/kitchen-provider \
        --source-revision "${COMFY_KITCHEN_COMMIT}" \
        --torch-version "${TORCH_VERSION}" \
        --xpu-target "${XPU_TARGET}"

# The wheel builder writes 0600; make the artifact world-readable so the
# sha256 verification in the runtime image works under the unprivileged user.
RUN chmod 0644 /wheels/kitchen-provider/*.whl

# ======== AIMDO XPU wheel branch ========
# The native-owner diagnostic stays off (Intel's AIMDO_XPU_BUILD_NATIVE_OWNER_
# DIAGNOSTIC=0 path): it replaces the allocator and adds a diagnostic interface,
# neither of which this deployment drives. DynamicVRAM weight staging and the
# public AIMDO APIs remain available without it.
FROM python-base AS aimdo-wheel

ARG COMFY_AIMDO_REPOSITORY
ARG COMFY_AIMDO_COMMIT
ARG COMFY_AIMDO_PROVIDER_VERSION
ARG TORCH_VERSION
ARG XPU_TARGET

RUN cd /llm && \
    git clone --filter=blob:none --no-checkout \
        "${COMFY_AIMDO_REPOSITORY}" comfy-aimdo-xpu && \
    git -C comfy-aimdo-xpu fetch --depth 1 origin \
        "${COMFY_AIMDO_COMMIT}" && \
    git -C comfy-aimdo-xpu checkout --detach FETCH_HEAD && \
    pip install setuptools-scm==10.2.1 && \
    source /opt/intel/oneapi/setvars.sh --force && \
    cd /llm/comfy-aimdo-xpu && \
    test -f /opt/venv/include/unified-runtime/ur_api.h && \
    UR_INCLUDE_DIR=/opt/venv/include/unified-runtime \
    AIMDO_XPU_BUILD_NATIVE_OWNER_DIAGNOSTIC=0 \
    AIMDO_TORCH_PYTHON=/opt/venv/bin/python \
        ./scripts/build-linux-xpu.sh && \
    mkdir -p /wheels/aimdo-source /wheels/aimdo-provider && \
    SETUPTOOLS_SCM_PRETEND_VERSION="${COMFY_AIMDO_PROVIDER_VERSION}" \
        pip wheel . --wheel-dir /wheels/aimdo-source \
            --no-deps --no-build-isolation && \
    source_wheels=(/wheels/aimdo-source/comfy_aimdo-${COMFY_AIMDO_PROVIDER_VERSION}-*.whl) && \
    test "${#source_wheels[@]}" -eq 1 && \
    python packaging/xpu_runtime_provider/build_wheel.py \
        --source-wheel "${source_wheels[0]}" \
        --output-dir /wheels/aimdo-provider \
        --source-revision "${COMFY_AIMDO_COMMIT}" \
        --torch-version "${TORCH_VERSION}" \
        --xpu-target "${XPU_TARGET}"

# ======== Omni kernel wheel branch ========
FROM sycl-tla AS kernel-wheel

ARG XPU_TARGET
ARG MAX_JOBS

ENV TORCH_XPU_ARCH_LIST=${XPU_TARGET} \
    OMNI_XPU_DEVICE=${XPU_TARGET} \
    MAX_JOBS=${MAX_JOBS} \
    CMAKE_BUILD_PARALLEL_LEVEL=${MAX_JOBS} \
    CUTLASS_SYCL_ROOT=/llm/sycl-tla \
    OMNI_XPU_REQUIRE_CUTE=1

COPY --link --from=llm-scaler /llm-scaler/omni/omni_xpu_kernel /llm/omni_xpu_kernel
RUN --mount=type=cache,target=/root/.cache/pip \
    set -eo pipefail && \
    source /opt/intel/oneapi/setvars.sh --force && \
    cd /llm/omni_xpu_kernel && \
    pip wheel -v . --wheel-dir /wheels --no-deps --no-build-isolation && \
    pip install --no-deps --force-reinstall \
        /wheels/omni_xpu_kernel-*.whl

# ======== ComfyUI runtime assembly ========
# The runtime is the completed assembly rather than a fresh os-base plus copies
# of /opt/venv and /llm: both use the same OMIX devel base, and copying the
# complete environment only creates very large replacement layers after each
# kernel/Kitchen edit and slows image export.
FROM comfyui-deps AS runtime

ARG BASE_IMAGE
ARG IMAGE_TAG
ARG XPU_TARGET
ARG MAX_JOBS
ARG TORCH_VERSION
ARG TORCHVISION_VERSION
ARG TORCHAUDIO_VERSION
ARG ONEDNN_VERSION
ARG ONEDNN_SOURCE_REPOSITORY
ARG ONEDNN_SOURCE_COMMIT
ARG ONEDNN_PATCH_SHA256
ARG SYCL_TLA_COMMIT
ARG COMFYUI_VERSION
ARG COMFYUI_FRONTEND_VERSION
ARG COMFYUI_WORKFLOW_TEMPLATES_VERSION
ARG COMFYUI_MANAGER_VERSION
ARG COMFY_KITCHEN_REPOSITORY
ARG COMFY_KITCHEN_COMMIT
ARG COMFY_KITCHEN_VERSION
ARG COMFY_KITCHEN_PROVIDER_VERSION
ARG COMFY_AIMDO_REPOSITORY
ARG COMFY_AIMDO_COMMIT
ARG COMFY_AIMDO_VERSION
ARG COMFY_AIMDO_PROVIDER_VERSION
ARG COMFY_GGUF_COMMIT
ARG COMFY_VHS_COMMIT
ARG COMFY_KJNODES_COMMIT
ARG COMFY_CONTROLNET_AUX_COMMIT
ARG COMFY_ESSENTIALS_COMMIT
ARG LLM_SCALER_REPOSITORY
ARG LLM_SCALER_COMMIT

ENV TORCH_XPU_ARCH_LIST=${XPU_TARGET} \
    OMNI_XPU_DEVICE=${XPU_TARGET} \
    MAX_JOBS=${MAX_JOBS} \
    CMAKE_BUILD_PARALLEL_LEVEL=${MAX_JOBS} \
    CUTLASS_SYCL_ROOT=/llm/sycl-tla \
    OMNI_XPU_REQUIRE_CUTE=1

COPY --from=sycl-tla /llm/sycl-tla /llm/sycl-tla
COPY --from=kernel-wheel /wheels/ /wheels/
COPY --from=kitchen-wheel /wheels/kitchen-provider/ /wheels/providers/
COPY --from=aimdo-wheel /wheels/aimdo-provider/ /wheels/providers/

# All third-party requirements, including official Kitchen and AIMDO, are
# already installed. Install the kernel and the two privately named XPU runtime
# providers without dependency resolution. The providers own no canonical
# comfy_kitchen or comfy_aimdo files, so later official upgrades are disjoint.
# Artifact and device acceptance belongs in the runtime test, where the check
# can run with the real /dev/dri device rather than a device-less build sandbox.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-deps --force-reinstall \
        /wheels/omni_xpu_kernel-*.whl \
        /wheels/providers/comfy_kitchen_xpu_runtime-${COMFY_KITCHEN_PROVIDER_VERSION}-*.whl \
        /wheels/providers/comfy_aimdo_xpu_runtime-${COMFY_AIMDO_PROVIDER_VERSION}-*.whl && \
    pip check

# The custom node is a thin adapter layer copied at the pinned llm-scaler
# commit; no git metadata is fabricated for it.
COPY --from=llm-scaler /llm-scaler/omni/ComfyUI-OmniXPU /llm/ComfyUI/custom_nodes/ComfyUI-OmniXPU

# Preserve the complete installed dependency snapshot used by image
# validation. This records transitive ComfyUI and custom-node packages in
# addition to the explicitly versioned frontend/templates/manager boundary.
RUN mkdir -p /llm/manifests && \
    sha256sum /wheels/providers/*.whl \
        > /llm/manifests/xpu-runtime-providers.sha256 && \
    pip freeze --all | LC_ALL=C sort \
        > /llm/manifests/comfyui-python-freeze.txt && \
    pip list --format=freeze | grep -Ei \
        '^(torch|torchvision|torchaudio|omni[-_]xpu[-_]kernel|comfy-kitchen-xpu-runtime|comfy-aimdo-xpu-runtime)==' \
        | LC_ALL=C sort \
        > /llm/manifests/omni-runtime-constraints.txt && \
    test "$(wc -l < /llm/manifests/omni-runtime-constraints.txt)" -eq 6 && \
    rm -rf /wheels

COPY --from=llm-scaler /llm-scaler/omni/patches /llm/patches
COPY --from=llm-scaler /llm-scaler/omni/tools /llm/tools
COPY --from=llm-scaler /llm-scaler/omni/configs/comfyui_host_models.yaml /llm/configs/comfyui_host_models.yaml

# The image runs as nobody (repo standard): the runtime writes only under the
# mounted /data dirs and /llm/ComfyUI/user, and PYTHONDONTWRITEBYTECODE keeps
# imports from writing __pycache__ into the root-owned ComfyUI tree.
RUN mkdir -p /llm/ComfyUI/user /llm/ComfyUI/input /llm/ComfyUI/output /llm/ComfyUI/temp /llm/ComfyUI/models /models/host /data/input /data/output /data/user && \
    chown -R 65534:65534 /data /models /llm/ComfyUI/user /llm/ComfyUI/input /llm/ComfyUI/output /llm/ComfyUI/temp /llm/ComfyUI/models && \
    chown -R 65534:65534 /opt/venv /llm/ComfyUI/custom_nodes

# Intel's start_comfyui.sh additionally sets no_proxy defaults, a
# --reserve-vram budget, and the DynamicVRAM flag logic wired to the AIMDO
# native allocator preload (runtime_bootstrap.py --allocator-preload-path /
# LD_PRELOAD native_hook): all dropped with the native-owner diagnostic, and
# any of it can be passed per-deployment through CLI_ARGS instead.
COPY --chmod=755 <<'ENTRYPOINT_EOF' /llm/entrypoints/start_comfyui.sh
#!/usr/bin/env bash
# Establish the same runtime environment intel/llm-scaler's
# omix_torch_runtime.sh sets: source the OMIX oneAPI environment, then restore
# the venv's Torch-matched SYCL/UR runtime ahead of the OMIX 2026.1 build
# toolchain. Without this reorder the inherited OMIX environment mixes libsycl
# from the Torch wheel with libur_loader from the compiler image.
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
    --temp-directory /data/temp \
    --enable-manager \
    ${CLI_ARGS:-} "$@"
ENTRYPOINT_EOF

# com.intel.omni.* keys keep Intel's label names for the pinned revisions so
# tools written against the upstream image (omni/tools/validate_comfyui_*.py)
# can read them; com.joryirving.* covers what this fork adds or replaces.
LABEL org.opencontainers.image.version="${IMAGE_TAG}" \
      org.opencontainers.image.base.name="${BASE_IMAGE}" \
      com.intel.omni.image-flavor="comfyui" \
      com.intel.omni.base-image="${BASE_IMAGE}" \
      com.intel.omni.torch.version="${TORCH_VERSION}" \
      com.intel.omni.torchvision.version="${TORCHVISION_VERSION}" \
      com.intel.omni.torchaudio.version="${TORCHAUDIO_VERSION}" \
      com.intel.omni.onednn.package.version="${ONEDNN_VERSION}" \
      com.intel.omni.onednn.source.repository="${ONEDNN_SOURCE_REPOSITORY}" \
      com.intel.omni.onednn.source.revision="${ONEDNN_SOURCE_COMMIT}" \
      com.intel.omni.onednn.patch.sha256="${ONEDNN_PATCH_SHA256}" \
      com.intel.omni.xpu-target="${XPU_TARGET}" \
      com.intel.omni.sycl-tla.revision="${SYCL_TLA_COMMIT}" \
      com.intel.omni.comfyui.version="${COMFYUI_VERSION}" \
      com.intel.omni.comfyui.frontend.version="${COMFYUI_FRONTEND_VERSION}" \
      com.intel.omni.comfyui.workflow-templates.version="${COMFYUI_WORKFLOW_TEMPLATES_VERSION}" \
      com.intel.omni.comfyui.manager.version="${COMFYUI_MANAGER_VERSION}" \
      com.intel.omni.comfy-kitchen.version="${COMFY_KITCHEN_VERSION}" \
      com.intel.omni.comfy-aimdo.version="${COMFY_AIMDO_VERSION}" \
      com.intel.omni.comfy-kitchen-xpu-runtime.repository="${COMFY_KITCHEN_REPOSITORY}" \
      com.intel.omni.comfy-kitchen-xpu-runtime.version="${COMFY_KITCHEN_PROVIDER_VERSION}" \
      com.intel.omni.comfy-kitchen-xpu-runtime.revision="${COMFY_KITCHEN_COMMIT}" \
      com.intel.omni.comfy-aimdo-xpu-runtime.repository="${COMFY_AIMDO_REPOSITORY}" \
      com.intel.omni.comfy-aimdo-xpu-runtime.version="${COMFY_AIMDO_PROVIDER_VERSION}" \
      com.intel.omni.comfy-aimdo-xpu-runtime.revision="${COMFY_AIMDO_COMMIT}" \
      com.intel.omni.comfy-gguf.revision="${COMFY_GGUF_COMMIT}" \
      com.joryirving.llm-scaler.repository="${LLM_SCALER_REPOSITORY}" \
      com.joryirving.llm-scaler.revision="${LLM_SCALER_COMMIT}" \
      com.joryirving.comfyui-videohelpersuite.revision="${COMFY_VHS_COMMIT}" \
      com.joryirving.comfyui-kjnodes.revision="${COMFY_KJNODES_COMMIT}" \
      com.joryirving.comfyui-controlnet-aux.revision="${COMFY_CONTROLNET_AUX_COMMIT}" \
      com.joryirving.comfyui-essentials.revision="${COMFY_ESSENTIALS_COMMIT}"

ENV OMNIXPU_INTERPOLATE_FIX=0 \
    OMNIXPU_H3_TE_INT8_CR=1 \
    UR_INCLUDE_DIR="/opt/venv/include/unified-runtime" \
    PIP_CONSTRAINT="/llm/manifests/omni-runtime-constraints.txt" \
    PYTHONDONTWRITEBYTECODE=1

# Keep the OMIX oneAPI environment initialization, then restore the venv's
# Torch-matched SYCL/UR runtime ahead of the OMIX 2026.1 build toolchain.
ENTRYPOINT ["/llm/entrypoints/start_comfyui.sh"]

USER 65534:65534

# nobody's passwd HOME is /nonexistent; give HF/torch/node caches a writable
# home so runtime model downloads work.
ENV HOME=/tmp \
    TMPDIR=/tmp

WORKDIR /llm/ComfyUI
