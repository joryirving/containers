package main

import (
	"os"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	if os.Getenv("TEST_IMAGE") == "" {
		t.Skip("TEST_IMAGE is set by the CI image test workflow")
	}
	image := testhelpers.GetTestImage("ghcr.io/joryirving/maya:rolling")
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/maya/.venv/bin/python", "/opt/maya/serve/server.py", "--help")
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/maya/build/maya", "--help")
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/maya/.venv/bin/python", "-c", "assert open('/opt/maya/image/cuda-architectures.txt').read().strip() == '86'")
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/maya/.venv/bin/python", "-c", "flags = dict(line.strip().split('=', 1) for line in open('/opt/maya/image/cpu-flags.txt')); assert flags.get('MAYA_PORTABLE:BOOL') == 'ON' and flags.get('GGML_NATIVE:BOOL') == 'OFF' and flags.get('GGML_AVX2:BOOL') == 'ON'; assert all(value == 'OFF' for name, value in flags.items() if name.startswith(('GGML_AVX512', 'GGML_AVX_VNNI', 'GGML_AMX_')))")
	// The vision encoder stamp is the one upstream's setup accepts: src equals setup.py's own source_hash
	// over tools/vision as the image ships it (maya.py's vision_step gate), with the built CUDA architectures.
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/maya/.venv/bin/python", "-B", "-c", "import json,sys; sys.path.insert(0,'/opt/maya'); import setup; m=json.load(open('/opt/maya/build-vision/MAYA-BUILD.json')); assert m['src']==setup.source_hash(('tools/vision',)); assert m['archs']==[86] and m['backend']=='cuda' and m['llama']=='/opt/maya/third_party/llama.cpp'")
	// maya-vision links the CUDA driver (libcuda.so.1), which comes from the host and is absent in a GPU-less
	// CI container: the binary then exits 127 (library missing) instead of 2 (usage). Upstream's own image check
	// (docker/build.sh) allows exactly the driver's libraries to be missing and nothing else, so that is the rule
	// here; the usage path is only reachable where the driver resolves.
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "missing=$(ldd /opt/maya/build-vision/bin/maya-vision | grep 'not found' | grep -v -E 'libcuda\\.so|libnvidia' || true); test -z \"$missing\"")
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "if ldd /opt/maya/build-vision/bin/maya-vision | grep -q 'not found'; then exit 0; fi; /opt/maya/build-vision/bin/maya-vision 2>/tmp/maya-vision-usage.txt; [ $? -eq 2 ] && grep -q 'usage:' /tmp/maya-vision-usage.txt")
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/maya/.venv/bin/python", "-c", "assert open('/opt/maya/image/vision-cuda-architectures.txt').read().strip() == '86'")
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/maya/.venv/bin/python", "-c", "flags = dict(line.strip().split('=', 1) for line in open('/opt/maya/image/vision-cpu-flags.txt')); assert flags.get('MAYA_PORTABLE:BOOL') == 'ON' and flags.get('MAYA_VISION_CUDA:BOOL') == 'ON' and flags.get('GGML_NATIVE:BOOL') == 'OFF' and flags.get('GGML_AVX2:BOOL') == 'ON'; assert all(value == 'OFF' for name, value in flags.items() if name.startswith(('GGML_AVX512', 'GGML_AVX_VNNI', 'GGML_AMX_')))")
	// Upstream setup (maya.py) passes its gates on this image's artifacts. Step 3 (tools_step) is a no-op:
	// the venv's .strata-pip.json covers every PY_PACKAGES entry, and third_party/llama.cpp passes its
	// checkout check, so pip and the llama.cpp download are skipped.
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/maya/.venv/bin/python", "-B", "-c", "import json,sys; sys.path.insert(0,'/opt/maya'); import setup; have=json.load(open('/opt/maya/.venv/.strata-pip.json')); assert not [p for p in setup.PY_PACKAGES if p not in have]; assert (setup.ROOT/'third_party/llama.cpp/ggml/CMakeLists.txt').is_file() and (setup.ROOT/'third_party/llama.cpp/gguf-py').is_dir()")
	// Step 1's toolchain checks: nvcc where find_nvcc looks for it, g++ on PATH. No compile follows: the stamps
	// (steps 4/7, asserted below and above) keep setup from building.
	testhelpers.TestCommandSucceeds(t, image, nil, "/usr/local/cuda/bin/nvcc", "--version")
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "command -v g++ >/dev/null && g++ --version >/dev/null")
	// Step 4 (build_step) accepts the prebuilt engine: stamp src equals this tree's own ENGINE_SOURCES hash,
	// targets lists maya, archs cover sm_86 as ints, and the exe is where the gate looks.
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/maya/.venv/bin/python", "-B", "-c", "import json,sys; sys.path.insert(0,'/opt/maya'); import setup; m=json.load(open('/opt/maya/build/MAYA-BUILD.json')); assert m['src']==setup.source_hash(setup.ENGINE_SOURCES); assert 'maya' in m['targets'] and 86 in m['archs'] and (setup.ROOT/'build/maya').is_file()")
	// Step 8 writes config, .log and run-<config>.sh into ROOT: as the image user (65534) /opt/maya is writable
	// (create own + delete own), but the shipped code and engines are neither writable nor unlinkable (sticky).
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "touch /opt/maya/.maya-write-test && rm /opt/maya/.maya-write-test")
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/sh", "-c", "test ! -w /opt/maya/maya.py && test ! -w /opt/maya/build/maya && test ! -w /opt/maya/build-vision/bin/maya-vision && ! rm /opt/maya/maya.py")
}
