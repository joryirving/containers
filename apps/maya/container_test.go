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
}
