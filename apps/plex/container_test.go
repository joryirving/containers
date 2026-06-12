package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/plex:rolling")
	testhelpers.TestHTTPEndpoint(t, image, testhelpers.HTTPTestConfig{
		Port: "32400",
		Path: "/web/index.html",
	}, nil)
}
