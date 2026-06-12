package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/hoymiles-exporter:rolling")

	testhelpers.TestHTTPEndpoint(t, image, testhelpers.HTTPTestConfig{
		Port: "9099",
		Path: "/metrics",
	}, &testhelpers.ContainerConfig{
		Env: map[string]string{
			"DTU_HOST":                "127.0.0.1",
			"SCRAPE_INTERVAL_SECONDS": "5",
		},
	})
}
