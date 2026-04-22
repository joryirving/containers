# syntax=docker/dockerfile:1

ARG TURBOQUANT_SOURCE=paudley/llama.cpp
ARG TURBOQUANT_REF=b8eda0cc7033dc62ad876dc29c965844928aaf36

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:vulkan-radv@sha256:13f37769216036bf04a91bc8650fa64f64e3e9c7cd8d23b160567bf2b87494f7 AS builder

ARG TURBOQUANT_SOURCE
ARG TURBOQUANT_REF

RUN dnf install -y --setopt=install_weak_deps=False \
    git cmake make ninja-build gcc-c++ binutils lld clang clang-devel compiler-rt libcurl-devel \
    vulkan-loader-devel vulkan-tools mesa-vulkan-drivers spirv-headers-devel radeontop glslc patch procps-ng && \
    dnf clean all && \
    ln -sf /usr/bin/ld.bfd /etc/alternatives/ld && \
    ln -sf /etc/alternatives/ld /usr/bin/ld

WORKDIR /opt/llama.cpp

RUN git clone https://github.com/${TURBOQUANT_SOURCE}.git . && \
    git fetch origin "${TURBOQUANT_REF}" && \
    git checkout "${TURBOQUANT_REF}"

RUN git clean -xdf \
    && git submodule update --recursive \
    && cmake -S . -B build -G Ninja \
        -DGGML_VULKAN=ON \
        -DGGML_RPC=ON \
        -DCMAKE_BUILD_TYPE=Release \
        -DLLAMA_BUILD_TESTS=OFF \
        -DLLAMA_BUILD_EXAMPLES=ON \
        -DLLAMA_BUILD_SERVER=ON \
    && cmake --build build --config Release --target llama-server \
    && mkdir -p /out/bin /out/lib \
    && cp build/bin/llama-server /out/bin/ \
    && cp build/bin/libllama.so* build/bin/libggml*.so* /out/lib/ \
    && (find /out -type f -exec strip {} \; 2>/dev/null || true)

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:vulkan-radv@sha256:13f37769216036bf04a91bc8650fa64f64e3e9c7cd8d23b160567bf2b87494f7

COPY --from=builder /out/bin/llama-server /usr/bin/llama-server
COPY --from=builder /out/lib /usr/lib64

USER 65534:65534

EXPOSE 8080

CMD ["llama-server"]
