package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/home-assistant:rolling")
	c := testhelpers.TestHTTPEndpoint(t, image, testhelpers.HTTPTestConfig{Port: "8123"}, nil)

	testhelpers.TestExecSucceeds(t, c, "go2rtc", "--version")

	// Custom integrations such as HACS rely on Home Assistant installing their requirements
	// into the venv at runtime, so check that path works for the container user.
	testhelpers.TestExecSucceeds(t, c, "/config/.venv/bin/python3", "-m", "uv", "pip", "install", "--quiet",
		"--python", "/config/.venv/bin/python3", "aiogithubapi")
	testhelpers.TestExecSucceeds(t, c, "/config/.venv/bin/python3", "-c", "import aiogithubapi")
}
