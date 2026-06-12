package main

import (
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	image := testhelpers.GetTestImage("ghcr.io/joryirving/kopia:rolling")
	testhelpers.TestCommandSucceeds(t, image, nil, "/usr/local/bin/kopia", "--version")
}
