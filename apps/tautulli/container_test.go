package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/tautulli:rolling")
	testhelpers.TestHTTPEndpoint(t, image, testhelpers.HTTPTestConfig{Port: "8181"}, nil)
}
