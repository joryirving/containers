package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/rocm-smi-exporter:rolling")

	testhelpers.TestHTTPEndpoint(t, image, testhelpers.HTTPTestConfig{
		Port: "9494",
		Path: "/metrics",
	}, nil)
}
