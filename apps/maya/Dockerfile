# syntax=docker/dockerfile:1
# Project Maya GLM-5.3-Flash only: the maya engine and the maya-vision encoder. Source version comes from the
# upstream release tag; the llama.cpp pin comes from upstream setup.py.
FROM nvidia/cuda:13.5.0-devel-ubuntu24.04@sha256:d3fa71793540a2b76ab227ee00016e754da2758b7a51b49bc8a72543af5a8bc2 AS build
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates ccache cmake curl git ninja-build python3 unzip \
    && rm -rf /var/lib/apt/lists/*
ENV CCACHE_DIR=/root/.cache/ccache CCACHE_MAXSIZE=30G CCACHE_COMPILERCHECK=content
ARG CUDA_ARCHITECTURES=86
ARG VERSION
RUN test -n "${VERSION}" \
    && mkdir -p /src \
    && curl -fsSL "https://github.com/mw00/project-Maya/archive/refs/tags/v${VERSION}.tar.gz" \
        | tar xzf - -C /src --strip-components=1 \
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
# The vision encoder, the way maya.py's compile_vision builds it: glm5next_patch.py adds GLM-5.3-Flash's vision
# tower to the pinned llama.cpp's mtmd (idempotent, anchors fail the build on drift; its ggml-cuda edits are
# guarded by MAYA_VISION_F32_SUMS, and the engine above was compiled before the patch). -B: no bytecode under
# tools/vision, which upstream's setup source_hash hashes.
RUN python3 -B /src/tools/vision/glm5next_patch.py /llama.cpp
RUN cmake -S /src/tools/vision -B /build-vision -G Ninja -DCMAKE_BUILD_TYPE=Release \
        -DLLAMA_DIR=/llama.cpp -DSTRATA_VISION_CUDA=ON -DSTRATA_PORTABLE=ON \
        "-DCMAKE_CUDA_ARCHITECTURES=${CUDA_ARCHITECTURES}" \
        -DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache -DCMAKE_CUDA_COMPILER_LAUNCHER=ccache
RUN --mount=type=cache,id=project-maya-ccache,target=/root/.cache/ccache \
    cmake --build /build-vision --target maya-vision -j "$(( ($(nproc) / 2) > 0 ? ($(nproc) / 2) : 1 ))"
RUN cp /build-vision/bin/maya-vision /out/bin/maya-vision \
    && grep -E '^(STRATA_PORTABLE|GGML_NATIVE|GGML_AVX[A-Z0-9_]*|GGML_FMA|GGML_F16C|GGML_BMI2|GGML_AMX_[A-Z0-9_]*):' /build-vision/CMakeCache.txt > /out/vision-cpu-flags.txt \
    && sed -n 's/^CMAKE_CUDA_ARCHITECTURES:[A-Z]*=//p' /build-vision/CMakeCache.txt > /out/vision-cuda-architectures.txt

FROM nvidia/cuda:13.5.0-runtime-ubuntu24.04@sha256:ba4d4e8475ced890fb26f9661daf8dae7cce9827613682eb8b8379c5ecd94eba
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 LANG=C.UTF-8 MAYA_UPDATE_CHECK=0
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*
ARG CUDA_ARCHITECTURES=86
ARG VERSION
LABEL org.opencontainers.image.title="Project Maya GLM-5.3-Flash" \
      org.opencontainers.image.description="Project Maya ${VERSION}, CUDA 13, sm_86" \
      org.opencontainers.image.source="https://github.com/mw00/project-Maya" \
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
COPY --from=build /out/bin/maya-vision /opt/maya/build-vision/bin/maya-vision
COPY --from=build /out/cpu-flags.txt /out/cuda-architectures.txt /opt/maya/image/
COPY --from=build /out/vision-cpu-flags.txt /out/vision-cuda-architectures.txt /opt/maya/image/
# The stamp upstream's setup reads before it would compile the encoder (maya.py's vision_step): src is setup.py's
# own source_hash over tools/vision at the pinned llama.cpp, computed from this image's final tree, so setup
# accepts the prebuilt binary and only downloads the encoder's mmproj/vocab files. archs are ints (pc["archs"]).
RUN test -x /opt/maya/build-vision/bin/maya-vision && python3 -B - /opt/maya "${CUDA_ARCHITECTURES}" <<'PY'
import json, pathlib, sys, time
root, archs = pathlib.Path(sys.argv[1]), [int(x) for x in sys.argv[2].split(";") if x]
sys.path.insert(0, str(root))
import setup
src = setup.source_hash(("tools/vision",))
assert len(src) == 16, src
stamp = root / "build-vision" / "MAYA-BUILD.json"
stamp.parent.mkdir(parents=True, exist_ok=True)
stamp.write_text(json.dumps({"src": src, "archs": archs, "llama": str(root / "third_party" / "llama.cpp"),
                             "backend": "cuda", "date": time.strftime("%Y-%m-%d %H:%M")}, indent=1) + "\n",
                 encoding="utf-8")
PY
WORKDIR /opt/maya
USER 65534:65534
CMD ["/opt/maya/.venv/bin/python", "/opt/maya/serve/server.py", "--help"]
