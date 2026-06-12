package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/actions-runner:rolling")
	testhelpers.TestFileExists(t, image, "/usr/local/bin/yq", nil)
}
