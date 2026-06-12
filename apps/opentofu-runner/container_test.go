package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/opentofu-runner:rolling")
	testhelpers.TestFileExists(t, image, "/usr/local/bin/terraform", nil)
}
