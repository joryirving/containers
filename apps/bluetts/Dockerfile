# syntax=docker/dockerfile:1

FROM docker.io/library/python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b AS build

ENV DEBIAN_FRONTEND=noninteractive \
    UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl patch \
    && rm -rf /var/lib/apt/lists/*

# Pin uv for reproducible builds (bump manually; renovate does not track this pin)
COPY --from=ghcr.io/astral-sh/uv:0.11.6@sha256:b1e699368d24c57cda93c338a57a8c5a119009ba809305cc8e86986d4a006754 /uv /usr/local/bin/uv

WORKDIR /app

ARG VERSION
# Source pin: the tuning-tested commit (see SOURCE_SHA in docker-bake.hcl);
# VERSION only drives the semver image tags.
ARG SOURCE_SHA
# BlueV3 ONNX bundle revision on huggingface.co/notmax123/BlueV3-onnx; voice JSONs in
# voices-custom/ were exported against this bundle and only load with it.
ARG BLUEV3_REVISION

RUN test "${#SOURCE_SHA}" -eq 40 \
    && curl -fsSL "https://github.com/maxmelichov/BlueTTS/archive/${SOURCE_SHA}.tar.gz" \
        | tar xzf - -C /app --strip-components=1

COPY openai_server.patch /tmp/openai_server.patch
RUN patch examples/openai_server.py /tmp/openai_server.patch \
    && grep -q BLUE_STEPS examples/openai_server.py

RUN uv sync --frozen --no-dev --no-install-project --extra server

# English-only ONNX bundle: model weights + the English G2P data (the Hebrew and
# Yiddish frontends are on-demand downloads upstream and are deliberately excluded).
# sha256s are the LFS oids published for BLUEV3_REVISION on the hub.
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

FROM docker.io/library/python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b

RUN apt-get update && apt-get install -y --no-install-recommends \
        espeak-ng ffmpeg libsndfile1 curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build --chown=65534:65534 /app /app
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
