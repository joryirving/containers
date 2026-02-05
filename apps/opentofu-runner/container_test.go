package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/opentofu-runner:rolling")
	testhelpers.TestFileExists(t, ctx, image, "/usr/local/bin/terraform", nil)
}
