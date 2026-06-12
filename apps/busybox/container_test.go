package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/busybox:rolling")
	testhelpers.TestCommandSucceeds(t, image, nil, "/bin/busybox", "--list")
}
