package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/dashclaw:rolling")

	// These files SHOULD exist in the final image
	testhelpers.TestFileExists(t, image, "/app/package.json", nil)
	testhelpers.TestFileExists(t, image, "/app/next.config.js", nil)
}
