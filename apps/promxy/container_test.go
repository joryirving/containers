package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/promxy:rolling")
	testhelpers.TestCommandSucceeds(t, ctx, image, nil, "/bin/promxy", "--version")
}
