package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/mcp-arr:rolling")
	testhelpers.TestCommandSucceeds(t, ctx, image, nil, "node", "--version")
}
