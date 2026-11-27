package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	// Model load takes a while; give the health wait strategy ample time.
	c := testhelpers.TestHTTPEndpoint(t, testhelpers.GetTestImage("ghcr.io/joryirving/bluetts:rolling"), testhelpers.HTTPTestConfig{
		Port:    "8000",
		Path:    "/health",
		Timeout: 300_000_000_000, // 300s
	}, nil)

	testhelpers.TestExecSucceeds(t, c, "curl", "-sf", "http://127.0.0.1:8000/v1/audio/voices")

	// /health passes before the G2P is touched; a real synthesis catches
	// missing-frontend failures (e.g. an absent polyg2p wheel) that only
	// surface on the first phonemization.
	testhelpers.TestExecSucceeds(t, c, "curl", "-sf",
		"http://127.0.0.1:8000/v1/audio/speech",
		"-H", "Content-Type: application/json",
		"-d", `{"model":"bluev3","input":"ok","voice":"mia","response_format":"wav"}`,
		"-o", "/tmp/speech.wav")
}

func TestNoGPULoaderPaths(t *testing.T) {
	testhelpers.TestCommandSucceeds(t, testhelpers.GetTestImage("ghcr.io/joryirving/bluetts:rolling"), nil, "/app/.venv/bin/python", "-c", `
import sys
sys.path.insert(0, "/app/src")
import onnxruntime as ort
from blue_onnx import load_onnx
try:
    load_onnx("/app/bluev3_onnx/onnx/duration_predictor_style.onnx", ort.SessionOptions(), ["WebGpuExecutionProvider"])
except (RuntimeError, ModuleNotFoundError) as err:
    assert "webgpu" in str(err).lower(), err
else:
    raise SystemExit("WebGPU unexpectedly succeeded without a GPU")
`)
}
