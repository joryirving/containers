package main

import (
	"context"
	"testing"

	"github.com/joryirving/containers/testhelpers"
)

func Test(t *testing.T) {
	ctx := context.Background()
	image := testhelpers.GetTestImage("ghcr.io/joryirving/strixhalo-llama-turboquant-vulkan-radv:rolling")
	testhelpers.TestFileExists(t, ctx, image, "/usr/bin/llama-server", nil)
}
