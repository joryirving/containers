# syntax=docker/dockerfile:1

ARG TURBOQUANT_SOURCE=unixsysdev/llama-turboquant
ARG TURBOQUANT_REF=main

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-7.2@sha256:c246a5557e42d1375111160f43fbaa8519d9bf7e3308a87edc76f2d740fabf7c AS builder

ARG TURBOQUANT_SOURCE
ARG TURBOQUANT_REF

WORKDIR /build

RUN git clone https://github.com/${TURBOQUANT_SOURCE}.git . && \
    git fetch origin "${TURBOQUANT_REF}" && \
    git checkout "${TURBOQUANT_REF}"

RUN cmake -B build -DGGML_HIP=ON -DGGML_HIP_ROCWMMA=ON -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build --config Release --target llama-server -j "$(nproc)" \
    && mkdir -p /out \
    && cp build/bin/llama-server /out/ \
    && find /out -type f -exec strip {} \; 2>/dev/null || true

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-7.2@sha256:c246a5557e42d1375111160f43fbaa8519d9bf7e3308a87edc76f2d740fabf7c

COPY --from=builder /out/llama-server /usr/local/bin/llama-server

USER nobody:nogroup

EXPOSE 8080

CMD ["llama-server"]
