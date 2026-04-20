# syntax=docker/dockerfile:1

ARG TURBOQUANT_SOURCE=unixsysdev/llama-turboquant
ARG TURBOQUANT_REF=03fa8abc4708dfc13858de0a74695075702c8e26

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-6.4.4@sha256:957974b729f458ab34f33104e795216a79b347803aff18247355c5a1d61efe43 AS builder

ARG TURBOQUANT_SOURCE
ARG TURBOQUANT_REF

RUN dnf install -y --setopt=install_weak_deps=False procps-ng && dnf clean all

WORKDIR /build

RUN git clone https://github.com/${TURBOQUANT_SOURCE}.git . && \
    git fetch origin "${TURBOQUANT_REF}" && \
    git checkout "${TURBOQUANT_REF}"

RUN cmake -B build -DGGML_HIP=ON -DGGML_HIP_ROCWMMA=ON -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build --config Release --target llama-server -j "$(nproc)" \
    && mkdir -p /out \
    && cp build/bin/llama-server /out/ \
    && find /out -type f -exec strip {} \; 2>/dev/null || true

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-6.4.4@sha256:957974b729f458ab34f33104e795216a79b347803aff18247355c5a1d61efe43

COPY --from=builder /out/llama-server /usr/local/bin/llama-server

USER nobody:nobody

EXPOSE 8080

CMD ["llama-server"]
