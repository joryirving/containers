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
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/maya/.venv/bin/python", "-c", "flags = dict(line.strip().split('=', 1) for line in open('/opt/maya/image/cpu-flags.txt')); assert flags.get('STRATA_PORTABLE:BOOL') == 'ON' and flags.get('GGML_NATIVE:BOOL') == 'OFF' and flags.get('GGML_AVX2:BOOL') == 'ON'; assert all(value == 'OFF' for name, value in flags.items() if name.startswith(('GGML_AVX512', 'GGML_AVX_VNNI', 'GGML_AMX_')))")
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
	testhelpers.TestCommandSucceeds(t, image, nil, "/opt/maya/.venv/bin/python", "-c", "flags = dict(line.strip().split('=', 1) for line in open('/opt/maya/image/vision-cpu-flags.txt')); assert flags.get('STRATA_PORTABLE:BOOL') == 'ON' and flags.get('GGML_NATIVE:BOOL') == 'OFF' and flags.get('GGML_AVX2:BOOL') == 'ON'; assert all(value == 'OFF' for name, value in flags.items() if name.startswith(('GGML_AVX512', 'GGML_AVX_VNNI', 'GGML_AMX_')))")
}
