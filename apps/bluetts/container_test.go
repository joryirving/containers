package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	// Model load takes a while; give the health wait strategy ample time.
	c := testhelpers.TestHTTPEndpoint(t, "ghcr.io/joryirving/bluetts:rolling", testhelpers.HTTPTestConfig{
		Port:    "8000",
		Path:    "/health",
		Timeout: 300_000_000_000, // 300s
	}, nil)

	testhelpers.TestExecSucceeds(t, c, "curl", "-sf", "http://127.0.0.1:8000/v1/audio/voices")
}
