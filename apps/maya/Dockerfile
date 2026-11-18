# syntax=docker/dockerfile:1
# Project Maya GLM-5.3-Flash only. Source commit and llama.cpp pin are fixed below.
FROM nvidia/cuda:13.0.0-devel-ubuntu24.04@sha256:1e8ac7a54c184a1af8ef2167f28fa98281892a835c981ebcddb1fad04bdd452d AS build
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates ccache cmake curl git ninja-build python3 unzip \
    && rm -rf /var/lib/apt/lists/*
ENV CCACHE_DIR=/root/.cache/ccache CCACHE_MAXSIZE=30G CCACHE_COMPILERCHECK=content
ARG MAYA_COMMIT=81b68a6c1da6aebeecf83f6f9ca33878258ef968
ARG CUDA_ARCHITECTURES=86
ARG VERSION
RUN test "${#MAYA_COMMIT}" -eq 40 \
    && curl -fsSL "https://github.com/mw00/project-Maya/archive/${MAYA_COMMIT}.zip" -o /tmp/maya.zip \
    && unzip -q /tmp/maya.zip -d /tmp \
    && mv "/tmp/project-maya-${MAYA_COMMIT}" /src \
    && rm /tmp/maya.zip \
    && test "$(tr -d '[:space:]' < /src/VERSION)" = "$VERSION"
RUN LLAMA_CPP_COMMIT="$(sed -n 's/^LLAMA_CPP_COMMIT *= *\"\([0-9a-f]*\)\"/\1/p' /src/setup.py | head -1)" \
    && test "${#LLAMA_CPP_COMMIT}" -eq 40 \
    && curl -fsSL "https://github.com/ggml-org/llama.cpp/archive/${LLAMA_CPP_COMMIT}.zip" -o /tmp/llama.zip \
    && unzip -q /tmp/llama.zip -d /tmp \
    && mv "/tmp/llama.cpp-${LLAMA_CPP_COMMIT}" /llama.cpp \
    && rm /tmp/llama.zip
RUN cmake -S /src -B /build -G Ninja -DCMAKE_BUILD_TYPE=Release \
        -DSTRATA_ENABLE_CUDA=ON "-DCMAKE_CUDA_ARCHITECTURES=${CUDA_ARCHITECTURES}" \
        -DSTRATA_NATIVE_EXPERTS=ON -DSTRATA_BUILD_TESTS=OFF -DSTRATA_PORTABLE=ON \
        -DSTRATA_GGML_DIR=/llama.cpp \
        -DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache -DCMAKE_CUDA_COMPILER_LAUNCHER=ccache
RUN --mount=type=cache,id=project-maya-ccache,target=/root/.cache/ccache \
    cmake --build /build --target maya -j "$(( ($(nproc) / 2) > 0 ? ($(nproc) / 2) : 1 ))"
RUN mkdir -p /out/bin && cp /build/maya /out/bin/maya \
    && grep -E '^(STRATA_PORTABLE|GGML_NATIVE|GGML_AVX[A-Z0-9_]*|GGML_FMA|GGML_F16C|GGML_BMI2|GGML_AMX_[A-Z0-9_]*):' /build/CMakeCache.txt > /out/cpu-flags.txt \
    && sed -n 's/^CMAKE_CUDA_ARCHITECTURES:[A-Z]*=//p' /build/CMakeCache.txt > /out/cuda-architectures.txt

FROM nvidia/cuda:13.0.0-runtime-ubuntu24.04@sha256:95318efecfd68ab3d109da5277863257b06137c84f34a87f38de970d5cd035d3
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 LANG=C.UTF-8 MAYA_UPDATE_CHECK=0
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*
ARG MAYA_COMMIT=81b68a6c1da6aebeecf83f6f9ca33878258ef968
ARG CUDA_ARCHITECTURES=86
ARG VERSION
LABEL org.opencontainers.image.title="Project Maya GLM-5.3-Flash" \
      org.opencontainers.image.description="Project Maya ${VERSION}, CUDA 13, sm_86" \
      org.opencontainers.image.source="https://github.com/mw00/project-Maya" \
      org.opencontainers.image.revision="${MAYA_COMMIT}" \
      com.joryirving.maya.cuda-architectures="${CUDA_ARCHITECTURES}" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.licenses="MIT"
COPY --from=build /src /opt/maya
RUN test "$(tr -d '[:space:]' < /opt/maya/VERSION)" = "$VERSION"
RUN rm -rf /opt/maya/.git /opt/maya/tests /opt/maya/bench /opt/maya/ref /opt/maya/third_party/wheels /opt/maya/data/glm5-*-dumps*
COPY --from=build /llama.cpp/gguf-py /opt/maya/third_party/llama.cpp/gguf-py
RUN mkdir -p /opt/maya/image && python3 - > /opt/maya/image/py-packages.txt <<'PY'
import ast, re
with open("/opt/maya/setup.py", encoding="utf-8") as f:
    tree = ast.parse(f.read())
found = [n.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
         and any(isinstance(t, ast.Name) and t.id == "PY_PACKAGES" for t in n.targets)]
assert len(found) == 1
packages = [p for p in ast.literal_eval(found[0])
            if re.split(r"[<>=!~;\[ ]", p, maxsplit=1)[0].lower() not in ("cmake", "ninja")]
assert "numpy" in packages
print("\n".join(packages))
PY
RUN python3 -m venv /opt/maya/.venv \
    && /opt/maya/.venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/maya/.venv/bin/pip install --no-cache-dir -r /opt/maya/image/py-packages.txt \
    && /opt/maya/.venv/bin/pip freeze > /opt/maya/image/pip-freeze.txt
COPY --from=build /out/bin/maya /opt/maya/build/maya
COPY --from=build /out/cpu-flags.txt /out/cuda-architectures.txt /opt/maya/image/
WORKDIR /opt/maya
USER 65534:65534
CMD ["/opt/maya/.venv/bin/python", "/opt/maya/serve/server.py", "--help"]
