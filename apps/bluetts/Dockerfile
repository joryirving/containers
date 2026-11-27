# syntax=docker/dockerfile:1

ARG TARGETARCH

FROM docker.io/library/python:3.12-slim@sha256:191083cdf6c7bda8c76158983163ead5d5cf7b77cf3033e805bb0f5296f51b4b AS build

ENV DEBIAN_FRONTEND=noninteractive \
    UV_LINK_MODE=copy

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl patch \
    && rm -rf /var/lib/apt/lists/*

# Pin uv for reproducible builds (bump manually; renovate does not track this pin)
COPY --from=ghcr.io/astral-sh/uv:0.13.10@sha256:a3ea1357342c1a4bf9a0c53a3deb1b55379aefa037338d8113d5771efa01774f /uv /usr/local/bin/uv

# Keep downloaded source and dependencies separate from the Vulkan runtime.
FROM build AS app-build

WORKDIR /app

ARG VERSION
# BlueV3 ONNX bundle revision on huggingface.co/notmax123/BlueV3-onnx; voice JSONs in
# voices-custom/ were exported against this bundle and only load with it.
ARG BLUEV3_REVISION

RUN test -n "${VERSION}" \
    && curl -fsSL "https://github.com/maxmelichov/BlueTTS/archive/refs/tags/V${VERSION}.tar.gz" \
        | tar xzf - -C /app --strip-components=1

COPY openai_server.patch /tmp/openai_server.patch
COPY openvino.patch /tmp/openvino.patch
COPY reference-audio.patch /tmp/reference-audio.patch
COPY webgpu_device.py /app/src/blue_onnx/webgpu_device.py
RUN patch examples/openai_server.py /tmp/openai_server.patch \
    && grep -q BLUE_STEPS examples/openai_server.py \
    && patch src/blue_onnx/style.py /tmp/reference-audio.patch \
    && grep -q _bluev3_reference src/blue_onnx/style.py \
    && patch src/blue_onnx/__init__.py /tmp/openvino.patch \
    && grep -q BLUE_OV_DEVICE src/blue_onnx/__init__.py \
    && grep -q BLUE_WEBGPU_ADAPTER src/blue_onnx/__init__.py

RUN uv sync --frozen --no-dev --no-install-project --extra server

FROM app-build AS runtime-build

USER root
ARG TARGETARCH
RUN case "${TARGETARCH}" in \
        amd64) curl -fsSL "https://files.pythonhosted.org/packages/98/57/656e7b4071d754674fc9f749bcd9dc0229efc685b084ca71932a34d7cad4/onnxruntime_ep_webgpu-0.6.0-py3-none-manylinux_2_28_x86_64.whl" \
                -o /tmp/onnxruntime_ep_webgpu-0.6.0-py3-none-manylinux_2_28_x86_64.whl \
            && echo "791d991f2779ae23cdd273d4689413e798080cfa4b736012ec53da8cd14a7c79  /tmp/onnxruntime_ep_webgpu-0.6.0-py3-none-manylinux_2_28_x86_64.whl" | sha256sum -c - \
            && uv pip install --python .venv/bin/python --no-index /tmp/onnxruntime_ep_webgpu-0.6.0-py3-none-manylinux_2_28_x86_64.whl \
            && rm /tmp/onnxruntime_ep_webgpu-0.6.0-py3-none-manylinux_2_28_x86_64.whl ;; \
        arm64) : ;; \
        *) echo "unsupported arch ${TARGETARCH}" && exit 1 ;; \
    esac

RUN case "${TARGETARCH}" in \
        amd64) curl -fsSL "https://files.pythonhosted.org/packages/88/01/4e72a8a65b584f01d6e59eb453bae397b82b2e51df1b5c94efa05e17800b/onnxruntime_ep_openvino-1.8.1-py3-none-manylinux_2_28_x86_64.whl" \
                -o /tmp/onnxruntime_ep_openvino-1.8.1-py3-none-manylinux_2_28_x86_64.whl \
            && echo "3832643158c8c187fcab6db661cde2a8c06a2b3559d95d0f2411ac0e51c5e924  /tmp/onnxruntime_ep_openvino-1.8.1-py3-none-manylinux_2_28_x86_64.whl" | sha256sum -c - \
            && uv pip install --python .venv/bin/python --no-index /tmp/onnxruntime_ep_openvino-1.8.1-py3-none-manylinux_2_28_x86_64.whl \
            && rm /tmp/onnxruntime_ep_openvino-1.8.1-py3-none-manylinux_2_28_x86_64.whl ;; \
        arm64) : ;; \
        *) echo "unsupported arch ${TARGETARCH}" && exit 1 ;; \
    esac

# The English bundle needs polyg2p. Upstream has no linux/arm64 wheel, so
# arm64 images build but cannot synthesize English.
RUN case "${TARGETARCH}" in \
        amd64) WHEEL=manylinux_2_34_x86_64 ;; \
        arm64) WHEEL="" ;; \
        *) echo "unsupported arch ${TARGETARCH}" && exit 1 ;; \
    esac \
    && if [ -n "${WHEEL}" ]; then \
        curl -fsSL "https://huggingface.co/notmax123/BlueV3-onnx/resolve/${BLUEV3_REVISION}/frontend/polyg2p-0.1.0-cp39-abi3-${WHEEL}.whl" \
            -o "/tmp/polyg2p-0.1.0-cp39-abi3-${WHEEL}.whl" \
        && echo "c32261120e83ed4d84cef433ae8bbb4cdab40e6e835eeea6483a0423c5193e37  /tmp/polyg2p-0.1.0-cp39-abi3-${WHEEL}.whl" | sha256sum -c - \
        && uv pip install --python .venv/bin/python --no-index "/tmp/polyg2p-0.1.0-cp39-abi3-${WHEEL}.whl" \
        && rm "/tmp/polyg2p-0.1.0-cp39-abi3-${WHEEL}.whl"; \
    fi

# The image includes the English model and G2P files, but not Hebrew or Yiddish data.
# These hashes are the LFS object IDs for BLUEV3_REVISION.
RUN mkdir -p bluev3_onnx/onnx bluev3_onnx/frontend/polyg2p_data \
    && : > /tmp/bundle.sha256 \
    && echo "46197a2c10f06e151adc6dd109082889e6aaf903c46ce25d798eebaa7b07e313  bluev3_onnx/onnx/duration_predictor_style.onnx" >> /tmp/bundle.sha256 \
    && echo "11c0ddffa7187dd01aebf2099e2da8d32d2176bcddfd4b3b42c1f55f7cc32812  bluev3_onnx/onnx/reference_encoder.onnx" >> /tmp/bundle.sha256 \
    && echo "22a0352b4e4bb60dd4c4a45788006150a097fb5cfc84313093a95ed43ecbffe9  bluev3_onnx/onnx/stats.npz" >> /tmp/bundle.sha256 \
    && echo "9dd84651a48048dce980d9d54c11fd3c04170602fb4f9e66957c08eeee2e55ba  bluev3_onnx/onnx/text_encoder.onnx" >> /tmp/bundle.sha256 \
    && echo "54995402c6c88d93d54fbd8b48096dd675dff8c8d3e6112cede33f4d90047a71  bluev3_onnx/onnx/uncond.npz" >> /tmp/bundle.sha256 \
    && echo "2f0e4af007f166afdc020331b863b1ea6b93c29258ae3b649f81234c1d7ad7c1  bluev3_onnx/onnx/vector_estimator.onnx" >> /tmp/bundle.sha256 \
    && echo "054a700e9ef17d43de203212dca335fa2cd000cd9ca7701df49fcc544b49ccbe  bluev3_onnx/onnx/vocoder.onnx" >> /tmp/bundle.sha256 \
    && while read -r _sha _path; do \
        curl -fsSL "https://huggingface.co/notmax123/BlueV3-onnx/resolve/${BLUEV3_REVISION}/${_path#bluev3_onnx/}" -o "${_path}"; \
    done < /tmp/bundle.sha256 \
    && curl -fsSL "https://huggingface.co/notmax123/BlueV3-onnx/resolve/${BLUEV3_REVISION}/onnx/export_check.json" -o bluev3_onnx/onnx/export_check.json \
    && curl -fsSL "https://huggingface.co/notmax123/BlueV3-onnx/resolve/${BLUEV3_REVISION}/onnx/tts.json" -o bluev3_onnx/onnx/tts.json \
    && curl -fsSL "https://huggingface.co/notmax123/BlueV3-onnx/resolve/${BLUEV3_REVISION}/onnx/vocab.json" -o bluev3_onnx/onnx/vocab.json \
    && for f in en.lex en-large.g2p en.g2p LICENSE NOTICE; do \
        curl -fsSL "https://huggingface.co/notmax123/BlueV3-onnx/resolve/${BLUEV3_REVISION}/frontend/polyg2p_data/${f}" -o "bluev3_onnx/frontend/polyg2p_data/${f}"; \
    done \
    && sha256sum -c /tmp/bundle.sha256 \
    && rm /tmp/bundle.sha256

# OpenVINO GPU needs the Intel OpenCL runtime from the pinned OVMS GPU image.
FROM --platform=linux/amd64 openvino/model_server:2026.4.1-gpu@sha256:a928903fe429f1e3e27107cc45932d30d95febfd2d1159dc50869c3eac76fc58 AS intel-opencl-amd64
FROM scratch AS intel-opencl-arm64
COPY intel-opencl-arm64/ /
FROM intel-opencl-${TARGETARCH} AS intel-opencl

FROM ghcr.io/ggml-org/llama.cpp:server-vulkan@sha256:3d21475ecd4383a9649ea21737d07044399d0995490b5ce5c6d89326dc7c7771 AS runtime-base

COPY --from=runtime-build /usr/local/bin/python3.12 /usr/local/bin/python3.12
COPY --from=runtime-build /usr/local/lib/libpython3.12.so* /usr/local/lib/
COPY --from=runtime-build /usr/local/lib/python3.12 /usr/local/lib/python3.12
RUN apt-get update && apt-get install -y --no-install-recommends \
        espeak-ng ffmpeg libsndfile1 curl libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=intel-opencl /etc/OpenCL/vendors /etc/OpenCL/vendors
COPY --from=intel-opencl /usr/lib/x86_64-linux-gnu/intel-opencl /usr/lib/x86_64-linux-gnu/intel-opencl
COPY --from=intel-opencl /usr/lib/x86_64-linux-gnu/libigdgmm.so.12* /usr/lib/x86_64-linux-gnu/
COPY --from=intel-opencl /usr/local/lib/ /usr/local/lib/

COPY --from=runtime-build --chown=65534:65534 /app /app
COPY --chown=65534:65534 voices-custom/ /app/voices-custom/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/tmp \
    TMPDIR=/tmp \
    ORT_DISABLE_CPU_AFFINITY=1 \
    ORT_INTRA=4 \
    ORT_INTER=1 \
    BLUE_STEPS=16 \
    BLUE_CFG=4.0 \
    BLUE_PACE_BLEND=0.5 \
    BLUE_PACE_REF=0.0625

USER 65534:65534
WORKDIR /app
EXPOSE 8000
HEALTHCHECK CMD curl -sf http://127.0.0.1:8000/health || exit 1

ENTRYPOINT ["/app/.venv/bin/python", "-u", "examples/openai_server.py", \
    "--bundle", "bluev3_onnx", "--voices-dir", "voices-custom", \
    "--default-voice", "mia", \
    "--host", "0.0.0.0", "--port", "8000"]
